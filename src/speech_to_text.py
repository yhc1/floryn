import time
import io
import queue
import sys
from dataclasses import dataclass

import numpy as np
import sounddevice as sd
import soundfile as sf
from openai import OpenAI




@dataclass
class CostSummary:
    last_duration_sec = 0.0
    last_latency_sec = 0.0
    total_latency_sec = 0.0


class SpeechToText:
    def __init__(self, model="whisper-1", sample_rate=16000, channels=1):
        self.model = model
        self.sample_rate = sample_rate
        self.channels = channels
        self.client = OpenAI()
        self.cost = CostSummary()

    def record_until_enter(self):
        q = queue.Queue()
        frames = []

        def callback(indata, _frames, _time_info, status):
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        print("Press Enter to start recording...")
        input()
        print("🎙️ Recording... Press Enter to stop.")
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype="float32", callback=callback):
            input()
            print("⏹️ Recording stopped.")

        while not q.empty():
            frames.append(q.get())

        if not frames:
            return np.zeros((0, self.channels), dtype="float32")

        audio = np.concatenate(frames, axis=0)
        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        if peak > 0:
            audio = (audio / peak) * 0.98

        return audio

    def _to_wav_bytes(self, audio):
        if audio.ndim == 1:
            audio = audio.reshape(-1, self.channels)
        buf = io.BytesIO()
        sf.write(buf, audio, self.sample_rate, format="WAV", subtype="PCM_16")
        return buf.getvalue()

    def transcribe(self, audio, language=None):
        if audio.size == 0:
            self.cost.last_duration_sec = 0.0
            self.cost.last_latency_sec = 0.0
            return ""

        duration_sec = float(audio.shape[0]) / float(self.sample_rate)
        wav_bytes = self._to_wav_bytes(audio)
        bio = io.BytesIO(wav_bytes)
        bio.name = "audio.wav"

        kwargs = {"model": self.model, "file": bio}
        if language:
            if "-" in language:
                language = language.split("-")[0]
            kwargs["language"] = language

        start_time = time.time()
        resp = self.client.audio.transcriptions.create(**kwargs)
        latency = time.time() - start_time

        text = getattr(resp, "text", str(resp))

        self.cost.last_duration_sec = duration_sec
        self.cost.last_latency_sec = latency
        self.cost.total_latency_sec += latency
        return text

    def run_once(self, language=None):
        audio = self.record_until_enter()
        print("⏫ Uploading for transcription...")
        return self.transcribe(audio, language=language)

    def get_cost_summary(self):
        return self.cost


def main():
    tool = SpeechToText(model="whisper-1")

    try:
        text = tool.run_once(language="zh")
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)

    print("\n===== Transcription =====")
    print(text)
    print("=========================")

    summary = tool.get_cost_summary()
    print(f"🎧 Duration: {summary.last_duration_sec:.2f} seconds")
    print(f"⚡ Latency: {summary.last_latency_sec:.2f} seconds")
    print(f"📊 Total latency: {summary.total_latency_sec:.2f} seconds")
    print("📌 Actual cost depends on OpenAI token usage. Check https://platform.openai.com/usage")


if __name__ == "__main__":
    main()

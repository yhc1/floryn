from dotenv import load_dotenv

from src.speech_to_text import SpeechToText
from src.reminder import Reminder


def main():
    load_dotenv()

    s2t = SpeechToText(model="whisper-1")
    transcript = s2t.run_once(language="zh")
    print(f" Transcript : {transcript}")
    summary = s2t.get_cost_summary()
    print(f"⚡ Latency: {summary.last_latency_sec:.2f} seconds")

    reminder = Reminder()
    reminder.run(text=transcript)




if __name__ == '__main__':
    main()

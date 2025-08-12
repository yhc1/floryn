from dotenv import load_dotenv

from src.speech_to_text import SpeechToText
from src.reminder import Reminder


def main():
    load_dotenv()

    # s2t = SpeechToText(model="whisper-1")
    # transcript = s2t.run_once(language="zh")
    # print(f" Transcript : {transcript}")
    # summary = s2t.get_cost_summary()
    # print(f"⚡ Latency: {summary.last_latency_sec:.2f} seconds")

    transcript = "我今天不知道要幹嘛欸，晚點整理東西好了。明天早上我想要開始規劃行程拉"
    reminder = Reminder()
    reminder.run(text=transcript)




if __name__ == '__main__':
    main()

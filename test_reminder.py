#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from src.reminder import Reminder

# Load environment variables
load_dotenv()

# Test the reminder
reminder = Reminder()
result = reminder.run("我今天不知道要幹嘛欸，晚點整理東西好了")
print(f"Description: {result.description}")
print(f"Date/Time: {result.date_time}")
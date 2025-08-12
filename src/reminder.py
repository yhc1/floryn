import os
import json
from datetime import datetime

import google.generativeai as genai
from pydantic import BaseModel

from prompt_renderer import PromptRenderer


class TodoItem(BaseModel):
    description: str
    time: str

class Response(BaseModel):
    todo_list: list[TodoItem]


class Reminder:
    def __init__(self):
        # Configure Google AI with API key from environment
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_name = "gemini-2.5-flash"
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
                "response_mime_type": "application/json",
            }
        )
        self.prompt_renderer = PromptRenderer(strict=True, debug=False)

    def _get_structured_completion(self, prompt: str) -> Response:
        """Get structured completion from Google Gemini API"""
        response = self.model.generate_content(prompt)
        
        import json
        parsed = json.loads(response.text)
        return Response(**parsed)

    def _save(self, todo_list: list[TodoItem]):
        """Save the reminder to a persistent storage (e.g., database or file)"""
        with open("reminder.jsonl", "a") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for item in todo_list:
                created_at = now
                description = item.description
                setting_time = item.time
                f.write(json.dumps({
                    "created_at": created_at,
                    "description": description,
                    "setting_time": setting_time
                }, ensure_ascii=False) + "\n")

    def run(self, text: str):
        system_prompt = self.prompt_renderer.render("reminder")
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %I:%M %p %A")
        
        # Combine system prompt and user message for Gemini
        full_prompt = f"""{system_prompt}
        **口語描述**：
        {text}
        **當前情境 (Context)**：
        當前時間是 {formatted_time}"""
        response = self._get_structured_completion(full_prompt)
        for item in response.todo_list:
            print(f"待辦事項: {item.description}，時間: {item.time}")
        self._save(response.todo_list)

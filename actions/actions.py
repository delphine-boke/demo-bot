import json
import os
import urllib.request
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

SYSTEM = """You are the fallback for a Kenya registry assistant.
Scope: office hours, bursary forms, application status, documents.
If the question is outside that scope, say so in one sentence.
Do not invent fees, deadlines, or reference numbers.
Reply in the requested language. If the language is guz, reply in Swahili
and add that an Ekegusii answer needs a speaker-approved template.
"""

from pathlib import Path

def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))

_load_dotenv()

class ActionLlmFallback(Action):
    def name(self) -> Text:
        return "action_llm_fallback"

    def run(self, dispatcher, tracker, domain):
        language = tracker.get_slot("language") or "en"
        text = tracker.latest_message.get("text") or ""
        dispatcher.utter_message(text=self._complete(text, language))
        return []

    def _complete(self, text, language):
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            return "Fallback is not configured. Set OPENAI_API_KEY and restart the action server."
        body = json.dumps({
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"language={language}\nuser={text}"},
            ],
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode())
        return payload["choices"][0]["message"]["content"].strip()
    
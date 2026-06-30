import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
URL = "https://openrouter.ai/api/v1/chat/completions"

_last = 0
DELAY = 3


def rate_limit():
    global _last
    now = time.time()

    if now - _last < DELAY:
        time.sleep(DELAY)

    _last = time.time()


def safe_json(text):
    try:
        if not text:
            return {}
        text = text.replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return {}


def call_llm(prompt: str):

    if not API_KEY:
        return ""

    rate_limit()

    try:
        r = requests.post(
            URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "openai/gpt-oss-120b:free",
                "messages": [
                    {"role": "system", "content": "Return ONLY JSON. Never invent data."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            },
            timeout=90
        )

        if r.status_code == 429:
            time.sleep(5)
            return ""

        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print("[LLM ERROR]", e)
        return ""
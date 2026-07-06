import time
import random
import requests
import json
import re
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL


def call_openrouter(prompt, retries=5):

    if not OPENROUTER_API_KEY:
        print("❌ Missing OPENROUTER_API_KEY")
        return None

    for attempt in range(retries):

        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost",
                    "X-Title": "wamda-scraper"
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 1500
                },
                timeout=60
            )

            data = r.json()

            if "choices" in data:
                return data["choices"][0]["message"]["content"]

            print("❌ OpenRouter error:", data)

        except Exception as e:
            print(f"OpenRouter exception attempt {attempt}:", e)

        # 🔥 BACKOFF intelligent
        sleep_time = (2 ** attempt) + random.uniform(0.5, 2)
        print(f"⏳ retrying in {sleep_time:.1f}s...")
        time.sleep(sleep_time)

    return None


def safe_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        return json.loads(match.group(0))
    except:
        return None
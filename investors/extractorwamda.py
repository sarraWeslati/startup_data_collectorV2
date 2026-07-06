import time
import random
import json
import re
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL


# =========================
# 🔥 OPENROUTER CALL (robuste)
# =========================
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
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1800
                },
                timeout=60
            )

            data = r.json()

            if "choices" in data:
                return data["choices"][0]["message"]["content"]

            print("❌ OpenRouter error:", data)

        except Exception as e:
            print(f"⚠️ attempt {attempt} error:", e)

        # backoff intelligent
        sleep_time = (2 ** attempt) + random.uniform(0.5, 1.5)
        time.sleep(sleep_time)

    return None


# =========================
# 🧠 SAFE JSON PARSER
# =========================
def safe_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        return json.loads(match.group(0))
    except:
        return None


# =========================
# 🧠 PROMPT (TRÈS IMPORTANT)
# =========================
def build_prompt(text):

    return f"""
You are an expert extraction system.

Extract structured data ONLY from the article.

RETURN STRICT JSON ONLY (no markdown).

FORMAT:

{{
  "news": [
    {{
      "title": "",
      "date": "",
      "summary": "",
      "startups": [],
      "investors": []
    }}
  ],
  "startups": [
    {{
      "name": "",
      "description": ""
    }}
  ],
  "investors": [
    {{
      "name": "",
      "type": ""
    }}
  ]
}}

RULES:
- Extract ALL startups mentioned (do not miss any)
- Extract ALL investors mentioned
- Do NOT hallucinate
- If none → empty array []
- Keep names EXACT from text
- No duplicates inside response

TEXT:
{text[:6000]}
"""


# =========================
# 🚀 MAIN EXTRACTOR
# =========================
def extract_wamda(text):

    if not text:
        return None

    prompt = build_prompt(text)
    raw = call_openrouter(prompt)

    if not raw:
        return None

    print("\n🔵 RAW LLM:\n", raw[:400])

    return safe_json(raw)
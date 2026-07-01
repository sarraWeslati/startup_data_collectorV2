import json
import re
import requests
from config import GROQ_API_KEY

MODEL = "openai/gpt-oss-20b"

def build_prompt(text):
    return f"""
You are a data extractor.

Extract ALL investors from Tunisia page.

RULES:
- Only investors (VC, Angel, Fund, PE)
- No other countries
- No duplicates
- Return STRICT JSON ONLY

Format:
{{
  "investors": [
    {{
      "name": "string",
      "type": "VC|Angel|Fund|PE",
      "country": "Tunisia",
      "website": "",
      "description": ""
    }}
  ]
}}

TEXT:
{text[:6000]}
"""


def safe_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        return json.loads(match.group(0))
    except:
        return None


def call_groq(prompt):
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 800
            },
            timeout=30
        )

        data = r.json()

        if r.status_code != 200:
            print("❌ GROQ ERROR:", data)
            return None

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("GROQ exception:", e)
        return None


def extract_investors(text, existing=None):

    if not text:
        return {"investors": []}

    prompt = build_prompt(text)
    raw = call_groq(prompt)

    print("\n🔵 GROQ RAW:\n", raw[:300] if raw else "EMPTY")

    data = safe_json(raw or "")

    if not data:
        print("⚠️ JSON FAILED")
        return {"investors": []}

    investors = data.get("investors", [])

    cleaned = []

    for inv in investors:
        name = inv.get("name", "").lower().strip()

        if not name:
            continue

        if existing and name in existing:
            continue

        # 🔥 FORCE TUNISIA ONLY
        inv["country"] = "Tunisia"

        cleaned.append(inv)

    print(f"🧠 extracted={len(investors)} | cleaned={len(cleaned)}")

    return {"investors": cleaned}
import os
import json
import time
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini")
BASE_URL = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")


def extract_with_llm(url: str, text: str, max_retries: int = 1):

    if not text:
        return None

    # 🔥 reduce cost
    text = text[:2500]

    prompt = f"""
Extract structured data from this article.

Return ONLY JSON:

{{
  "summary": "short summary",
  "type": "funding|news|regulation|interview|other",
  "startups": [],
  "companies": [],
  "banks": [],
  "people": []
}}

ARTICLE:
{text}
"""

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 300   # 🔥 IMPORTANT COST CONTROL
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for _ in range(max_retries + 1):

        try:
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            data = response.json()

            # ❌ API error handling
            if "choices" not in data:

                print("\n❌ LLM ERROR:", data)

                # stop wasting time on quota errors
                if data.get("error", {}).get("code") in [401, 402]:
                    return {
                        "summary": "",
                        "type": "error",
                        "startups": [],
                        "companies": [],
                        "banks": [],
                        "people": []
                    }

                return None

            content = data["choices"][0]["message"]["content"]

            try:
                return json.loads(content)

            except:
                return {
                    "summary": content[:200],
                    "type": "unknown",
                    "startups": [],
                    "companies": [],
                    "banks": [],
                    "people": []
                }

        except Exception as e:
            print("❌ Request error:", e)
            return None
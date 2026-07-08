import json
import re

import requests

from config import LLM_TIMEOUT, NVIDIA_API_KEY

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "nvidia/nemotron-3-ultra-550b-a55b"

HEADERS = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Content-Type": "application/json"
}


def extract_json(text):
    try:
        text = text.replace("```json", "").replace("```", "")
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            print("[LLM ERROR] No JSON object found in response")
            return None
        return json.loads(match.group(0))
    except Exception as e:
        print("[LLM ERROR] Invalid JSON response:", e)
        return None


def call_llm(payload, url=""):
    try:
        res = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=(10, LLM_TIMEOUT)
        )

        if res.status_code != 200:
            print(f"[LLM HTTP {res.status_code}] {url}")
            return None

        data = res.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"[LLM REQUEST ERROR] {url} {e}")
        return None


def safe_extract(text, url):

    prompt = f"""
Extract structured news from Africa & Tunisia startup ecosystem.

RETURN ONLY JSON:

{{
  "title": "",
  "summary": "",
  "content": "",
  "country": "",
  "category": "startup|funding|investor|banking|report|news|event",
  "entities": {{
    "startups": [],
    "investors": [],
    "funds": []
  }},
  "source": "{url}",
  "date": ""
}}

RULES:
- clean content
- no duplicates
- country must be Africa / Tunisia / MENA / Unknown
- entities = ONLY names

TEXT:
{text[:5000]}
"""

    response = call_llm({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 1800
    }, url=url)

    if not response:
        return None

    return extract_json(response)

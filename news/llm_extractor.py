import requests
import json
import re
from config import NVIDIA_API_KEY

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
            return None
        return json.loads(match.group(0))
    except:
        return None


def call_llm(payload):
    try:
        res = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=(10, 180)
        )

        if res.status_code != 200:
            return None

        data = res.json()
        return data["choices"][0]["message"]["content"]

    except:
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
    })

    if not response:
        return None

    return extract_json(response)
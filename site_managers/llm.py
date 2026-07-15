import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv(
    "NVIDIA_API_KEY"
)


if not NVIDIA_API_KEY:

    raise Exception(
        "❌ NVIDIA_API_KEY introuvable dans .env"
    )


print(
    "✅ NVIDIA KEY:",
    NVIDIA_API_KEY[:15] + "********"
)



NVIDIA_URL = (

    "https://integrate.api.nvidia.com/v1/chat/completions"

)


NVIDIA_MODEL = (

    "meta/llama-3.1-8b-instruct"

)


SYSTEM_PROMPT = """
You are a high-precision startup ecosystem extraction system.

TASK:
1. Classify article into ONLY ONE:
   - startup
   - investor
   - other

=================================================
CLASSIFICATION RULES
=================================================

STARTUP:
- company, startup, product, app
- founded, launched
- funding, seed, series A, B, C
- raising money

INVESTOR:
- VC, venture capital
- fund, investor, accelerator, incubator
- investment activity

OTHER:
- ecosystem news
- stats
- trends
- events (no specific company/investor)

IMPORTANT:
If funding is mentioned AND a company exists → startup

=================================================
COUNTRY RULE
=================================================
Always try to identify the country of the entity (startup or investor)
from the article. Use the country actually stated or clearly implied in
the text (e.g. "startup tunisienne" → "Tunisia", "fonds égyptien" →
"Egypt"). If truly not determinable, leave it as an empty string.

=================================================
OUTPUT (STRICT JSON ONLY)
=================================================

{
  "entity_type": "startup | investor | other",
  "data": {}
}

=================================================
STARTUP FIELDS
=================================================
If startup:
{
  "name": "",
  "industry": "",
  "country": "",
  "city": "",
  "website": "",
  "founders": [],
  "funding": {},
  "investors": [],
  "tags": [],
  "others": {}
}

=================================================
INVESTOR FIELDS
=================================================
If investor:
{
  "name": "",
  "investor_type": "",
  "country": "",
  "website": "",
  "focus": [],
  "portfolio": [],
  "others": {}
}

=================================================
OTHER FIELDS
=================================================
If other:
{
  "title": "",
  "summary": "",
  "tags": [],
  "relevance": "low | medium | high",
  "others": {}
}

RULES:
- Never invent data
- Unknown = empty value
- Return ONLY JSON
"""


def safe_json(raw):
    try:
        raw = raw.strip()

        if raw.startswith("```json"):
            raw = raw.replace("```json", "").replace("```", "").strip()
        elif raw.startswith("```"):
            raw = raw.replace("```", "").strip()

        return json.loads(raw)

    except Exception as e:
        print("JSON ERROR:", e)
        return {
            "entity_type": "other",
            "data": {}
        }


def llm_extract(url, title, text):

    text = text[:3000]

    prompt = f"""
URL: {url}
TITLE: {title}

ARTICLE:
{text}

Extract structured data.
"""

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": 1024,
    }

    try:
        response = requests.post(
            NVIDIA_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        raw = response.json()["choices"][0]["message"]["content"]
        return safe_json(raw)

    except Exception as e:
        print("LLM ERROR:", e)
        return {
            "entity_type": "other",
            "data": {}
        }
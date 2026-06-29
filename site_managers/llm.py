from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
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

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        raw = response.choices[0].message.content
        return safe_json(raw)

    except Exception as e:
        print("LLM ERROR:", e)
        return {
            "entity_type": "other",
            "data": {}
        }
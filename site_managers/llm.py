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
You are a strict startup data extraction engine.

Return ONLY valid JSON.

RULES:

1. startup_name:
- must be a REAL startup/company
- reject: programs, events, articles, generic words
- if not real → return null

2. funding:
- always return numeric values (NOT strings)
- include:
  amount (float)
  currency
  type (equity/debt/grant/unknown)
  meaning (short explanation of what the money represents)

3. summary:
- 2-3 lines max
- MUST explain meaning of funding (not just numbers)

4. entities:
- only real companies, investors, organizations, countries

OUTPUT FORMAT:
{
  "startup_name": "",
  "year": "",
  "funding": [],
  "entities": [],
  "summary": ""
}
"""


# =========================
# SAFE JSON PARSER
# =========================
def safe_parse_json(text: str):
    try:
        data = json.loads(text)

        # 🔥 Fix: sometimes LLM returns list instead of dict
        if isinstance(data, list):
            return data[0] if len(data) > 0 else {}

        if isinstance(data, dict):
            return data

        return {}

    except Exception:
        return {}


# =========================
# LLM CALL WITH RETRY
# =========================
def llm_extract(url: str, title: str, text: str):

    text = text[:2500]

    prompt = f"""
URL: {url}
TITLE: {title}

CONTENT:
{text}

Extract structured startup intelligence in strict JSON.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        raw = response.choices[0].message.content

        # 🔥 DEBUG (utile en dev)
        # print("RAW LLM:", raw)

        return safe_parse_json(raw)

    except Exception as e:
        print("❌ LLM ERROR:", e)
        return {}
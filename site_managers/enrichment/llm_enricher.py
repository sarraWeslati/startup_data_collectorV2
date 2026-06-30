import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# =========================
# RATE LIMIT (ANTI 429)
# =========================
_last_call = 0
MIN_DELAY = 3


def rate_limit():
    global _last_call
    now = time.time()

    if now - _last_call < MIN_DELAY:
        time.sleep(MIN_DELAY)

    _last_call = time.time()


# =========================
# SAFE JSON PARSER
# =========================
def safe_json(text: str):

    try:
        if not text:
            return {}

        text = text.strip()
        text = text.replace("```json", "").replace("```", "")

        data = json.loads(text)

        # parfois LLM retourne list
        if isinstance(data, list):
            return data[0] if data else {}

        return data

    except Exception as e:
        print("[LLM PARSE ERROR]", e)
        return {}


# =========================
# CORE LLM CALL
# =========================
def call_llm(prompt: str, model: str = "openai/gpt-oss-120b:free"):

    if not OPENROUTER_API_KEY:
        return ""

    rate_limit()

    try:
        response = requests.post(
            BASE_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a strict data extraction engine. "
                            "You MUST NOT invent information. "
                            "Return ONLY valid JSON."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1
            },
            timeout=90
        )

        # anti rate limit
        if response.status_code == 429:
            print("[LLM WARNING] rate limit hit")
            time.sleep(5)
            return ""

        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print("[LLM ERROR]", e)
        return ""


# =========================
# SMART MERGE (IMPORTANT)
# =========================
def merge_non_empty(target: dict, source: dict):

    if not isinstance(source, dict):
        return target

    for k, v in source.items():

        # ignore empty values
        if v in ("", [], {}, None):
            continue

        # don't overwrite existing data
        if target.get(k) not in ("", [], {}, None):
            continue

        target[k] = v

    return target


# =========================
# STARTUP ENRICHMENT PROMPT
# =========================
def enrich_startup_with_llm(startup: dict, serper_data: dict, website_content: str):

    prompt = f"""
You are a startup intelligence system.

TASK:
Extract structured startup data ONLY from provided information.

RULES:
- NEVER invent data
- If unknown → leave empty
- Do NOT overwrite existing fields
- Keep answers factual
- Put extra info in "others"

OUTPUT FORMAT:
Return ONLY valid JSON.

====================
STARTUP DATA
====================
{json.dumps(startup, indent=2)}

====================
SEARCH DATA (SERPER)
====================
{json.dumps(serper_data, indent=2)}

====================
WEBSITE CONTENT
====================
{website_content[:7000]}
"""

    raw = call_llm(prompt)
    data = safe_json(raw)

    return merge_non_empty(startup, data)


# =========================
# INVESTOR ENRICHMENT PROMPT
# =========================
def enrich_investor_with_llm(investor: dict, serper_data: dict, website_content: str):

    prompt = f"""
You are a venture capital intelligence system.

TASK:
Extract structured VC/investor data ONLY from provided information.

RULES:
- NEVER invent funds or portfolio companies
- If unknown → empty
- Do NOT overwrite existing values
- Be strict and factual

OUTPUT:
Return ONLY valid JSON.

====================
INVESTOR DATA
====================
{json.dumps(investor, indent=2)}

====================
SEARCH DATA
====================
{json.dumps(serper_data, indent=2)}

====================
WEBSITE CONTENT
====================
{website_content[:7000]}
"""

    raw = call_llm(prompt)
    data = safe_json(raw)

    return merge_non_empty(investor, data)
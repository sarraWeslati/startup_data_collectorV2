# extractors/startup_extractor.py

import json
from typing import Dict, Any

from llm.openrouter_client import call_llm

from utils.url_normalizer import (
    normalize_website
)

def build_startup_prompt(content: str) -> str:

    content = content[:20000]

    return f"""
You are a startup intelligence analyst.

Extract all startup information available in the content.

Return ONLY valid JSON.

Schema:

{{
    "entity_type": "startup",
    "name": "",
    "description": "",
    "industry": "",
    "country": "",
    "city": "",
    "website": "",
    "linkedin": "",
    "founders": [],
    "team_members": [],
    "products": [],
    "technologies": [],
    "emails": [],
    "phones": []
}}

Rules:

- Use empty string if unknown.
- Use empty array if unknown.
- Do not invent information.
- Return ONLY JSON.

CONTENT:

{content}
"""


def parse_startup_response(response: str) -> Dict[str, Any]:

    try:

        response = response.strip()

        response = response.replace("```json", "")
        response = response.replace("```", "")

        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("JSON not found")

        json_text = response[start:end + 1]

        return json.loads(json_text)

    except Exception as e:

        return {
            "entity_type": "startup",
            "error": str(e)
        }


def extract_startup(content: str) -> Dict[str, Any]:

    prompt = build_startup_prompt(content)

    response = call_llm(
        prompt=prompt,
        max_tokens=2500
    )

    startup = parse_startup_response(response)
    website = startup.get("website", "")
    startup["website"] = normalize_website(website)
    return startup
# extractors/support_organization_extractor.py

import json
from typing import Dict, Any

from llm.openrouter_client import call_llm_json


def build_prompt(content: str) -> str:
    """
    Construit le prompt d'extraction.
    """

    content = content[:15000]

    return f"""
You are an expert startup ecosystem analyst.

Extract information about the support organization.

Return ONLY valid JSON.

Schema:

{{
    "entity_type": "support_organization",
    "name": "",
    "description": "",
    "website": "",
    "linkedin": "",
    "country": "",
    "city": "",
    "services": [],
    "programs": [],
    "contacts": []
}}

Rules:

- Return ONLY JSON.
- Do not invent information.
- Empty string if unknown.
- Empty array if unknown.

CONTENT:

{content}
"""


def parse_response(response: str) -> Dict[str, Any]:
    """
    Parse la réponse JSON.
    """

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
            "entity_type": "support_organization",
            "name": "",
            "description": "",
            "website": "",
            "linkedin": "",
            "country": "",
            "city": "",
            "services": [],
            "programs": [],
            "contacts": [],
            "error": str(e)
        }


def extract_support_organization(
    content: str
) -> Dict[str, Any]:
    """
    Extraction principale.
    """

    prompt = build_prompt(content)

    response = call_llm_json(
        prompt=prompt,
        max_tokens=1500
    )

    return parse_response(response)


if __name__ == "__main__":

    sample_text = """
    The Dot is a startup support organization.
    It helps entrepreneurs through programs,
    networking and ecosystem development.
    """

    result = extract_support_organization(
        sample_text
    )

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )
# extractors/incubator_extractor.py

import json
from typing import Dict, Any

from llm.openrouter_client import call_llm_json


def build_prompt(content: str) -> str:
    """
    Construit le prompt pour extraire les données
    d'un incubateur.
    """

    content = content[:12000]

    return f"""
You are an expert startup ecosystem analyst.

Extract information about the incubator.

Return ONLY valid JSON.

Schema:

{{
    "entity_type": "incubator",
    "name": "",
    "description": "",
    "website": "",
    "linkedin": "",
    "country": "",
    "city": "",
    "programs": [],
    "services": [],
    "partners": [],
    "contacts": []
}}

Rules:

- Return ONLY valid JSON.
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

        response = response.replace(
            "```json",
            ""
        )

        response = response.replace(
            "```",
            ""
        )

        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                "JSON not found"
            )

        json_text = response[
            start:end + 1
        ]

        return json.loads(
            json_text
        )

    except Exception as e:

        return {
            "entity_type": "incubator",
            "name": "",
            "description": "",
            "website": "",
            "linkedin": "",
            "country": "",
            "city": "",
            "programs": [],
            "services": [],
            "partners": [],
            "contacts": [],
            "error": str(e)
        }


def extract_incubator(
    content: str
) -> Dict[str, Any]:
    """
    Extraction principale.
    """

    prompt = build_prompt(
        content
    )

    response = call_llm_json(
        prompt=prompt,
        max_tokens=1500
    )

    return parse_response(
        response
    )


if __name__ == "__main__":

    sample_content = """
    Flat6Labs Tunisia is a startup incubator.
    It supports entrepreneurs through mentoring,
    funding and incubation programs.
    """

    result = extract_incubator(
        sample_content
    )

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )
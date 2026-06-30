# extractors/entity_detector.py

import json
from typing import Dict, Any

from llm.openrouter_client import call_llm_json


ALLOWED_ENTITY_TYPES = {
    "startup",
    "investor",
    "venture_capital_fund",
    "incubator",
    "accelerator",
    "support_organization",
    "startup_directory",
    "investor_directory",
    "government_program",
    "other"
}


def build_detection_prompt(content: str) -> str:
    """
    Construit le prompt envoyé au LLM.
    """

    truncated_content = content[:15000]

    return f"""
You are an expert in startup ecosystem analysis.

Your task is to identify the primary entity type represented by the content below.

Allowed entity types:

- startup
- investor
- venture_capital_fund
- incubator
- accelerator
- support_organization
- startup_directory
- investor_directory
- government_program
- other

Return ONLY valid JSON.

Example:

{{
    "entity_type": "startup",
    "confidence": 0.95,
    "reason": "The page describes a startup, its product and founders."
}}

CONTENT:

{truncated_content}
"""


def parse_detection_response(response: str) -> Dict[str, Any]:
    """
    Parse la réponse du LLM.
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

        result = json.loads(json_text)

        entity_type = result.get(
            "entity_type",
            "other"
        )

        if entity_type not in ALLOWED_ENTITY_TYPES:
            entity_type = "other"

        return {
            "entity_type": entity_type,
            "confidence": result.get("confidence", 0),
            "reason": result.get("reason", "")
        }

    except Exception as e:

        return {
            "entity_type": "other",
            "confidence": 0,
            "reason": f"Parsing error: {e}"
        }


def detect_entity_type(content: str) -> Dict[str, Any]:
    """
    Détecte le type d'entité.
    """

    prompt = build_detection_prompt(content)

    response = call_llm_json(prompt)

    return parse_detection_response(response)
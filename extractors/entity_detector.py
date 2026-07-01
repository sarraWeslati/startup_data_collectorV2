# extractors/entity_detector.py

import json
from typing import Dict, Any

from llm.openrouter_client import call_llm_json


ALLOWED_ENTITY_TYPES = {
    "startup",
    "startup_directory",

    "investor",
    "venture_capital_fund",
    "investor_directory",

    "incubator",
    "incubator_directory",

    "accelerator",
    "accelerator_directory",

    "support_organization",
    "support_organization_directory",

    "government_program",

    "other"
}


def build_detection_prompt(
    content: str
) -> str:
    """
    Construit le prompt envoyé au LLM.
    """

    truncated_content = content[:15000]

    return f"""
You are an expert in startup ecosystem intelligence.

Your task is to identify the SINGLE primary entity represented by the document.

Return ONLY valid JSON.

Allowed entity types:

- startup
- startup_directory
- investor
- venture_capital_fund
- investor_directory
- incubator
- accelerator
- support_organization
- government_program
- other

Definitions:

startup
- A company building products or services.
- Usually contains founders, products, customers,
website, contact information.

startup_directory
- A page listing multiple startups.
- Examples:
    - Startup directory
    - Startup catalog
    - Startup list
    - Startup ranking

investor
- A single investor.
- Examples:
    - Angel Investor
    - Venture Capital Firm
    - Investment Company

venture_capital_fund
- A single Venture Capital fund.
- Usually contains:
    - portfolio
    - investment focus
    - investment stages
    - partners

investor_directory
- A page listing multiple investors.
- Examples:
    - VC directory
    - Top Investors
    - Investors List
    - Venture Capital Directory

incubator
- One incubator.

accelerator
- One accelerator.

support_organization
- One ecosystem support organization.

government_program
- Government initiative,
public funding program,
innovation agency,
public startup support.

other
- None of the above.

Important rules:

- Choose ONLY one entity type.
- If the page mainly describes one company,
choose the company type.

Examples:

216capital.vc
→ venture_capital_fund

Flat6Labs Tunisia
→ accelerator

Top VC Funds in Africa
→ investor_directory

Top 100 Startups Tunisia
→ startup_directory

The Dot
→ support_organization

Return ONLY JSON.

Example:

{{
    "entity_type":"startup",
    "confidence":0.98,
    "reason":"The page describes one startup."
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
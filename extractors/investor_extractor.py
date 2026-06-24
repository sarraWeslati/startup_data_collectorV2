# extractors/investor_extractor.py

import json
from typing import Dict, Any

from llm.openrouter_client import call_llm
from utils.url_normalizer import (
    normalize_website
)


def build_investor_prompt(content: str) -> str:

    content = content[:20000]

    return f"""
You are an investor intelligence analyst.

Extract all information about the investor organization.

Return ONLY valid JSON.

Schema:

{{
    "entity_type": "investor",
    "name": "",
    "description": "",
    "country": "",
    "city": "",
    "website": "",
    "linkedin": "",
    "investment_focus": [],
    "ticket_size": "",
    "portfolio_companies": [],
    "partners": [],
    "team_members": [],
    "emails": [],
    "phones": []
}}

Rules:

- Do not invent information.
- Use empty strings if unknown.
- Use empty arrays if unknown.
- Return ONLY JSON.

CONTENT:

{content}
"""


def parse_investor_response(
    response: str
) -> Dict[str, Any]:

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

            "entity_type":
            "investor",

            "error":
            str(e)
        }


def extract_investor(
    content: str
) -> Dict[str, Any]:

    prompt = build_investor_prompt(
        content
    )

    response = call_llm(
        prompt=prompt,
        max_tokens=2500
    )

    investor = (
        parse_investor_response(
            response
        )
    )

    # --------------------------
    # Website normalization
    # --------------------------

    website = investor.get(
        "website",
        ""
    )

    investor[
        "website"
    ] = normalize_website(
        website
    )

    return investor
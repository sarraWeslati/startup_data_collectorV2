# extractors/investor_extractor.py

from typing import Dict

from llm.openrouter_client import call_llm_json
from schemas.investor_schema import get_empty_investor
from utils.json_tools import parse_llm_json
from utils.url_normalizer import normalize_website


def build_investor_prompt(content: str) -> str:

    content = content[:20000]

    schema = get_empty_investor()

    return f"""
You are a venture capital and investor intelligence analyst.

Extract every piece of information that is explicitly present in the content.

Do NOT invent information.

If a field is missing, keep the default value.

Return ONLY valid JSON.

JSON Schema:

{schema}

Rules:

- Return ONLY JSON.
- Do not add explanations.
- Do not use markdown.
- Do not invent information.
- Preserve the JSON structure exactly.
- Keep empty strings, empty arrays, empty objects and null values if information is missing.

CONTENT:

{content}
"""


def extract_investor(
    content: str
) -> Dict:

    prompt = build_investor_prompt(content)

    response = call_llm_json(
        prompt=prompt,
        max_tokens=3500
    )

    investor = parse_llm_json(response)

    if not investor:

        investor = get_empty_investor()

    # =====================================================
    # Website normalization
    # =====================================================

    investor["website"] = normalize_website(
        investor.get("website", "")
    )


    # =====================================================
    # Contact normalization
    # =====================================================

    investor.setdefault(
        "emails",
        []
    )

    investor.setdefault(
        "phones",
        []
    )

    investor.setdefault(
        "address",
        ""
    )

    return investor
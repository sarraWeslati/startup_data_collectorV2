# extractors/startup_extractor.py

from typing import Dict

from llm.openrouter_client import call_llm_json

from schemas.startup_schema import (get_empty_startup)

from utils.json_tools import (parse_llm_json)

from utils.url_normalizer import (normalize_website)

# =====================================================
# PROMPT
# =====================================================

def build_startup_prompt(
    content: str
) -> str:

    content = content[:20000]

    return f"""
You are an expert startup intelligence analyst.

Extract ONLY information explicitly present in the text.

Do NOT invent information.

Return ONLY valid JSON.

Return ONLY the fields below.

Schema:

{{
    "name": "",
    "description": "",
    "tagline": "",

    "industry": "",
    "sub_industry": "",
    "keywords": [],

    "country": "",
    "city": "",
    "headquarters": "",

    "founded_year": "",
    "startup_stage": "",

    "website": "",
    "linkedin_url": "",

    "contact": {{
        "emails": [],
        "phones": [],
        "address": ""
    }},

    "founders": [],

    "leadership": [],

    "products": [],

    "services": [],

    "technologies": [],

    "customer_segments": [],

    "target_market": "",

    "partners": [],

    "accelerators": [],

    "incubators": [],

    "investors": [],

    "awards": [],

    "certifications": [],

    "patents": []
}}

Rules:

- Return ONLY JSON.
- Empty string if unknown.
- Empty array if unknown.
- Never guess.

CONTENT:

{content}
"""

# =====================================================
# MERGE
# =====================================================

def merge_startup_data(
    startup: Dict,
    extracted: Dict
) -> Dict:

    for key, value in extracted.items():

        if value in (
            "",
            None,
            [],
            {}
        ):
            continue

        if key == "website":

            startup["website"] = normalize_website(
                value
            )

            continue

        existing = startup.get(key)

        if isinstance(value, dict) and isinstance(existing, dict):

            existing.update(value)

            startup[key] = existing

        elif isinstance(value, list) and isinstance(existing, list):

            merged = existing.copy()

            for item in value:

                if item not in merged:

                    merged.append(item)

            startup[key] = merged

        else:

            startup[key] = value

    return startup

# =====================================================
# MAIN
# =====================================================

def extract_startup(
    content: str
) -> Dict:

    startup = get_empty_startup()

    prompt = build_startup_prompt(
        content
    )

    response = call_llm_json(
        prompt=prompt,
        max_tokens=3000
    )

    extracted = parse_llm_json(
        response
    )

    if not extracted:

        startup["extraction_error"] = (
            "Unable to parse LLM response."
        )

        return startup

    startup = merge_startup_data(
        startup,
        extracted
    )

    startup["entity_type"] = "startup"

    return startup
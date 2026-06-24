# enrichment/website_enricher.py

import re
from typing import Dict

from collectors.website_collector import scrape_url
from llm.openrouter_client import call_llm
from utils.json_tools import parse_llm_json


# =====================================================
# REGEX HELPERS
# =====================================================

def extract_emails(
    content: str
):

    emails = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        content
    )

    return list(
        set(emails)
    )


def extract_phone_numbers(
    content: str
):

    phones = re.findall(
        r"\+?\d[\d\s\-\(\)]{7,20}",
        content
    )

    return list(
        set(phones)
    )


# =====================================================
# PROMPT
# =====================================================

def build_prompt(
    content: str
) -> str:

    content = content[:12000]

    return f"""
You are a startup and investor intelligence analyst.

Extract as much information as possible.

Do NOT invent information.

Return ONLY valid JSON.

Schema:

{{
    "description": "",

    "founders": [],
    "team_members": [],

    "technologies": [],

    "products": [],
    "services": [],

    "industry": "",
    "sub_industry": "",

    "country": "",
    "city": "",

    "founded_year": "",

    "funding_stage": "",

    "investors": [],

    "partners": [],

    "awards": [],

    "social_media": {{
        "linkedin": "",
        "facebook": "",
        "instagram": "",
        "twitter": "",
        "youtube": ""
    }}
}}

CONTENT:

{content}
"""


# =====================================================
# MAIN ENRICHMENT
# =====================================================

async def enrich_from_website(
    entity: Dict
) -> Dict:

    website = entity.get(
        "website",
        ""
    )

    if not website:

        return entity

    print(
        f"[WEBSITE ENRICHMENT] {website}"
    )

    # -------------------------------------------------
    # SCRAPING
    # -------------------------------------------------

    try:

        content = await scrape_url(
            website
        )

    except Exception as e:

        print(
            f"[SCRAPE ERROR] {e}"
        )

        return entity

    if not content:

        return entity

    # -------------------------------------------------
    # SAVE WEBSITE CONTENT
    # -------------------------------------------------

    entity[
        "website_content"
    ] = content[:15000]

    entity[
        "website_metadata"
    ] = {

        "url":
        website,

        "content_length":
        len(content)
    }

    # -------------------------------------------------
    # REGEX EXTRACTION
    # -------------------------------------------------

    entity[
        "emails"
    ] = extract_emails(
        content
    )

    entity[
        "phones"
    ] = extract_phone_numbers(
        content
    )

    # -------------------------------------------------
    # LLM EXTRACTION
    # -------------------------------------------------

    prompt = build_prompt(
        content
    )

    response = call_llm(
        prompt=prompt,
        max_tokens=2500
    )

    llm_data = parse_llm_json(
        response
    )

    if not llm_data:

        print(
            "[WARNING] No LLM data extracted"
        )

        return entity

    # -------------------------------------------------
    # SMART MERGE
    # -------------------------------------------------

    for field, value in llm_data.items():

        if value in (
            "",
            None,
            [],
            {}
        ):
            continue

        existing = entity.get(
            field
        )

        # LIST MERGE

        if (
            isinstance(value, list)
            and isinstance(
                existing,
                list
            )
        ):

            entity[field] = list(
                {
                    *existing,
                    *value
                }
            )

        # DICT MERGE

        elif (
            isinstance(value, dict)
            and isinstance(
                existing,
                dict
            )
        ):

            existing.update(
                value
            )

            entity[field] = existing

        # SIMPLE VALUE

        elif not existing:

            entity[field] = value

    return entity
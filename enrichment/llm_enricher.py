
# enrichment/llm_enricher.py

import json
from typing import Dict, Any

from llm.openrouter_client import call_llm
from utils.json_tools import parse_llm_json


# =====================================================
# HELPERS
# =====================================================

def compact_tavily_data(
    tavily_data: Dict
) -> Dict:

    return {

        "answer":
        tavily_data.get(
            "answer",
            ""
        ),

        "results": [

            {
                "title":
                result.get(
                    "title",
                    ""
                ),

                "url":
                result.get(
                    "url",
                    ""
                )
            }

            for result in tavily_data.get(
                "results",
                []
            )[:10]
        ]
    }


def merge_data(
    original: Dict,
    enriched: Dict
) -> Dict:

    merged = original.copy()

    for key, value in enriched.items():

        if value in (
            "",
            None,
            [],
            {}
        ):
            continue

        existing = merged.get(
            key
        )

        if (
            isinstance(value, list)
            and isinstance(
                existing,
                list
            )
        ):

            merged[key] = list(
                {
                    *existing,
                    *value
                }
            )

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

            merged[key] = existing

        else:

            merged[key] = value

    return merged


# =====================================================
# STARTUP PROMPT
# =====================================================

def build_startup_enrichment_prompt(
    startup: Dict,
    tavily_data: Dict,
    website_content: str
) -> str:

    compact_tavily = (
        compact_tavily_data(
            tavily_data
        )
    )

    website_content = (
        website_content[:10000]
        if website_content
        else ""
    )

    return f"""
You are a startup intelligence analyst.

Your task is to enrich the startup profile.

Use ONLY the information provided.

Do NOT invent information.

Return ONLY valid JSON.

Schema:

{{
    "name": "",
    "description": "",

    "industry": "",
    "sub_industry": "",

    "country": "",
    "city": "",
    "headquarters": "",

    "website": "",
    "linkedin": "",

    "founders": [],
    "team_members": [],

    "emails": [],
    "phones": [],

    "technologies": [],

    "products": [],
    "services": [],

    "business_model": "",
    "target_market": "",

    "founded_year": "",
    "employees_count": "",

    "funding_stage": "",
    "funding_amount": "",

    "investors": [],

    "customers": [],
    "partners": [],
    "competitors": [],

    "awards": [],

    "social_media": {{
        "linkedin": "",
        "facebook": "",
        "instagram": "",
        "twitter": "",
        "youtube": ""
    }}
}}

INITIAL STARTUP JSON:

{json.dumps(
    startup,
    indent=2,
    ensure_ascii=False
)}

TAVILY:

{json.dumps(
    compact_tavily,
    indent=2,
    ensure_ascii=False
)}

WEBSITE CONTENT:

{website_content}
"""
    

# =====================================================
# INVESTOR PROMPT
# =====================================================

def build_investor_enrichment_prompt(
    investor: Dict,
    tavily_data: Dict,
    website_content: str
) -> str:

    compact_tavily = (
        compact_tavily_data(
            tavily_data
        )
    )

    website_content = (
        website_content[:10000]
        if website_content
        else ""
    )

    return f"""
You are a venture capital intelligence analyst.

Your task is to enrich the investor profile.

Use ONLY the information provided.

Do NOT invent information.

Return ONLY valid JSON.

Schema:

{{
    "name": "",
    "description": "",

    "website": "",
    "linkedin": "",

    "country": "",
    "city": "",

    "emails": [],
    "phones": [],

    "aum": "",

    "ticket_size": "",

    "investment_focus": [],

    "investment_stages": [],

    "geographic_focus": [],

    "portfolio_startups": [],

    "partners": [],

    "social_media": {{
        "linkedin": "",
        "facebook": "",
        "twitter": ""
    }}
}}

INITIAL INVESTOR JSON:

{json.dumps(
    investor,
    indent=2,
    ensure_ascii=False
)}

TAVILY:

{json.dumps(
    compact_tavily,
    indent=2,
    ensure_ascii=False
)}

WEBSITE CONTENT:

{website_content}
"""
    

# =====================================================
# STARTUP ENRICHMENT
# =====================================================

def enrich_startup_with_llm(
    startup: Dict,
    tavily_data: Dict,
    website_content: str
) -> Dict:

    prompt = (
        build_startup_enrichment_prompt(
            startup,
            tavily_data,
            website_content
        )
    )

    response = call_llm(
        prompt=prompt,
        max_tokens=3000
    )

    result = parse_llm_json(
        response
    )

    if not result:

        print(
            "[LLM] Startup enrichment failed"
        )

        return startup

    return merge_data(
        startup,
        result
    )


# =====================================================
# INVESTOR ENRICHMENT
# =====================================================

def enrich_investor_with_llm(
    investor: Dict,
    tavily_data: Dict,
    website_content: str
) -> Dict:

    prompt = (
        build_investor_enrichment_prompt(
            investor,
            tavily_data,
            website_content
        )
    )

    response = call_llm(
        prompt=prompt,
        max_tokens=3000
    )

    result = parse_llm_json(
        response
    )

    if not result:

        print(
            "[LLM] Investor enrichment failed"
        )

        return investor

    return merge_data(
        investor,
        result
    )

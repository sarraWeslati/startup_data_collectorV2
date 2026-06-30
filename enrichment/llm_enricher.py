
# enrichment/llm_enricher.py

import json
from typing import Dict
from llm.openrouter_client import call_llm_json
from utils.json_tools import parse_llm_json


# =====================================================
# HELPERS
# =====================================================

def compact_tavily_data(
    tavily_data: Dict
) -> Dict:
    """
    Réduit la réponse Tavily afin d'envoyer
    uniquement les informations utiles au LLM.
    """

    compact_results = []

    for result in tavily_data.get(
        "results",
        []
    )[:10]:

        compact_results.append({

            "title":
            result.get(
                "title",
                ""
            ),

            "url":
            result.get(
                "url",
                ""
            ),

            "content":
            result.get(
                "content",
                ""
            )[:1000],

            "score":
            result.get(
                "score",
                0
            )
        })

    return {

        "answer":
        tavily_data.get(
            "answer",
            ""
        ),

        "results":
        compact_results
    }


def merge_data(
    original: Dict,
    enriched: Dict
) -> Dict:
    """
    Fusion intelligente entre les données déjà connues
    et les données retournées par le LLM.
    """

    merged = original.copy()

    for key, value in enriched.items():

        # Ignore les valeurs vides
        if value in (
            "",
            None,
            [],
            {}
        ):
            continue

        existing = merged.get(key)

        # ----------------------------------
        # LISTES
        # ----------------------------------

        if (
            isinstance(existing, list)
            and isinstance(value, list)
        ):

            merged[key] = list(dict.fromkeys(

                item

                for item in (
                    existing + value
                )

                if item not in (
                    "",
                    None
                )
            ))

        # ----------------------------------
        # DICTIONNAIRES
        # ----------------------------------

        elif (
            isinstance(existing, dict)
            and isinstance(value, dict)
        ):

            merged_dict = existing.copy()

            for sub_key, sub_value in value.items():

                if sub_value not in (
                    "",
                    None,
                    [],
                    {}
                ):

                    merged_dict[sub_key] = sub_value

            merged[key] = merged_dict

        # ----------------------------------
        # VALEURS SIMPLES
        # ----------------------------------

        else:

            if not existing:

                merged[key] = value

    return merged

# =====================================================
# GENERIC LLM ENRICHMENT
# =====================================================

def enrich_with_llm(
    entity: Dict,
    prompt: str,
    entity_name: str,
    max_tokens: int = 3000
) -> Dict:
    """
    Fonction générique d'enrichissement LLM.
    """

    response = call_llm_json(
        prompt=prompt,
        max_tokens=max_tokens
    )

    result = parse_llm_json(
        response
    )

    if not result:

        print(
            f"[LLM] {entity_name} enrichment failed"
        )

        return entity

    return merge_data(
        entity,
        result
    )

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
You are an expert startup intelligence analyst.

Your task is to enrich an existing startup profile using ONLY the information provided.

Important rules:

- Never invent facts.
- Never guess missing information.
- Preserve existing information whenever possible.
- Only fill fields when there is clear evidence.
- Keep existing values if the evidence is uncertain.
- Merge complementary information instead of replacing valid data.
- Return ONLY valid JSON.
- Do not include markdown.
- Do not include explanations.
- Keep arrays unique (no duplicates).
- Keep URLs complete and valid.

Complete the following schema as much as possible.

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
You are an expert venture capital and investor intelligence analyst.

Your task is to enrich an existing investor profile using ONLY the information provided.

Important rules:

- Never invent facts.
- Never guess missing information.
- Preserve existing information whenever possible.
- Only fill fields when there is clear evidence.
- Keep existing values if the evidence is uncertain.
- Merge complementary information instead of replacing valid data.
- Return ONLY valid JSON.
- Do not include markdown.
- Do not include explanations.
- Keep arrays unique (no duplicates).
- Keep URLs complete and valid.

Complete the following schema as much as possible.

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

    prompt = build_startup_enrichment_prompt(
        startup,
        tavily_data,
        website_content
    )

    return enrich_with_llm(
        entity=startup,
        prompt=prompt,
        entity_name="Startup",
        max_tokens=3500
    )


# =====================================================
# INVESTOR ENRICHMENT
# =====================================================

def enrich_investor_with_llm(
    investor: Dict,
    tavily_data: Dict,
    website_content: str
) -> Dict:

    prompt = build_investor_enrichment_prompt(
        investor,
        tavily_data,
        website_content
    )

    return enrich_with_llm(
        entity=investor,
        prompt=prompt,
        entity_name="Investor",
        max_tokens=3500
    )

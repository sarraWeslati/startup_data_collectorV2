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
    Réduit la réponse Tavily pour ne conserver
    que les résultats les plus pertinents.
    """

    results = tavily_data.get("results", [])

    # Trier par score décroissant
    results = sorted(
        results,
        key=lambda r: r.get("score", 0),
        reverse=True
    )

    compact_results = []

    seen_urls = set()

    for result in results:

        url = result.get("url", "")

        # éviter les doublons
        if url in seen_urls:
            continue

        seen_urls.add(url)

        compact_results.append({

            "title": result.get("title", ""),

            "url": url,

            "score": result.get("score", 0),

            "content": result.get(
                "content",
                ""
            )[:800]
        })

        # garder uniquement les 8 meilleurs
        if len(compact_results) >= 8:
            break

    return {

        "answer": tavily_data.get(
            "answer",
            ""
        ),

        "results": compact_results
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

            merged_list = existing.copy()

            for item in value:

                if item in ("", None):
                    continue

                # Cas des dictionnaires
                if isinstance(item, dict):

                    name = item.get("name", "").lower()

                    already_exists = False

                    for existing_item in merged_list:

                        if (
                            isinstance(existing_item, dict)
                            and existing_item.get("name", "").lower() == name
                        ):
                            existing_item.update({
                                k: v
                                for k, v in item.items()
                                if v not in ("", None, [], {})
                            })

                            already_exists = True
                            break

                    if not already_exists:
                        merged_list.append(item)

                else:

                    if item not in merged_list:
                        merged_list.append(item)

            merged[key] = merged_list

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
    investors_data: Dict,
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

Use the section "INVESTOR SEARCH RESULTS" as the primary source
to populate the "investors" field.

For each investor found, return an object with:

{{
    "name": "",
    "website": "",
    "linkedin": "",
    "country": "",
    "investment_stage": "",
    "investment_round": "",
    "source": ""
}}

Use the following priority:

1. Funding mentions
2. Possible investors
3. Detailed investor search results
4. Search answers

Only return investors that are supported by at least one of these sources.

If multiple sources mention the same investor, keep only one entry.

Do not infer investors.

Do NOT include:
- partners
- customers
- incubators (unless they invested)
- accelerators (unless they invested)

If there is no explicit evidence of an investment,
return an empty array.

Do not confuse:

- partners
- incubators
- accelerators
- customers

Only include organizations that explicitly invested in the startup.

If no investor is mentioned, return an empty array.

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

=========================
INVESTOR SEARCH RESULTS
=========================

The following search results come from a dedicated Tavily search
using the query:

"investors for <startup_name>"

These results are specifically intended to identify investors
that funded this startup.

Possible investors:

{json.dumps(
    investors_data.get(
        "possible_investors",
        []
    ),
    indent=2,
    ensure_ascii=False
)}

Funding mentions:

{json.dumps(
    investors_data.get(
        "funding_mentions",
        []
    ),
    indent=2,
    ensure_ascii=False
)}

Search answers:

{json.dumps(
    investors_data.get(
        "answers",
        []
    ),
    indent=2,
        ensure_ascii=False
)}

Detailed investor search results:

{json.dumps(
    compact_tavily_data({

        "answer": "",

        "results": investors_data.get(
            "results",
            []
        )

    }),

    indent=2,
    ensure_ascii=False
)}
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
    investors_data: Dict,
    website_content: str
) -> Dict:
    """
    Enrichit une startup avec les données Tavily,
    les résultats de recherche des investisseurs
    et le contenu du site web.
    """

    prompt = build_startup_enrichment_prompt(
        startup=startup,
        tavily_data=tavily_data,
        investors_data=investors_data,
        website_content=website_content
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

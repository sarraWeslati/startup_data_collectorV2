from datetime import datetime
from enrichment.serper_client import (
    serper_search,
    extract_company_website,
    extract_linkedin_url,
    extract_social_links
)
from enrichment.website_enricher import enrich_from_website
from enrichment.llm_client import call_llm, safe_json
from enrichment.query_expander import build_multi_queries


FIELDS = ["portfolio", "investment_focus", "funds", "leadership"]


def merge(a, b):
    for k, v in b.items():
        if v and not a.get(k):
            a[k] = v
    return a


async def enrich_investor(investor):

    name = investor.get("name", "")
    if not name:
        return investor

    print(f"[INVESTOR] {name}")

    queries = build_multi_queries(name, "investor")

    serper = {"organic": []}
    for q in queries:
        serper["organic"] += serper_search(q).get("organic", [])

    website = extract_company_website(serper)
    linkedin = extract_linkedin_url(serper)
    socials = extract_social_links(serper)

    if website:
        investor["website"] = website

    investor.setdefault("social_media", {}).update(socials)

    if linkedin:
        investor["linkedin"] = linkedin

    investor = enrich_from_website(investor)

    missing = sum(1 for f in FIELDS if not investor.get(f))

    if missing >= 2 and investor.get("website_content"):

        prompt = f"""
Extract VC structured data.

RULES:
- no invention
- only facts

DATA:
{investor}

SERPER:
{serper}

Return JSON only.
"""

        raw = call_llm(prompt)
        data = safe_json(raw)

        if isinstance(data, dict):
            investor = merge(investor, data)

    investor["enrichment"] = {
        "status": "done",
        "date": datetime.utcnow().isoformat()
    }

    return investor
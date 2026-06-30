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
from enrichment.wikipedia_client import get_wikipedia_summary

async def enrich_from_wikipedia(startup):
    name = startup.get("name")

    wiki = get_wikipedia_summary(name)

    if wiki:
        startup["wikipedia"] = wiki

        # enrich description si vide
        if not startup.get("description") and wiki.get("summary"):
            startup["description"] = wiki["summary"]

        # extra fields
        if not startup.get("headquarters"):
            startup["others"]["wiki_url"] = wiki.get("url")

    return startup

IMPORTANT_FIELDS = ["industry", "description", "founders", "funding", "products"]


def should_use_llm(entity, content):
    missing = sum(1 for f in IMPORTANT_FIELDS if not entity.get(f))
    return content and missing >= 3


def merge(a, b):
    for k, v in b.items():
        if v and not a.get(k):
            a[k] = v
    return a


async def enrich_startup(startup):

    name = startup.get("name", "")
    if not name:
        return startup

    print(f"[STARTUP] {name}")

    queries = build_multi_queries(name, "startup")

    serper = {"organic": []}
    for q in queries:
        serper["organic"] += serper_search(q).get("organic", [])

    website = extract_company_website(serper)
    linkedin = extract_linkedin_url(serper)
    socials = extract_social_links(serper)

    if website:
        startup["website"] = website

    startup.setdefault("social_media", {}).update(socials)

    if linkedin:
        startup["linkedin"] = linkedin

    startup = enrich_from_website(startup)
    content = startup.get("website_content", "")

    if should_use_llm(startup, content):

        prompt = f"""
Extract startup structured data.

RULES:
- no invention
- only facts
- empty if unknown

DATA:
{startup}

SERPER:
{serper}

CONTENT:
{content[:6000]}

Return JSON only.
"""

        raw = call_llm(prompt)
        data = safe_json(raw)

        if isinstance(data, dict):
            startup = merge(startup, data)

    startup["enrichment"] = {
        "status": "done",
        "date": datetime.utcnow().isoformat()
    }

    return startup
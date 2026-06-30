import copy
import re
from typing import Any, Dict

from collectors.website_collector import scrape_url
from llm.openrouter_client import call_llm
from utils.json_tools import parse_llm_json


# =====================================================
# REGEX
# =====================================================

EMAIL_REGEX = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

PHONE_REGEX = re.compile(
    r"\+?\d[\d\s\-\(\)]{7,20}"
)


SOCIAL_PATTERNS = {

    "linkedin":
    re.compile(
        r"https?://(?:[\w]+\.)?linkedin\.com/[^\s\"'>]+",
        re.IGNORECASE
    ),

    "facebook":
    re.compile(
        r"https?://(?:[\w]+\.)?facebook\.com/[^\s\"'>]+",
        re.IGNORECASE
    ),

    "instagram":
    re.compile(
        r"https?://(?:[\w]+\.)?instagram\.com/[^\s\"'>]+",
        re.IGNORECASE
    ),

    "youtube":
    re.compile(
        r"https?://(?:[\w]+\.)?youtube\.com/[^\s\"'>]+",
        re.IGNORECASE
    ),

    "github":
    re.compile(
        r"https?://(?:[\w]+\.)?github\.com/[^\s\"'>]+",
        re.IGNORECASE
    )
}


# =====================================================
# REGEX HELPERS
# =====================================================

def extract_emails(
    content: str
) -> list[str]:

    return sorted(
        set(
            EMAIL_REGEX.findall(content)
        )
    )


def extract_phone_numbers(
    content: str
) -> list[str]:

    phones = []

    for phone in PHONE_REGEX.findall(content):

        cleaned = " ".join(
            phone.split()
        )

        if cleaned not in phones:

            phones.append(
                cleaned
            )

    return phones


def extract_social_links(
    content: str
) -> Dict[str, str]:

    socials = {

        "linkedin": "",
        "facebook": "",
        "instagram": "",
        "youtube": "",
        "github": ""
    }

    for platform, pattern in SOCIAL_PATTERNS.items():

        match = pattern.search(content)

        if match:

            socials[platform] = match.group(0)

    return socials


# =====================================================
# DEEP MERGE
# =====================================================

def deep_merge(
    original: Any,
    incoming: Any
) -> Any:

    if incoming in (
        "",
        None,
        [],
        {}
    ):
        return original

    # -----------------------------------
    # Dict
    # -----------------------------------

    if (
        isinstance(original, dict)
        and isinstance(incoming, dict)
    ):

        merged = copy.deepcopy(
            original
        )

        for key, value in incoming.items():

            if key not in merged:

                merged[key] = value

            else:

                merged[key] = deep_merge(
                    merged[key],
                    value
                )

        return merged

    # -----------------------------------
    # List
    # -----------------------------------

    if (
        isinstance(original, list)
        and isinstance(incoming, list)
    ):

        merged = copy.deepcopy(
            original
        )

        for item in incoming:

            if item not in merged:

                merged.append(item)

        return merged

    # -----------------------------------
    # Primitive values
    # -----------------------------------

    if original in (
        "",
        None
    ):

        return incoming

    return original
# =====================================================
# PROMPT
# =====================================================

def build_prompt(
    content: str
) -> str:

    content = content[:15000]

    return f"""
You are an expert startup and investor intelligence analyst.

Your task is to extract ONLY information that is explicitly mentioned in the company's official website.

The company MUST be located in Africa.

If the company is clearly not located in Africa,
set:

"country": ""
"city": ""

Do not guess.

Do not infer.

Only use explicit information.

Do NOT invent information.

Do NOT infer missing information.

If a field cannot be determined, keep its default value.

Return ONLY valid JSON.

The JSON must follow this schema.

{{
    "description": "",
    "tagline": "",

    "industry": "",
    "keywords": [],

    "country": "",
    "city": "",
    "headquarters": "",

    "website": "",
    "linkedin_url": "",

    "social_media": {{
        "linkedin": "",
        "facebook": "",
        "instagram": "",
        "youtube": "",
        "github": ""
    }},

    "contact": {{
        "emails": [],
        "phones": [],
        "address": ""
    }},

    "founders": [
        {{
            "name": "",
            "role": "",
            "linkedin": "",
            "bio": ""
        }}
    ],

    "leadership": [
        {{
            "name": "",
            "role": "",
            "linkedin": "",
            "bio": ""
        }}
    ],

    "employee_count": null,
    "employee_range": "",
    "team_size": "",

    "products": [
        {{
            "name": "",
            "description": "",
            "category": ""
        }}
    ],

    "services": [],

    "technologies": [],

    "customer_segments": [],

    "target_market": "",

    "operating_countries": [],

    "languages_supported": [],

    "notable_customers": [],

    "partners": [],

    "accelerators": [],

    "incubators": [],

    "investors": [
        {{
            "name": "",
            "type": "",
            "website": "",
            "country": ""
        }}
    ],

    "awards": [],

    "certifications": [],

    "patents": [],

    "legal_info": {{
        "company_type": "",
        "registration_number": ""
    }}
}}

Extraction rules:

- Extract ONLY facts explicitly present in the website.
- Never guess missing information.
- Never invent founders.
- Never invent investors.
- Never invent technologies.
- Never invent products.
- Never infer startup stage.
- Keep empty strings if unknown.
- Keep empty arrays if unknown.
- Keep null values if unknown.
- Return ONLY valid JSON.
- Do not use markdown.

WEBSITE CONTENT:

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
    # SCRAP WEBSITE
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
    # SAVE RAW WEBSITE CONTENT
    # -------------------------------------------------

    entity["website_content"] = content[:15000]

    entity["website_metadata"] = {

        "url": website,

        "content_length": len(content)
    }

    # -------------------------------------------------
    # CONTACT
    # -------------------------------------------------

    contact = entity.setdefault(
        "contact",
        {}
    )

    contact["emails"] = deep_merge(
        contact.get(
            "emails",
            []
        ),
        extract_emails(content)
    )

    contact["phones"] = deep_merge(
        contact.get(
            "phones",
            []
        ),
        extract_phone_numbers(content)
    )

    contact.setdefault(
        "address",
        ""
    )

    entity["contact"] = contact

    # -------------------------------------------------
    # SOCIAL MEDIA
    # -------------------------------------------------

    socials = extract_social_links(
        content
    )

    entity["social_media"] = deep_merge(

        entity.get(
            "social_media",
            {}
        ),

        socials
    )

    # -------------------------------------------------
    # INITIALIZE OPTIONAL FIELDS
    # -------------------------------------------------

    entity.setdefault(
        "founders",
        []
    )

    entity.setdefault(
        "leadership",
        []
    )

    entity.setdefault(
        "products",
        []
    )

    entity.setdefault(
        "services",
        []
    )

    entity.setdefault(
        "technologies",
        []
    )

    entity.setdefault(
        "partners",
        []
    )

    entity.setdefault(
        "investors",
        []
    )

    entity.setdefault(
        "accelerators",
        []
    )

    entity.setdefault(
        "incubators",
        []
    )

    entity.setdefault(
        "keywords",
        []
    )

    entity.setdefault(
        "customer_segments",
        []
    )

    entity.setdefault(
        "operating_countries",
        []
    )

    entity.setdefault(
        "languages_supported",
        []
    )

    entity.setdefault(
        "notable_customers",
        []
    )

    entity.setdefault(
        "awards",
        []
    )

    entity.setdefault(
        "certifications",
        []
    )

    entity.setdefault(
        "patents",
        []
    )

    entity.setdefault(
        "legal_info",
        {}
    )

    # -------------------------------------------------
    # LLM EXTRACTION
    # -------------------------------------------------

    prompt = build_prompt(
        content
    )

    response = call_llm(
        prompt=prompt,
        max_tokens=3000
    )

    llm_data = parse_llm_json(
        response
    )

    if not llm_data:

        print(
            "[WARNING] No data extracted from website"
        )

        return entity
        # -------------------------------------------------
    # DEEP MERGE
    # -------------------------------------------------

    entity = deep_merge(
        entity,
        llm_data
    )

    # -------------------------------------------------
    # UPDATE CONTACT (REGEX HAS PRIORITY)
    # -------------------------------------------------

    contact = entity.setdefault(
        "contact",
        {}
    )

    contact["emails"] = deep_merge(
        contact.get(
            "emails",
            []
        ),
        extract_emails(content)
    )

    contact["phones"] = deep_merge(
        contact.get(
            "phones",
            []
        ),
        extract_phone_numbers(content)
    )

    entity["contact"] = contact

    # -------------------------------------------------
    # UPDATE SOCIAL LINKS
    # -------------------------------------------------

    entity["social_media"] = deep_merge(

        entity.get(
            "social_media",
            {}
        ),

        extract_social_links(content)
    )

    # -------------------------------------------------
    # ENRICHMENT METADATA
    # -------------------------------------------------

    enrichment = entity.setdefault(
        "enrichment",
        {}
    )

    enrichment["status"] = "completed"

    enrichment["sources_used"] = deep_merge(

        enrichment.get(
            "sources_used",
            []
        ),

        ["website"]
    )

    enrichment.setdefault(
        "collection_date",
        ""
    )

    enrichment.setdefault(
        "last_updated",
        ""
    )

    # -------------------------------------------------
    # STATS
    # -------------------------------------------------

    stats = entity.setdefault(
        "stats",
        {}
    )

    stats["has_website"] = bool(
        entity.get(
            "website"
        )
    )

    stats["has_linkedin"] = bool(

        entity.get(
            "linkedin_url"
        )

        or

        entity.get(
            "social_media",
            {}
        ).get(
            "linkedin"
        )
    )

    stats["founders_count"] = len(
        entity.get(
            "founders",
            []
        )
    )

    stats["leadership_count"] = len(
        entity.get(
            "leadership",
            []
        )
    )

    stats["investors_count"] = len(
        entity.get(
            "investors",
            []
        )
    )

    stats["products_count"] = len(
        entity.get(
            "products",
            []
        )
    )

    stats["services_count"] = len(
        entity.get(
            "services",
            []
        )
    )

    stats["technologies_count"] = len(
        entity.get(
            "technologies",
            []
        )
    )

    stats["news_count"] = len(
        entity.get(
            "recent_news",
            []
        )
    )

    entity["stats"] = stats

    # -------------------------------------------------
    # WEBSITE SOURCE
    # -------------------------------------------------

    entity.setdefault(
        "sources",
        []
    )

    website_source = {

        "type": "website",

        "url": website,

        "confidence": 1.0
    }

    if website_source not in entity["sources"]:

        entity["sources"].append(
            website_source
        )

    # -------------------------------------------------
    # CLEANUP
    # -------------------------------------------------

    if not entity.get("linkedin_url"):

        linkedin = entity.get(
            "social_media",
            {}
        ).get(
            "linkedin",
            ""
        )

        if linkedin:

            entity["linkedin_url"] = linkedin

    return entity
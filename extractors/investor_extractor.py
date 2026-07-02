# extractors/investor_extractor.py

from typing import Dict

from llm.openrouter_client import call_llm_json
from schemas.investor_schema import get_empty_investor
from utils.json_tools import parse_llm_json
from utils.url_normalizer import normalize_website
from utils.investor_normalizer import normalize_investor

def build_investor_prompt(
    content: str
) -> str:

    content = content[:40000]

    return f"""
You are an expert Venture Capital, Angel Investor and Investment Intelligence analyst.

Your task is to extract ONLY the information that is explicitly stated in the document.

Never invent information.

Never infer information.

Never guess.

Return ONLY valid JSON.

Use the following schema.

{{
    "name": "",
    "description": "",
    "tagline": "",

    "organization_type": "",

    "country": "",
    "city": "",
    "headquarters": "",

    "website": "",
    "linkedin": "",

    "social_media": {{
        "linkedin": "",
        "facebook": "",
        "twitter": "",
        "instagram": "",
        "youtube": "",
        "github": ""
    }},

    "emails": [],
    "phones": [],
    "address": "",

    "investment_focus": [],
    "investment_stages": [],
    "preferred_industries": [],
    "geographic_focus": [],

    "ticket_size": "",
    "aum": "",

    "portfolio_startups": [],

    "partners": [],
    "team_members": [],

    "investment_thesis": "",

    "co_investors": [],

    "accelerators": [],
    "incubators": [],

    "awards": [],
    "certifications": [],

    "recent_news": [],
    "events": [],

    "legal_info": {{
        "company_type": "",
        "registration_number": ""
    }},

    "extra_notes": ""
}}

Extraction rules:

- Return ONLY JSON.
- Do not use Markdown.
- Do not write explanations.
- Do not add comments.

General rules:

- Keep empty strings if the value is missing.
- Keep empty arrays if no information exists.
- Never create information.
- Never estimate dates or values.
- Preserve URLs exactly as written.

Investment Focus:

Extract sectors such as:

- FinTech
- HealthTech
- EdTech
- AI
- SaaS
- Mobility
- AgriTech
- ClimateTech
- Energy
- DeepTech
- Cybersecurity
- E-commerce
- FoodTech
- Manufacturing

Investment Stages:

Extract stages such as:

- Pre-seed
- Seed
- Series A
- Series B
- Series C
- Growth
- Late Stage

Organization Type:

Extract one of:

- Venture Capital
- VC Fund
- Angel Investor
- Corporate Venture Capital
- Family Office
- Accelerator
- Incubator
- Government Fund
- Investment Company

Portfolio:

Extract ONLY startups explicitly listed as portfolio companies.

Partners:

Extract ONLY investment partners, managing partners,
general partners or venture partners.

Team Members:

Extract founders, principals, investment managers,
analysts, associates and executives.

Co-investors:

Extract ONLY organizations explicitly mentioned as
co-investors.

Contact:

Extract all emails.

Extract all phone numbers.

Extract complete postal address if available.

Do not confuse:

- Startup founders
- Portfolio founders
- Advisors
- Customers

with investor team members.

CONTENT:

{content}
"""

def merge_investor_data(
    investor: Dict,
    extracted: Dict
) -> Dict:
    """
    Fusion intelligente entre le schéma vide
    et les données extraites par le LLM.
    """

    for key, value in extracted.items():

        # Ignore les valeurs vides
        if value in (
            "",
            None,
            [],
            {}
        ):
            continue

        # -------------------------
        # Website
        # -------------------------

        if key == "website":

            investor["website"] = normalize_website(
                value
            )

            continue

        # -------------------------
        # LinkedIn
        # -------------------------

        if key == "linkedin":

            if isinstance(value, str):

                investor["linkedin"] = value.strip()

            continue

        existing = investor.get(key)

        # -------------------------
        # Dictionnaires
        # -------------------------

        if (
            isinstance(existing, dict)
            and isinstance(value, dict)
        ):

            merged = existing.copy()

            for sub_key, sub_value in value.items():

                if sub_value not in (
                    "",
                    None,
                    [],
                    {}
                ):
                    merged[sub_key] = sub_value

            investor[key] = merged

        # -------------------------
        # Listes
        # -------------------------

        elif (
            isinstance(existing, list)
            and isinstance(value, list)
        ):

            merged = existing.copy()

            for item in value:

                if item not in merged:

                    merged.append(item)

            investor[key] = merged

        # -------------------------
        # Valeurs simples
        # -------------------------

        else:

            investor[key] = value

    return investor

def update_investor_stats(
    investor: Dict
) -> Dict:
    """
    Met à jour automatiquement les statistiques
    de l'investisseur.
    """

    stats = investor.setdefault(
        "stats",
        {}
    )

    stats["has_website"] = bool(
        investor.get("website")
    )

    stats["has_linkedin"] = bool(

        investor.get("linkedin")

        or investor.get(
            "social_media",
            {}
        ).get("linkedin")
    )

    stats["portfolio_count"] = len(

        investor.get(
            "portfolio_startups",
            []
        )
    )

    stats["partners_count"] = len(

        investor.get(
            "partners",
            []
        )
    )

    stats["team_members_count"] = len(

        investor.get(
            "team_members",
            []
        )
    )

    stats["investment_focus_count"] = len(

        investor.get(
            "investment_focus",
            []
        )
    )

    return investor

def update_investor_confidence(
    investor: Dict
) -> Dict:
    """
    Calcule automatiquement les scores
    de confiance de l'investisseur.
    """

    confidence = investor.setdefault(
        "confidence",
        {}
    )

    confidence["description"] = (

        1.0

        if investor.get(
            "description"
        )

        else 0.0

    )

    confidence["investment_focus"] = (

        1.0

        if investor.get(
            "investment_focus",
            []
        )

        else 0.0

    )

    confidence["portfolio"] = (

        1.0

        if investor.get(
            "portfolio_startups",
            []
        )

        else 0.0

    )

    confidence["partners"] = (

        1.0

        if investor.get(
            "partners",
            []
        )

        else 0.0

    )

    confidence["team"] = (

        1.0

        if investor.get(
            "team_members",
            []
        )

        else 0.0

    )

    scores = [

        confidence["description"],

        confidence["investment_focus"],

        confidence["portfolio"],

        confidence["partners"],

        confidence["team"]

    ]

    confidence["overall"] = round(

        sum(scores) / len(scores),

        2

    )

    return investor

def extract_investor(
    content: str
) -> Dict:

    prompt = build_investor_prompt(content)

    response = call_llm_json(
        prompt=prompt,
        max_tokens=3500
    )

    investor = get_empty_investor()

    extracted = parse_llm_json(
        response
    )

    if not isinstance(extracted, dict):

        investor["extraction_error"] = (
            "LLM returned invalid JSON."
        )

        return investor

    if not extracted:

        investor["extraction_error"] = (
            "Unable to parse LLM response."
        )

        return investor

    investor = merge_investor_data(
        investor,
        extracted
    )

    # =====================================================
    # Website normalization
    # =====================================================

    website = investor.get("website", "")

    if isinstance(website, str):
        investor["website"] = normalize_website(website)
    else:
        investor["website"] = ""


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

    investor = update_investor_stats(
        investor
    )

    investor = update_investor_confidence(
        investor
    )

    LIST_FIELDS = [

        "emails",
        "phones",
        "investment_focus",
        "investment_stages",
        "preferred_industries",
        "geographic_focus",
        "portfolio_startups",
        "partners",
        "team_members",
        "co_investors",
        "accelerators",
        "incubators",
        "awards",
        "certifications",
        "recent_news",
        "events"

    ]

    for field in LIST_FIELDS:

        if not isinstance(
            investor.get(field),
            list
        ):
            investor[field] = []

    investor = normalize_investor(
        investor
    )

    return investor
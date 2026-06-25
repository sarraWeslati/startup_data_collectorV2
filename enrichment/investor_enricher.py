# enrichment/investor_enricher.py

from datetime import datetime

from enrichment.website_enricher import (
    enrich_from_website
)

from enrichment.tavily_client import (
    search_investor,
    extract_company_website,
    extract_linkedin_url,
    extract_crunchbase_url,
    extract_social_links
)

from enrichment.llm_enricher import (
    enrich_investor_with_llm
)


async def enrich_investor(
    investor: dict
) -> dict:
    """
    Investor enrichment pipeline

    1. Website enrichment
    2. Tavily Deep Search
    3. LLM enrichment
    4. Metadata generation
    """

    investor_name = investor.get(
        "name",
        ""
    ).strip()

    if not investor_name:

        print(
            "[ENRICHMENT] Investor name missing"
        )

        return investor

    print(
        f"[ENRICHING INVESTOR] {investor_name}"
    )

    # =====================================
    # WEBSITE ENRICHMENT
    # =====================================

    try:

        investor = await enrich_from_website(
            investor
        )

    except Exception as e:

        print(
            f"[WEBSITE ERROR] {e}"
        )

    # =====================================
    # TAVILY DEEP SEARCH
    # =====================================

    tavily_data = {}

    website = ""
    linkedin = ""
    crunchbase = ""

    socials = {}

    try:

        tavily_data = search_investor(
            investor_name
        )

        if not isinstance(
            tavily_data,
            dict
        ):

            tavily_data = {}

        website = (
            extract_company_website(
                tavily_data
            )
        )

        linkedin = (
            extract_linkedin_url(
                tavily_data
            )
        )

        crunchbase = (
            extract_crunchbase_url(
                tavily_data
            )
        )

        socials = (
            extract_social_links(
                tavily_data
            )
        )

        # Website

        if (
            website
            and not investor.get(
                "website"
            )
        ):

            investor[
                "website"
            ] = website

        # LinkedIn

        if (
            linkedin
            and not investor.get(
                "linkedin"
            )
        ):

            investor[
                "linkedin"
            ] = linkedin

        # Crunchbase

        if crunchbase:

            investor[
                "crunchbase"
            ] = crunchbase

        # Social Media

        existing_socials = (
            investor.get(
                "social_media",
                {}
            )
        )

        if not isinstance(
            existing_socials,
            dict
        ):

            existing_socials = {}

        existing_socials.update(
            socials
        )

        investor[
            "social_media"
        ] = existing_socials

    except Exception as e:

        print(
            f"[TAVILY ERROR] {e}"
        )

        tavily_data = {}

    # =====================================
    # WEBSITE CONTENT
    # =====================================

    website_content = investor.get(
        "website_content",
        ""
    )

    if website_content:

        website_content = (
            website_content[:15000]
        )

    # =====================================
    # LLM ENRICHMENT
    # =====================================

    try:

        enriched_investor = (
            enrich_investor_with_llm(
                investor=investor,
                tavily_data=tavily_data,
                website_content=website_content
            )
        )

        if not isinstance(
            enriched_investor,
            dict
        ):

            print(
                "[WARNING] Invalid LLM result"
            )

            enriched_investor = investor

    except Exception as e:

        print(
            f"[LLM ERROR] {e}"
        )

        return investor

    # =====================================
    # PRESERVE TAVILY DATA
    # =====================================

    if (
        website
        and not enriched_investor.get(
            "website"
        )
    ):

        enriched_investor[
            "website"
        ] = website

    if (
        linkedin
        and not enriched_investor.get(
            "linkedin"
        )
    ):

        enriched_investor[
            "linkedin"
        ] = linkedin

    if crunchbase:

        enriched_investor[
            "crunchbase"
        ] = crunchbase

    existing_socials = (
        enriched_investor.get(
            "social_media",
            {}
        )
    )

    if not isinstance(
        existing_socials,
        dict
    ):

        existing_socials = {}

    existing_socials.update(
        socials
    )

    enriched_investor[
        "social_media"
    ] = existing_socials

    # =====================================
    # EXTERNAL PROFILES
    # =====================================

    enriched_investor[
        "external_profiles"
    ] = {

        "website":
        website,

        "linkedin":
        linkedin,

        "crunchbase":
        crunchbase
    }

    # =====================================
    # ENTITY TYPE
    # =====================================

    enriched_investor[
        "entity_type"
    ] = investor.get(
        "entity_type",
        "investor"
    )

    # =====================================
    # ENRICHMENT METADATA
    # =====================================

    enriched_investor[
        "enrichment"
    ] = {

        "status":
        "completed",

        "sources": [
            "website",
            "tavily",
            "llm"
        ],

        "date":
        datetime.utcnow().isoformat()
    }

    # =====================================
    # TAVILY METADATA
    # =====================================

    enriched_investor[
        "tavily"
    ] = {

        "query":
        investor_name,

        "results_count":
        len(
            tavily_data.get(
                "results",
                []
            )
        ),

        "answer":
        tavily_data.get(
            "answer",
            ""
        )
    }

    # =====================================
    # STATS
    # =====================================

    enriched_investor[
        "stats"
    ] = {

        "has_website":
        bool(
            enriched_investor.get(
                "website"
            )
        ),

        "has_linkedin":
        bool(
            enriched_investor.get(
                "linkedin"
            )
        ),

        "portfolio_count":
        len(
            enriched_investor.get(
                "portfolio_startups",
                []
            )
        ),

        "focus_count":
        len(
            enriched_investor.get(
                "investment_focus",
                []
            )
        ),

        "partners_count":
        len(
            enriched_investor.get(
                "partners",
                []
            )
        ),

        "team_members_count":
        len(
            enriched_investor.get(
                "team_members",
                []
            )
        )
    }

    return enriched_investor
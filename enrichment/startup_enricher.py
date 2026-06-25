# enrichment/startup_enricher.py

from datetime import datetime

from enrichment.website_enricher import (
    enrich_from_website
)

from enrichment.tavily_client import (
    search_startup,
    extract_company_website,
    extract_linkedin_url,
    extract_crunchbase_url,
    extract_wellfound_url,
    extract_social_links
)

from enrichment.llm_enricher import (
    enrich_startup_with_llm
)


async def enrich_startup(
    startup: dict
) -> dict:
    """
    Startup enrichment pipeline

    1. Website enrichment
    2. Tavily Deep Search
    3. LLM enrichment
    4. Metadata generation
    """

    startup_name = startup.get(
        "name",
        ""
    ).strip()

    if not startup_name:

        print(
            "[ENRICHMENT] Startup name missing"
        )

        return startup

    print(
        f"[ENRICHING STARTUP] {startup_name}"
    )

    # =====================================
    # WEBSITE ENRICHMENT
    # =====================================

    try:

        startup = await enrich_from_website(
            startup
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
    wellfound = ""

    socials = {}

    try:

        tavily_data = search_startup(
            startup_name
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

        wellfound = (
            extract_wellfound_url(
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
            and not startup.get(
                "website"
            )
        ):

            startup[
                "website"
            ] = website

        # LinkedIn

        if (
            linkedin
            and not startup.get(
                "linkedin"
            )
        ):

            startup[
                "linkedin"
            ] = linkedin

        # Crunchbase

        if crunchbase:

            startup[
                "crunchbase"
            ] = crunchbase

        # Wellfound

        if wellfound:

            startup[
                "wellfound"
            ] = wellfound

        # Socials

        existing_socials = (
            startup.get(
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

        startup[
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

    website_content = startup.get(
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

        enriched_startup = (
            enrich_startup_with_llm(
                startup=startup,
                tavily_data=tavily_data,
                website_content=website_content
            )
        )

        if not isinstance(
            enriched_startup,
            dict
        ):

            print(
                "[WARNING] Invalid LLM result"
            )

            enriched_startup = startup

    except Exception as e:

        print(
            f"[LLM ERROR] {e}"
        )

        return startup

    # =====================================
    # PRESERVE TAVILY DATA
    # =====================================

    if (
        website
        and not enriched_startup.get(
            "website"
        )
    ):

        enriched_startup[
            "website"
        ] = website

    if (
        linkedin
        and not enriched_startup.get(
            "linkedin"
        )
    ):

        enriched_startup[
            "linkedin"
        ] = linkedin

    if crunchbase:

        enriched_startup[
            "crunchbase"
        ] = crunchbase

    if wellfound:

        enriched_startup[
            "wellfound"
        ] = wellfound

    existing_socials = (
        enriched_startup.get(
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

    enriched_startup[
        "social_media"
    ] = existing_socials

    # =====================================
    # EXTERNAL PROFILES
    # =====================================

    enriched_startup[
        "external_profiles"
    ] = {

        "website":
        website,

        "linkedin":
        linkedin,

        "crunchbase":
        crunchbase,

        "wellfound":
        wellfound
    }

    # =====================================
    # ENTITY TYPE
    # =====================================

    enriched_startup[
        "entity_type"
    ] = startup.get(
        "entity_type",
        "startup"
    )

    # =====================================
    # ENRICHMENT METADATA
    # =====================================

    enriched_startup[
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

    enriched_startup[
        "tavily"
    ] = {

        "query":
        startup_name,

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

    enriched_startup[
        "stats"
    ] = {

        "has_website":
        bool(
            enriched_startup.get(
                "website"
            )
        ),

        "has_linkedin":
        bool(
            enriched_startup.get(
                "linkedin"
            )
        ),

        "founders_count":
        len(
            enriched_startup.get(
                "founders",
                []
            )
        ),

        "investors_count":
        len(
            enriched_startup.get(
                "investors",
                []
            )
        ),

        "products_count":
        len(
            enriched_startup.get(
                "products",
                []
            )
        ),

        "services_count":
        len(
            enriched_startup.get(
                "services",
                []
            )
        ),

        "technologies_count":
        len(
            enriched_startup.get(
                "technologies",
                []
            )
        )
    }

    return enriched_startup
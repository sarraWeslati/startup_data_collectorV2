
# enrichment/startup_enricher.py

from datetime import datetime

from enrichment.website_enricher import (
    enrich_from_website
)

from enrichment.tavily_client import (
    search_startup
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
    2. Tavily search
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
    # STEP 1
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
    # STEP 2
    # TAVILY SEARCH
    # =====================================

    try:

        tavily_data = search_startup(
            startup_name
        )

        if not isinstance(
            tavily_data,
            dict
        ):

            tavily_data = {}

    except Exception as e:

        print(
            f"[TAVILY ERROR] {e}"
        )

        tavily_data = {}

    # =====================================
    # STEP 3
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
    # STEP 4
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
    # STEP 5
    # ENTITY TYPE
    # =====================================

    enriched_startup[
        "entity_type"
    ] = startup.get(
        "entity_type",
        "startup"
    )

    # =====================================
    # STEP 6
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
    # STEP 7
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
    # STEP 8
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
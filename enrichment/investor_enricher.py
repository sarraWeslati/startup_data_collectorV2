# enrichment/investor_enricher.py

from datetime import datetime

from enrichment.website_enricher import (
    enrich_from_website
)

from enrichment.tavily_client import (
    search_investor
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
    2. Tavily search
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
    # STEP 1
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
    # STEP 2
    # TAVILY SEARCH
    # =====================================

    try:

        tavily_data = search_investor(
            investor_name
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

    website_content = investor.get(
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
    # STEP 5
    # ENTITY TYPE
    # =====================================

    enriched_investor[
        "entity_type"
    ] = investor.get(
        "entity_type",
        "investor"
    )

    # =====================================
    # STEP 6
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
    # STEP 7
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
    # STEP 8
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
        )
    }

    return enriched_investor


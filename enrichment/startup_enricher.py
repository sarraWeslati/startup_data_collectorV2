from datetime import datetime

from enrichment.website_enricher import (
    enrich_from_website
)

from enrichment.tavily_client import (
    search_startup,
    build_enrichment_package
)

from enrichment.llm_enricher import (
    enrich_startup_with_llm
)

from utils.confidence_score import (
    compute_confidence_score
)

from validators.entity_validator import (
    validate_entity
)

async def enrich_startup(
    startup: dict
) -> dict:
    """
    Startup enrichment pipeline

    1. Website enrichment
    2. Tavily Search
    3. LLM enrichment
    4. Metadata
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
    # TAVILY SEARCH
    # =====================================

    tavily_data = {}

    package = {}

    try:

        tavily_data = search_startup(
            startup_name
        )

        if not isinstance(
            tavily_data,
            dict
        ):

            tavily_data = {}

        package = build_enrichment_package(
            tavily_data
        )

    except Exception as e:

        print(
            f"[TAVILY ERROR] {e}"
        )

        tavily_data = {}

        package = {}
            # =====================================
    # APPLY TAVILY ENRICHMENT
    # =====================================

    if (
        package.get("website")
        and not startup.get("website")
    ):

        startup["website"] = (
            package["website"]
        )

    if (
        package.get("linkedin")
        and not startup.get("linkedin")
    ):

        startup["linkedin"] = (
            package["linkedin"]
        )

    startup["external_profiles"] = {

        "website":
        package.get("website"),

        "linkedin":
        package.get("linkedin"),

        "crunchbase":
        package.get("crunchbase"),

        "wellfound":
        package.get("wellfound"),

        "github":
        package.get("github"),

        "dealroom":
        package.get("dealroom"),

        "pitchbook":
        package.get("pitchbook"),

        "startupblink":
        package.get("startupblink")
    }

    existing_socials = startup.get(
        "social_media",
        {}
    )

    if not isinstance(
        existing_socials,
        dict
    ):

        existing_socials = {}

    for platform, url in package.get(
        "social_media",
        {}
    ).items():

        if (
            url
            and not existing_socials.get(
                platform
            )
        ):

            existing_socials[
                platform
            ] = url

    startup[
        "social_media"
    ] = existing_socials
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

        enriched_startup = startup
            # =====================================
    # PRESERVE TAVILY DATA
    # =====================================

    if (
        package.get("website")
        and not enriched_startup.get("website")
    ):

        enriched_startup["website"] = (
            package["website"]
        )

    if (
        package.get("linkedin")
        and not enriched_startup.get("linkedin")
    ):

        enriched_startup["linkedin"] = (
            package["linkedin"]
        )

    existing_socials = enriched_startup.get(
        "social_media",
        {}
    )

    if not isinstance(
        existing_socials,
        dict
    ):

        existing_socials = {}

    for platform, url in package.get(
        "social_media",
        {}
    ).items():

        if (
            url
            and not existing_socials.get(
                platform
            )
        ):

            existing_socials[
                platform
            ] = url

    enriched_startup[
        "social_media"
    ] = existing_socials

    enriched_startup[
        "external_profiles"
    ] = {

        "website":
        package.get("website"),

        "linkedin":
        package.get("linkedin"),

        "crunchbase":
        package.get("crunchbase"),

        "wellfound":
        package.get("wellfound"),

        "github":
        package.get("github"),

        "dealroom":
        package.get("dealroom"),

        "pitchbook":
        package.get("pitchbook"),

        "startupblink":
        package.get("startupblink")
    }
        # =====================================
    # ENTITY TYPE
    # =====================================

    enriched_startup["entity_type"] = (
        startup.get(
            "entity_type",
            "startup"
        )
    )

    # =====================================
    # ENRICHMENT METADATA
    # =====================================

    enriched_startup["enrichment"] = {

        "status":
        "completed",

        "sources": [
            "website",
            "tavily",
            "llm"
        ],

        "date":
        datetime.utcnow().isoformat(),

        "website_enriched":
        bool(
            startup.get(
                "website_content"
            )
        ),

        "tavily_results":
        package.get(
            "results_count",
            0
        ),

        "llm_enriched":
        True
    }

    # =====================================
    # TAVILY METADATA
    # =====================================

    enriched_startup["tavily"] = {

        "query":
        startup_name,

        "answer":
        package.get(
            "answer",
            ""
        ),

        "results_count":
        package.get(
            "results_count",
            0
        ),

        "urls":
        package.get(
            "urls",
            []
        )
    }
        # =====================================
    # STATS
    # =====================================

    enriched_startup["stats"] = {

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

        "has_crunchbase":
        bool(
            enriched_startup.get(
                "external_profiles",
                {}
            ).get(
                "crunchbase"
            )
        ),

        "has_wellfound":
        bool(
            enriched_startup.get(
                "external_profiles",
                {}
            ).get(
                "wellfound"
            )
        ),

        "has_github":
        bool(
            enriched_startup.get(
                "external_profiles",
                {}
            ).get(
                "github"
            )
        ),

        "founders_count":
        len(
            enriched_startup.get(
                "founders",
                []
            )
        ),

        "team_members_count":
        len(
            enriched_startup.get(
                "team_members",
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
        ),

        "partners_count":
        len(
            enriched_startup.get(
                "partners",
                []
            )
        ),

        "awards_count":
        len(
            enriched_startup.get(
                "awards",
                []
            )
        ),

        "social_profiles":
        len(
            [
                url
                for url in enriched_startup.get(
                    "social_media",
                    {}
                ).values()
                if url
            ]
        )
    }

    # =====================================
    # VALIDATION
    # =====================================

    enriched_startup = validate_entity(
        enriched_startup
    )

    # =====================================
    # CONFIDENCE SCORE
    # =====================================

    enriched_startup["confidence"] = (
        compute_confidence_score(
            enriched_startup
        )
    )
    return enriched_startup
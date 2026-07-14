from datetime import (datetime, UTC)

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

from enrichment.investor_search import (
    search_startup_investors
)

from utils.confidence_score import (
    compute_confidence_score
)

from utils.website_resolver import resolve_official_website
from validators.entity_validator import (
    validate_entity
)
from utils.entity_merger import (
    merge_entities
)

async def enrich_startup(
    startup: dict
) -> dict:
    """
    Complete startup enrichment pipeline.

    Steps

    1. Tavily Search
    2. Website Resolution
    3. Website Enrichment
    4. Investor Search
    5. LLM Enrichment
    6. Validation
    7. Confidence Score
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
    # TAVILY SEARCH
    # =====================================

    tavily_data = {}
    investors_data = {}
    package = {}

    # -------------------------
    # Recherche startup
    # -------------------------

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
            f"[TAVILY STARTUP ERROR] {e}"
        )

        tavily_data = {}

    # =====================================================
    # BUILD ENRICHMENT PACKAGE
    # =====================================================

    package = build_enrichment_package(

        startup_name,

        tavily_data

    )

    if not isinstance(
        package,
        dict
    ):

        package = {}

    # =====================================================
    # BUILD WEBSITE CANDIDATES
    # =====================================================

    candidate_urls = []

    # -----------------------------------------------------
    # Existing website
    # -----------------------------------------------------

    website = startup.get(
        "website"
    )

    if website:

        candidate_urls.append(
            website
        )

    # -----------------------------------------------------
    # Package main website
    # -----------------------------------------------------

    website = package.get(
        "website"
    )

    if website:

        candidate_urls.append(
            website
        )

    # -----------------------------------------------------
    # LinkedIn
    # -----------------------------------------------------

    linkedin = package.get(
        "linkedin"
    )

    if linkedin:

        candidate_urls.append(
            linkedin
        )

    # -----------------------------------------------------
    # External profiles
    # -----------------------------------------------------

    for key in [

        "crunchbase",

        "wellfound",

        "github",

        "dealroom",

        "pitchbook",

        "startupblink"

    ]:

        url = package.get(
            key
        )

        if url:

            candidate_urls.append(
                url
            )

    # -----------------------------------------------------
    # Tavily URLs
    # -----------------------------------------------------

    candidate_urls.extend(

        package.get(
            "urls",
            []
        )

    )

    # -----------------------------------------------------
    # Remove duplicates
    # -----------------------------------------------------

    candidate_urls = [

        url

        for url in dict.fromkeys(
            candidate_urls
        )

        if url

    ]

    # =====================================================
    # RESOLVE OFFICIAL WEBSITE
    # =====================================================

    website_candidate = resolve_official_website(

        company_name=startup_name,

        urls=candidate_urls

    )

    if website_candidate:

        print(
            f"[OFFICIAL WEBSITE] {website_candidate}"
        )

        startup["official_website"] = website_candidate

        startup["website"] = website_candidate

    else:

        print(
            "[OFFICIAL WEBSITE] Not found."
        )

    startup["website_candidates"] = candidate_urls


    # =====================================================
    # WEBSITE ENRICHMENT
    # =====================================================

    if startup.get("website"):

        try:

            startup = await enrich_from_website(
                startup
            )

        except Exception as e:

            print(
                f"[WEBSITE ERROR] {e}"
            )

    else:

        print(
            "[WEBSITE ENRICHMENT] No website available."
        )

    # -------------------------
    # Recherche investisseurs
    # -------------------------

    try:

        investors_data = search_startup_investors(
            startup_name
        )

    except Exception as e:

        print(
            f"[TAVILY INVESTORS ERROR] {e}"
        )

        investors_data = {}
    # =====================================================
    # APPLY TAVILY ENRICHMENT
    # =====================================================

    startup = merge_entities(

        startup,

        {

            "linkedin": package.get(
                "linkedin"
            ),

            "external_profiles": {

                "official_website": startup.get(
                    "official_website"
                ),

                "website": package.get(
                    "website"
                ),

                "linkedin": package.get(
                    "linkedin"
                ),

                "crunchbase": package.get(
                    "crunchbase"
                ),

                "wellfound": package.get(
                    "wellfound"
                ),

                "github": package.get(
                    "github"
                ),

                "dealroom": package.get(
                    "dealroom"
                ),

                "pitchbook": package.get(
                    "pitchbook"
                ),

                "startupblink": package.get(
                    "startupblink"
                )

            }

        }

    )

    # =====================================================
    # SOCIAL MEDIA MERGING
    # =====================================================

    startup = merge_entities(

        startup,

        {

            "social_media":

            package.get(
                "social_media",
                {}
            )

        }

    )

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

    # =====================================================
    # LLM ENRICHMENT
    # =====================================================

    if (

        startup.get("website")

        or package.get("results_count", 0) > 0

    ):

        enriched_startup = await enrich_startup_with_llm(

            startup,

            package,

            investors_data

        )

    else:

        print(
            "[LLM] Skipped (no search data available)."
        )

        enriched_startup = startup
    
     # =====================================================
    # PRESERVE TAVILY DATA
    # =====================================================

    enriched_startup = merge_entities(

        enriched_startup,

        {

            "official_website": startup.get(
                "official_website"
            ),

            "website_candidates": startup.get(
                "website_candidates",
                []
            ),

            "linkedin": package.get(
                "linkedin"
            ),

            "social_media": package.get(
                "social_media",
                {}
            ),

            "external_profiles": {

                "official_website": startup.get(
                    "official_website"
                ),

                "website": package.get(
                    "website"
                ),

                "linkedin": package.get(
                    "linkedin"
                ),

                "crunchbase": package.get(
                    "crunchbase"
                ),

                "wellfound": package.get(
                    "wellfound"
                ),

                "github": package.get(
                    "github"
                ),

                "dealroom": package.get(
                    "dealroom"
                ),

                "pitchbook": package.get(
                    "pitchbook"
                ),

                "startupblink": package.get(
                    "startupblink"
                )

            }

        }

    )
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

    enriched_startup = merge_entities(

        enriched_startup,

        {

            "enrichment": {

                "status": "completed",

                "sources": [

                    "website",

                    "tavily",

                    "llm"

                ],

                "date": datetime.now(UTC).isoformat(),

                "website_enriched": bool(

                    startup.get(
                        "website_content"
                    )

                ),

                "tavily_results": package.get(

                    "results_count",

                    0

                ),

                "llm_enriched": True

            }

        }

    )

    # =====================================
    # TAVILY METADATA
    # =====================================

    enriched_startup = merge_entities(

        enriched_startup,

        {

            "tavily": {

                "query": startup_name,

                "answer": package.get(
                    "answer",
                    ""
                ),

                "results_count": package.get(
                    "results_count",
                    0
                ),

                "official_website": startup.get(
                    "official_website"
                ),

                "candidate_urls": startup.get(
                    "website_candidates",
                    []
                ),

                "urls": package.get(
                    "urls",
                    []
                )

            }

        }

    )

    # =====================================
    # STATS
    # =====================================

    enriched_startup = merge_entities(

        enriched_startup,

        {

            "stats": {

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

        }

    )

    # =====================================
    # FINAL MERGE
    # =====================================

    enriched_startup = merge_entities(

        startup,

        enriched_startup

    )

    # =====================================
    # VALIDATION
    # =====================================

    enriched_startup = validate_entity(
        enriched_startup
    )

    # =====================================
    # CONFIDENCE
    # =====================================

    enriched_startup["confidence"] = (
        compute_confidence_score(
            enriched_startup
        )
    )

    return enriched_startup



# =====================================================
# TEST
# =====================================================

import asyncio
import json


async def test():

    startup = {

        "name": "2BK Innovation",

        "entity_type": "startup"

    }

    result = await enrich_startup(
        startup
    )

    print("\n")
    print("=" * 80)
    print("RESULT")
    print("=" * 80)

    print(

        json.dumps(

            result,

            indent=4,

            ensure_ascii=False

        )

    )


if __name__ == "__main__":

    asyncio.run(
        test()
    )
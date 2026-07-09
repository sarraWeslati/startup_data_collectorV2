# enrichment/investor_enricher.py
from datetime import (
    datetime,
    timezone
)

from enrichment.website_enricher import (
    enrich_from_website
)

from enrichment.tavily_client import (
    search_investor,
    build_enrichment_package
)

from enrichment.llm_enricher import (
    enrich_investor_with_llm
)

from utils.website_resolver import (
    resolve_official_website
)

from validators.entity_validator import (
    validate_entity
)

from utils.confidence_score import (
    compute_confidence_score
)

from utils.entity_merger import (
    merge_entities,
    merge_dicts
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

    

    

    # =====================================
    # TAVILY SEARCH
    # =====================================

    tavily_data = {}

    package = {}

    try:

        tavily_data = search_investor(
            investor_name
        )

        if not isinstance(
            tavily_data,
            dict
        ):

            tavily_data = {}

        package = build_enrichment_package(
            investor_name,
            tavily_data
        )

        website_candidate = resolve_official_website(

            investor.get(
                "website",
                ""
            ),

            package.get(
                "website",
                ""
            )

        )

        investor = merge_entities(

            investor,

            {

                "website": website_candidate

            }

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
        and not investor.get("website")
    ):

        investor["website"] = (
            package["website"]
        )

    if (
        package.get("linkedin")
        and not investor.get("linkedin")
    ):

        investor["linkedin"] = (
            package["linkedin"]
        )

    # =====================================
    # EXTERNAL PROFILES
    # =====================================

    investor = merge_entities(

        investor,

        {

            "external_profiles": {

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

        }

    )

    # =====================================
    # SOCIAL MEDIA
    # =====================================

    investor = merge_entities(

        investor,

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

    llm_success = False
    try:

        enriched_investor = (
            enrich_investor_with_llm(
                investor=investor,
                tavily_data=tavily_data,
                website_content=website_content
            )
        )

        llm_success = True

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

        enriched_investor = investor

    # =====================================
    # PRESERVE TAVILY DATA
    # =====================================

    if (
        package.get("website")
        and not enriched_investor.get(
            "website"
        )
    ):

        enriched_investor["website"] = (
            package["website"]
        )

    if (
        package.get("linkedin")
        and not enriched_investor.get(
            "linkedin"
        )
    ):

        enriched_investor["linkedin"] = (
            package["linkedin"]
        )

    existing_socials = enriched_investor.get(
        "social_media"
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

    enriched_investor[
        "social_media"
    ] = existing_socials

    external_profiles = {

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

    enriched_investor[
        "external_profiles"
    ] = external_profiles

    
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

    enriched_investor = merge_entities(

        enriched_investor,

        {

            "enrichment": {

                "status": "completed",

                "sources": [

                    "website",

                    "tavily",

                    "llm"

                ],

                "date": datetime.utcnow().isoformat(),

                "website_enriched": bool(

                    investor.get(
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

    enriched_investor = merge_entities(

        enriched_investor,

        {

            "tavily": {

                "query":
                investor_name,

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

        }

    )

    # =====================================
    # STATS
    # =====================================

    enriched_investor = merge_entities(

        enriched_investor,

        {

            "stats": {

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

                    or

                    enriched_investor.get(
                        "social_media",
                        {}
                    ).get(
                        "linkedin"
                    )

                ),

                "has_crunchbase":
                bool(

                    enriched_investor.get(
                        "external_profiles",
                        {}
                    ).get(
                        "crunchbase"
                    )

                ),

                "has_wellfound":
                bool(

                    enriched_investor.get(
                        "external_profiles",
                        {}
                    ).get(
                        "wellfound"
                    )

                ),

                "has_github":
                bool(

                    enriched_investor.get(
                        "external_profiles",
                        {}
                    ).get(
                        "github"
                    )

                ),

                "has_dealroom":
                bool(

                    enriched_investor.get(
                        "external_profiles",
                        {}
                    ).get(
                        "dealroom"
                    )

                ),

                "has_pitchbook":
                bool(

                    enriched_investor.get(
                        "external_profiles",
                        {}
                    ).get(
                        "pitchbook"
                    )

                ),

                "portfolio_count":
                len(

                    enriched_investor.get(
                        "portfolio_startups",
                        []
                    )

                ),

                "investment_focus_count":
                len(

                    enriched_investor.get(
                        "investment_focus",
                        []
                    )

                ),

                "investment_stages_count":
                len(

                    enriched_investor.get(
                        "investment_stages",
                        []
                    )

                ),

                "geographic_focus_count":
                len(

                    enriched_investor.get(
                        "geographic_focus",
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

                ),

                "social_profiles":
                len(

                    [

                        url

                        for url in enriched_investor.get(
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

    enriched_investor = merge_entities(

        investor,

        enriched_investor

    )

    # =====================================
    # VALIDATION
    # =====================================

    enriched_investor = validate_entity(

        enriched_investor

    )

    # =====================================
    # CONFIDENCE SCORE
    # =====================================

    enriched_investor["confidence"] = (

        compute_confidence_score(

            enriched_investor

        )

    )

    return enriched_investor
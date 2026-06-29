from typing import Dict

from utils.african_countries import (
    is_african_startup
)

from utils.entity_matcher import (
    is_matching_company
)


def validate_entity(
    entity: Dict
) -> Dict:
    """
    Valide une entité enrichie.
    """

    validation = {}

    # --------------------------
    # Africa
    # --------------------------

    validation["is_african"] = (
        is_african_startup(entity)
    )

    # --------------------------
    # Website
    # --------------------------

    website = entity.get(
        "website",
        ""
    )

    validation["website_matches"] = (
        is_matching_company(
            entity.get(
                "name",
                ""
            ),
            website
        )
    )

    entity["validation"] = validation

    return entity
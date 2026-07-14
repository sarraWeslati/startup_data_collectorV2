from typing import Dict
from typing import List

from etl.deduplicators.startup_deduplicator import (
    deduplicate_startups
)

from etl.deduplicators.investor_deduplicator import (
    deduplicate_investors
)


# =====================================================
# DEDUPLICATE STARTUPS
# =====================================================

def deduplicate_startup_entities(
    startups: List[Dict]
) -> List[Dict]:

    return deduplicate_startups(
        startups
    )


# =====================================================
# DEDUPLICATE INVESTORS
# =====================================================

def deduplicate_investor_entities(
    investors: List[Dict]
) -> List[Dict]:

    return deduplicate_investors(
        investors
    )


# =====================================================
# DEDUPLICATE ALL
# =====================================================

def deduplicate_entities(
    entities: Dict[str, List[Dict]]
) -> Dict[str, List[Dict]]:
    """
    Déduplique toutes les entités.
    """

    startups = deduplicate_startup_entities(

        entities.get(
            "startups",
            []
        )

    )

    investors = deduplicate_investor_entities(

        entities.get(
            "investors",
            []
        )

    )

    return {

        "startups": startups,

        "investors": investors

    }
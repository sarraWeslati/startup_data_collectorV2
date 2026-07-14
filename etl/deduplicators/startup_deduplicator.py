from typing import Dict
from typing import List

from etl.deduplicators.common import (
    is_duplicate,
    merge_duplicate
)


# =====================================================
# STARTUP DEDUPLICATOR
# =====================================================

def deduplicate_startups(
    startups: List[Dict]
) -> List[Dict]:
    """
    Détecte et fusionne les startups
    dupliquées.
    """

    merged = []

    for startup in startups:

        duplicate_found = False

        for index, existing in enumerate(
            merged
        ):

            if is_duplicate(
                startup,
                existing
            ):

                merged[index] = merge_duplicate(

                    existing,

                    startup

                )

                duplicate_found = True

                break

        if not duplicate_found:

            merged.append(
                startup
            )

    return merged
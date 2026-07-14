from typing import Dict
from typing import List

from etl.deduplicators.common import (
    is_duplicate,
    merge_duplicate
)


# =====================================================
# INVESTOR DEDUPLICATOR
# =====================================================

def deduplicate_investors(
    investors: List[Dict]
) -> List[Dict]:
    """
    Détecte et fusionne les investisseurs
    dupliqués.
    """

    merged = []

    for investor in investors:

        duplicate_found = False

        for index, existing in enumerate(
            merged
        ):

            if is_duplicate(
                investor,
                existing
            ):

                merged[index] = merge_duplicate(

                    existing,

                    investor

                )

                duplicate_found = True

                break

        if not duplicate_found:

            merged.append(
                investor
            )

    return merged
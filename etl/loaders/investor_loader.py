# etl/loaders/investor_loader.py

from typing import Dict
from typing import List

from pymongo.database import Database

from etl.config import (
    INVESTORS_COLLECTION
)

from etl.loaders.common import (
    upsert_entity
)


# =====================================================
# INVESTOR LOADER
# =====================================================

def load_investors(
    database: Database,
    investors: List[Dict]
) -> Dict:
    """
    Charge tous les investisseurs
    dans MongoDB.
    """

    collection = database[
        INVESTORS_COLLECTION
    ]

    print("\n")
    print("=" * 60)
    print("LOADING INVESTORS")
    print("=" * 60)

    print(
        f"Total investors : {len(investors)}"
    )

    inserted = 0
    updated = 0
    skipped = 0

    for investor in investors:

        status = upsert_entity(

            collection,

            investor

        )

        if status == "inserted":

            inserted += 1

        elif status == "updated":

            updated += 1

        else:

            skipped += 1

    print( f"Loading : {investor.get('name')}")

    print()

    print(
        f"Inserted : {inserted}"
    )

    print(
        f"Updated : {updated}"
    )

    print(
        f"Skipped : {skipped}"
    )

    return {

        "inserted": inserted,

        "updated": updated,

        "skipped": skipped

    }
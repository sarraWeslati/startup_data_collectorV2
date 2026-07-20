# etl/loaders/startup_loader.py

from typing import Dict
from typing import List

from pymongo.database import Database

from etl.config import (
    STARTUPS_COLLECTION
)

from etl.loaders.common import (
    upsert_entity
)


# =====================================================
# STARTUP LOADER
# =====================================================

def load_startups(
    database: Database,
    startups: List[Dict]
) -> Dict:
    """
    Charge toutes les startups dans MongoDB.
    """

    collection = database[
        STARTUPS_COLLECTION
    ]

    print("\n")
    print("=" * 60)
    print("LOADING STARTUPS")
    print("=" * 60)

    print(
        f"Total startups : {len(startups)}"
    )

    inserted = 0
    updated = 0
    skipped = 0

    for startup in startups:

        status = upsert_entity(

            collection,

            startup

        )

        if status == "inserted":

            inserted += 1

        elif status == "updated":

            updated += 1

        else:

            skipped += 1

    print(f"Loading : {startups.get('name')}")

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
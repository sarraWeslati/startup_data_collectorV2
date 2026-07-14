# etl/mongodb_loader.py

from typing import Dict

from pymongo import MongoClient

from etl.config import (
    DATABASE_NAME
)

from etl.loaders.startup_loader import (
    load_startups
)

from etl.loaders.investor_loader import (
    load_investors
)


# =====================================================
# MONGODB LOADER
# =====================================================

def load_to_mongodb(
    client: MongoClient,
    entities: Dict
) -> Dict:
    """
    Charge toutes les entités dans MongoDB.
    """

    database = client[
        DATABASE_NAME
    ]

    startup_result = load_startups(

        database,

        entities.get(
            "startups",
            []
        )

    )

    investor_result = load_investors(

        database,

        entities.get(
            "investors",
            []
        )

    )

    return {

        "startups": startup_result,

        "investors": investor_result

    }
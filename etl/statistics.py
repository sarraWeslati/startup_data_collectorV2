# etl/statistics.py

from datetime import datetime
from typing import Dict


# =====================================================
# ETL STATISTICS
# =====================================================

class ETLStatistics:
    """
    Collecte toutes les statistiques
    du pipeline ETL.
    """

    def __init__(self):

        self.start_time = datetime.now()

        self.stats = {

            "extract": {

                "startups": 0,

                "investors": 0

            },

            "transform": {

                "startups": 0,

                "investors": 0

            },

            "validate": {

                "valid": 0,

                "rejected": 0

            },

            "deduplicate": {

                "before": 0,

                "after": 0

            },

            "load": {

                "inserted": 0,

                "updated": 0,

                "skipped": 0

            }

        }

    # =================================================

    def set_extract(

        self,

        startups: int,

        investors: int

    ):

        self.stats["extract"]["startups"] = startups

        self.stats["extract"]["investors"] = investors

    # =================================================

    def set_transform(

        self,

        startups: int,

        investors: int

    ):

        self.stats["transform"]["startups"] = startups

        self.stats["transform"]["investors"] = investors

    # =================================================

    def set_validation(

        self,

        valid: int,

        rejected: int

    ):

        self.stats["validate"]["valid"] = valid

        self.stats["validate"]["rejected"] = rejected

    # =================================================

    def set_deduplication(

        self,

        before: int,

        after: int

    ):

        self.stats["deduplicate"]["before"] = before

        self.stats["deduplicate"]["after"] = after

    # =================================================

    def set_loading(

        self,

        inserted: int,

        updated: int,

        skipped: int

    ):

        self.stats["load"]["inserted"] = inserted

        self.stats["load"]["updated"] = updated

        self.stats["load"]["skipped"] = skipped

    # =================================================

    def report(self):

        elapsed = (

            datetime.now()

            - self.start_time

        ).total_seconds()

        print("\n")
        print("=" * 80)
        print("ETL REPORT")
        print("=" * 80)

        print("\nEXTRACT")

        print(

            f"  Startups   : {self.stats['extract']['startups']}"

        )

        print(

            f"  Investors  : {self.stats['extract']['investors']}"

        )

        print("\nTRANSFORM")

        print(

            f"  Startups   : {self.stats['transform']['startups']}"

        )

        print(

            f"  Investors  : {self.stats['transform']['investors']}"

        )

        print("\nVALIDATION")

        print(

            f"  Valid      : {self.stats['validate']['valid']}"

        )

        print(

            f"  Rejected   : {self.stats['validate']['rejected']}"

        )

        print("\nDEDUPLICATION")

        print(

            f"  Before     : {self.stats['deduplicate']['before']}"

        )

        print(

            f"  After      : {self.stats['deduplicate']['after']}"

        )

        print("\nMONGODB")

        print(

            f"  Inserted   : {self.stats['load']['inserted']}"

        )

        print(

            f"  Updated    : {self.stats['load']['updated']}"

        )

        print(

            f"  Skipped    : {self.stats['load']['skipped']}"

        )

        print("\n")

        print(

            f"Duration : {elapsed:.2f}s"

        )

        print("=" * 80)

        return self.stats
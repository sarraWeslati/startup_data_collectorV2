# etl/main_etl.py

#from pymongo import MongoClient

from etl.extractor import (
    load_entities
)

from etl.transformer import (
    transform_entities
)

from etl.validator import (
    validate_entities
)

from etl.deduplicator import (
    deduplicate_entities
)

#from etl.mongodb_loader import (
 #   load_to_mongodb
#)

from etl.statistics import (
    ETLStatistics
)

#from etl.config import (
 #   MONGO_URI
#)

from etl.file_storage import (
    save_transformed_entities,
    save_validated_entities
)

from etl.file_storage import (
        save_rejected_entities
    )

from etl.file_storage import (
        save_deduplicated_entities
    )

from etl.file_storage import (
        save_etl_report
    )

# =====================================================
# MAIN
# =====================================================

def main():

    stats = ETLStatistics()

    print("\n")
    print("=" * 80)
    print("ETL PIPELINE")
    print("=" * 80)

    # =================================================
    # EXTRACT
    # =================================================

    entities = load_entities()

    stats.set_extract(

        len(
            entities["startups"]
        ),

        len(
            entities["investors"]
        )

    )

    # =================================================
    # TRANSFORM
    # =================================================

    startups = transform_entities(

        entities["startups"]

    )

    investors = transform_entities(

        entities["investors"]

    )

    stats.set_transform(

        len(startups),

        len(investors)

    )

    entities = {

        "startups": startups,

        "investors": investors

    }

    # save transformed entities to file storage

    save_transformed_entities(entities)

    # =================================================
    # VALIDATE
    # =================================================

    validated = {

        "startups": validate_entities(

            entities["startups"]

        ),

        "investors": validate_entities(

            entities["investors"]

        )

    }

    valid_entities = {

        "startups":

            validated["startups"]["valid_entities"],

        "investors":

            validated["investors"]["valid_entities"]

    }

    save_validated_entities(valid_entities)

    rejected = (

        len(

            validated["startups"]["rejected_entities"]

        )

        +

        len(

            validated["investors"]["rejected_entities"]

        )

    )

    valid = (

        len(

            valid_entities["startups"]

        )

        +

        len(

            valid_entities["investors"]

        )

    )

    stats.set_validation(

        valid,

        rejected

    )

    #save rejected entities to file storage

    save_rejected_entities(validated)

    # =================================================
    # DEDUPLICATE
    # =================================================

    before = (

        len(

            valid_entities["startups"]

        )

        +

        len(

            valid_entities["investors"]

        )

    )

    deduplicated = deduplicate_entities(

        valid_entities

    )

    #save deduplicated entities to file storage

    save_deduplicated_entities(deduplicated)

    after = (

        len(

            deduplicated["startups"]

        )

        +

        len(

            deduplicated["investors"]

        )

    )

    stats.set_deduplication(

        before,

        after

    )

    # =================================================
    # LOAD
    # =================================================

    #client = MongoClient(MONGO_URI)

    #loading = load_to_mongodb(

        #client,

        #deduplicated

    #)

    #stats.set_loading(

        #inserted=(

            #loading["startups"]["inserted"]

            #+

            #loading["investors"]["inserted"]

        #),

        #updated=(

            #loading["startups"]["updated"]

            #+

            #loading["investors"]["updated"]

        #),

        #skipped=(

            #loading["startups"]["skipped"]

            #+

            #loading["investors"]["skipped"]

        #)

    #)

    # =================================================
    # REPORT
    # =================================================

    report = stats.report()

    save_etl_report(report)

    print("\nDone.\n")


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":

    main()
# etl/transformer.py

from typing import Dict
from typing import List

from etl.extractor import load_entities
from etl.transforms.startup_transformer import (
    transform_startup
)

from etl.transforms.investor_transformer import (
    transform_investor
)


def transform_entities(
    entities: List[Dict]
) -> List[Dict]:
    """
    Transforme toutes les entités.
    """

    transformed = []

    for entity in entities:

        entity_type = entity.get(
            "entity_type",
            ""
        )

        if entity_type == "startup":

            transformed.append(

                transform_startup(
                    entity
                )

            )

        elif entity_type in [

            "investor",

            "venture_capital_fund"

        ]:

            transformed.append(

                transform_investor(
                    entity
                )

            )

        else:

            transformed.append(
                entity
            )

    return transformed

entities = load_entities()

startup = entities["startups"][0]

print("BEFORE")
print(startup)

startup = transform_startup(startup)

print("AFTER")
print(startup)
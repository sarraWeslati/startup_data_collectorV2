# etl/validator.py

from typing import Dict
from typing import List

from etl.validators.startup_validator import (
    validate_startup
)

from etl.validators.investor_validator import (
    validate_investor
)


# =====================================================
# VALIDATE ONE ENTITY
# =====================================================

def validate_entity(
    entity: Dict
) -> Dict:
    """
    Valide une seule entité.

    Retourne toujours :

    {
        "valid": bool,
        "errors": list[str]
    }
    """

    entity_type = entity.get(
        "entity_type",
        ""
    )

    errors: List[str] = []

    # ==========================================
    # STARTUP
    # ==========================================

    if entity_type == "startup":

        errors = validate_startup(
            entity
        )

    # ==========================================
    # INVESTOR
    # ==========================================

    elif entity_type in [

        "investor",

        "venture_capital_fund"

    ]:

        errors = validate_investor(
            entity
        )

    # ==========================================
    # UNKNOWN
    # ==========================================

    else:

        errors.append(

            f"Unknown entity_type : {entity_type}"

        )

    return {

        "valid": len(errors) == 0,

        "errors": errors

    }


# =====================================================
# VALIDATE MULTIPLE ENTITIES
# =====================================================

def validate_entities(
    entities: List[Dict]
) -> Dict:
    """
    Valide une liste d'entités.

    Retourne les entités valides,
    les entités rejetées
    et des statistiques.
    """

    valid_entities = []

    rejected_entities = []

    validation_errors = {}

    for entity in entities:

        result = validate_entity(
            entity
        )

        if result["valid"]:

            valid_entities.append(
                entity
            )

        else:

            rejected_entities.append({

                "entity": entity,

                "errors": result["errors"]

            })

            print()

            print("=" * 60)

            print(
                f"Rejected : {entity.get('name', 'Unknown')}"
            )

            for error in result["errors"]:

                print(
                    f"   - {error}"
                )

                validation_errors[error] = (

                    validation_errors.get(
                        error,
                        0
                    )

                    + 1

                )

    print()

    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    for error, count in sorted(

        validation_errors.items(),

        key=lambda item: item[1],

        reverse=True

    ):

        print(
            f"{count:5}  {error}"
        )

    print()

    return {

        "valid_entities": valid_entities,

        "rejected_entities": rejected_entities,

        "statistics": {

            "total": len(entities),

            "valid": len(valid_entities),

            "rejected": len(rejected_entities),

            "error_summary": validation_errors

        }

    }
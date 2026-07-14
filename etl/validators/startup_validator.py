from typing import Dict
from typing import List

from etl.validators.common import (
    validate_required,
    validate_url,
    validate_email,
    validate_list,
    validate_dict
)

from etl.validators.african_validator import (
    is_african_entity
)


# =====================================================
# STARTUP VALIDATOR
# =====================================================

def validate_startup(
    startup: Dict
) -> List[str]:
    """
    Valide une startup.

    Retourne une liste d'erreurs.
    Si la liste est vide,
    la startup est valide.
    """

    errors = []

    # =================================================
    # REQUIRED FIELDS
    # =================================================

    validate_required(
        startup.get("name"),
        "name",
        errors
    )

    validate_required(
        startup.get("entity_type"),
        "entity_type",
        errors
    )

    # =================================================
    # URLS
    # =================================================

    validate_url(
        startup.get("website"),
        "website",
        errors
    )

    validate_url(
        startup.get("linkedin_url"),
        "linkedin_url",
        errors
    )

    # =================================================
    # CONTACT
    # =================================================

    contact = startup.get(
        "contact",
        {}
    )

    validate_dict(
        contact,
        "contact",
        errors
    )

    if isinstance(
        contact,
        dict
    ):

        emails = contact.get(
            "emails",
            []
        )

        validate_list(
            emails,
            "contact.emails",
            errors
        )

        for email in emails:

            validate_email(
                email,
                "contact.emails",
                errors
            )

        validate_list(
            contact.get(
                "phones",
                []
            ),
            "contact.phones",
            errors
        )

    # =================================================
    # LISTS
    # =================================================

    validate_list(
        startup.get(
            "founders",
            []
        ),
        "founders",
        errors
    )

    validate_list(
        startup.get(
            "products",
            []
        ),
        "products",
        errors
    )

    validate_list(
        startup.get(
            "services",
            []
        ),
        "services",
        errors
    )

    validate_list(
        startup.get(
            "technologies",
            []
        ),
        "technologies",
        errors
    )

    validate_list(
        startup.get(
            "industries",
            []
        ),
        "industries",
        errors
    )

    validate_list(
        startup.get(
            "countries",
            []
        ),
        "countries",
        errors
    )

    validate_list(
        startup.get(
            "cities",
            []
        ),
        "cities",
        errors
    )

    # =================================================
    # AFRICAN STARTUP
    # =================================================

    if not is_african_entity(startup):

        errors.append(
            "Startup is not located in Africa."
        )

    return errors
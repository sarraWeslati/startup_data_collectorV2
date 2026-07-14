# etl/validators/investor_validator.py

from typing import Dict
from typing import List

from etl.validators.common import (
    validate_required,
    validate_url,
    validate_email,
    validate_list,
    validate_dict
)

# =====================================================
# AFRICA KEYWORDS
# =====================================================

AFRICA_KEYWORDS = {

    "africa",
    "african",
    "pan-african",
    "sub-saharan",
    "north africa",
    "west africa",
    "east africa",
    "southern africa",
    "central africa",

    "tunisia",
    "morocco",
    "algeria",
    "egypt",
    "nigeria",
    "ghana",
    "kenya",
    "uganda",
    "rwanda",
    "senegal",
    "ivory coast",
    "côte d'ivoire",
    "south africa",
    "cameroon",
    "ethiopia",
    "tanzania"

}

# =====================================================
# INVESTS IN AFRICA
# =====================================================

def invests_in_africa(
    investor: Dict
) -> bool:
    """
    Vérifie si un investisseur
    investit en Afrique.
    """

    fields = []

    # Description
    fields.append(
        investor.get(
            "description",
            ""
        )
    )

    # Focus
    fields.append(
        investor.get(
            "focus",
            ""
        )
    )

    # Thesis
    fields.append(
        investor.get(
            "investment_thesis",
            ""
        )
    )

    # Investment regions
    fields.extend(

        investor.get(
            "investment_regions",
            []
        )

    )

    # Countries
    fields.extend(

        investor.get(
            "countries",
            []
        )

    )

    #target markets
    fields.extend(

        investor.get(
            "target_markets",
            []
        )

    )

    #investment geographies
    fields.extend(
        investor.get(
            "investment_geographies",
            []
        )

    )

    #sectors
    fields.extend(
        investor.get(
            "sectors",
            []
        )

    )

    #portfolio
    portfolio = investor.get(
        "portfolio",
        []
    )
    if isinstance(
        portfolio,
        list
    ):
        for company in portfolio:

            if isinstance(
                company,
                dict
            ):

                fields.extend(
                    company.values()
                    )
            else:

                fields.append(
                    str(company)
                )

    # website content
    fields.append(
        investor.get(
            "website_content",
            ""
        )
    )

    #build searchable text

    text = " ".join(

        str(value)

        for value in fields

        if value

    ).lower()

    return any(

        keyword in text

        for keyword in AFRICA_KEYWORDS

    )

# =====================================================
# INVESTOR VALIDATOR
# =====================================================

def validate_investor(
    investor: Dict
) -> List[str]:
    """
    Valide un investisseur.

    Retourne une liste d'erreurs.
    Une liste vide signifie que
    l'entité est valide.
    """

    errors = []

    # =================================================
    # REQUIRED
    # =================================================

    validate_required(
        investor.get("name"),
        "name",
        errors
    )

    validate_required(
        investor.get("entity_type"),
        "entity_type",
        errors
    )

    # =================================================
    # URLS
    # =================================================

    validate_url(
        investor.get("website"),
        "website",
        errors
    )

    validate_url(
        investor.get("linkedin_url"),
        "linkedin_url",
        errors
    )

    # =================================================
    # CONTACT
    # =================================================

    contact = investor.get(
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
        investor.get(
            "investment_stages",
            []
        ),
        "investment_stages",
        errors
    )

    validate_list(
        investor.get(
            "industries",
            []
        ),
        "industries",
        errors
    )

    validate_list(
        investor.get(
            "countries",
            []
        ),
        "countries",
        errors
    )

    validate_list(
        investor.get(
            "cities",
            []
        ),
        "cities",
        errors
    )

    validate_list(
        investor.get(
            "portfolio",
            []
        ),
        "portfolio",
        errors
    )

    validate_list(
        investor.get(
            "team_members",
            []
        ),
        "team_members",
        errors
    )

    # =================================================
    # AFRICA INVESTMENT
    # =================================================

    if not invests_in_africa(
        investor
    ):

        errors.append(

            "Investor does not appear to invest in Africa."

        )

    return errors
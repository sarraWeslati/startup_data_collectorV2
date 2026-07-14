# etl/transforms/investor_transformer.py

from typing import Dict

from etl.normalizers.country_normalizer import normalize_country
from etl.normalizers.email_normalizer import normalize_entity_emails
from etl.normalizers.phone_normalizer import normalize_phone_numbers
from etl.normalizers.social_normalizer import normalize_entity_socials
from etl.normalizers.website_normalizer import normalize_entity_websites
from utils.url_normalizer import (
    normalize_website
)

from utils.name_normalizer import (
    normalize_name
)

from etl.transforms.common import (
    clone_entity,
    normalize_string,
    normalize_list,
)


# =====================================================
# INVESTOR TRANSFORMER
# =====================================================

def transform_investor(
    investor: Dict
) -> Dict:
    """
    Transforme et normalise un investisseur.

    Cette étape ne modifie jamais
    le JSON original.
    """

    investor = clone_entity(
        investor
    )

    # =================================================
    # NAME
    # =================================================

    if investor.get("name"):

        investor["name"] = normalize_string(
            investor["name"]
        )

        investor["normalized_name"] = normalize_name(
            investor["name"]
        )

    # =================================================
    # WEBSITE
    # =================================================

    if investor.get("website"):

        investor["website"] = normalize_website(
            investor["website"]
        )

    # =================================================
    # LINKEDIN
    # =================================================

    if investor.get("linkedin_url"):

        investor["linkedin_url"] = normalize_website(
            investor["linkedin_url"]
        )

    # =================================================
    # CONTACT
    # =================================================

    contact = investor.get(
        "contact",
        {}
    )

    if isinstance(
        contact,
        dict
    ):

        contact["emails"] = normalize_list(
            contact.get(
                "emails",
                []
            )
        )

        contact["phones"] = normalize_list(
            contact.get(
                "phones",
                []
            )
        )

        investor["contact"] = contact

    # =================================================
    # INVESTMENT STAGES
    # =================================================

    investor["investment_stages"] = normalize_list(
        investor.get(
            "investment_stages",
            []
        )
    )

    # =================================================
    # INDUSTRIES
    # =================================================

    investor["industries"] = normalize_list(
        investor.get(
            "industries",
            []
        )
    )

    # =================================================
    # COUNTRIES
    # =================================================

    investor["countries"] = normalize_list(
        investor.get(
            "countries",
            []
        )
    )

    # =================================================
    # CITIES
    # =================================================

    investor["cities"] = normalize_list(
        investor.get(
            "cities",
            []
        )
    )

    # =================================================
    # PORTFOLIO
    # =================================================

    investor["portfolio"] = normalize_list(
        investor.get(
            "portfolio",
            []
        )
    )

    # =================================================
    # TEAM MEMBERS
    # =================================================

    investor["team_members"] = normalize_list(
        investor.get(
            "team_members",
            []
        )
    )

    # =================================================
    # SOCIAL MEDIA
    # =================================================

    social = investor.get(
        "social_media",
        {}
    )

    if isinstance(
        social,
        dict
    ):

        for key, value in social.items():

            if isinstance(
                value,
                str
            ):

                social[key] = normalize_website(
                    value
                )

        investor["social_media"] = social

    investor = normalize_entity_websites(
        investor
    )

    investor = normalize_entity_socials(
        investor
    )

    investor = normalize_entity_emails(
        investor
    )

    investor = normalize_phone_numbers(
        investor
    )

    investor = normalize_country(
        investor
    )

    return investor
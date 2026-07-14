# etl/transforms/startup_transformer.py

from typing import Dict

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

from etl.normalizers.website_normalizer import (
    normalize_entity_websites
)

from etl.normalizers.social_normalizer import (
    normalize_entity_socials
)

from etl.normalizers.email_normalizer import (
    normalize_entity_emails
)

from etl.normalizers.phone_normalizer import (
    normalize_phone_numbers
)

from etl.normalizers.country_normalizer import (
    normalize_country
)

# =====================================================
# STARTUP TRANSFORMER
# =====================================================

def transform_startup(
    startup: Dict
) -> Dict:
    """
    Transforme et normalise une startup.

    Cette étape ne modifie jamais
    le JSON original.
    """

    startup = clone_entity(
        startup
    )

    # =================================================
    # NAME
    # =================================================

    if startup.get("name"):

        startup["name"] = normalize_string(
            startup["name"]
        )

        startup["normalized_name"] = normalize_name(
            startup["name"]
        )

    # =================================================
    # WEBSITE
    # =================================================

    if startup.get("website"):

        startup["website"] = normalize_website(
            startup["website"]
        )

    # =================================================
    # LINKEDIN
    # =================================================

    if startup.get("linkedin_url"):

        startup["linkedin_url"] = normalize_website(
            startup["linkedin_url"]
        )

    # =================================================
    # CONTACT
    # =================================================

    contact = startup.get(
        "contact",
        {}
    )

    if isinstance(contact, dict):

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

        startup["contact"] = contact

    # =================================================
    # FOUNDERS
    # =================================================

    startup["founders"] = normalize_list(
        startup.get(
            "founders",
            []
        )
    )

    # =================================================
    # PRODUCTS
    # =================================================

    startup["products"] = normalize_list(
        startup.get(
            "products",
            []
        )
    )

    # =================================================
    # SERVICES
    # =================================================

    startup["services"] = normalize_list(
        startup.get(
            "services",
            []
        )
    )

    # =================================================
    # TECHNOLOGIES
    # =================================================

    startup["technologies"] = normalize_list(
        startup.get(
            "technologies",
            []
        )
    )

    # =================================================
    # INDUSTRIES
    # =================================================

    startup["industries"] = normalize_list(
        startup.get(
            "industries",
            []
        )
    )

    # =================================================
    # ADVANCED NORMALIZATION
    # =================================================

    startup = normalize_entity_websites(
        startup
    )

    startup = normalize_entity_socials(
        startup
    )

    startup = normalize_entity_emails(
        startup
)

    startup = normalize_phone_numbers(
        startup
    )

    startup = normalize_country(
        startup
    )

    return startup
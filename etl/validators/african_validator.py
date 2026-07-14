from typing import Dict
from typing import List

from utils.african_countries import AFRICAN_COUNTRIES
from utils.website_resolver import get_domain
from utils.phone_country_codes import (PHONE_COUNTRY_CODES)


def normalize_country(
    country: str
) -> str:

    if not country:
        return ""

    return country.strip().lower()


def is_african_country(
    country: str
) -> bool:

    if not country:
        return False

    return normalize_country(country) in {
        c.lower()
        for c in AFRICAN_COUNTRIES
    }


AFRICAN_TLDS = {

    ".tn",
    ".dz",
    ".ma",
    ".ng",
    ".gh",
    ".ke",
    ".ug",
    ".rw",
    ".za",
    ".ci",
    ".sn",
    ".tz",
    ".et",
    ".cm",
    ".bw",
    ".zm"

}


def has_african_domain(
    website: str
) -> bool:

    if not website:
        return False

    domain = get_domain(website)

    return any(
        domain.endswith(tld)
        for tld in AFRICAN_TLDS
    )

# =====================================================
# PHONE
# =====================================================

def has_african_phone(
    phones: List[str]
) -> bool:
    """
    Vérifie si au moins un numéro
    appartient à un pays africain.
    """

    if not phones:

        return False

    african_codes = {

        code

        for code, country in PHONE_COUNTRY_CODES.items()

        if country in AFRICAN_COUNTRIES

    }

    for phone in phones:

        if not phone:

            continue

        phone = (

            phone

            .replace(" ", "")

            .replace("-", "")

            .replace("(", "")

            .replace(")", "")

        )

        for code in sorted(

            african_codes,

            key=len,

            reverse=True

        ):

            if phone.startswith(code):

                return True

    return False

# =====================================================
# HEADQUARTERS
# =====================================================

def has_african_headquarters(
    headquarters: str
) -> bool:
    """
    Vérifie si le siège contient
    un pays africain.
    """

    if not headquarters:

        return False

    headquarters = headquarters.lower()

    for country in AFRICAN_COUNTRIES:

        if country.lower() in headquarters:

            return True

    return False

def is_african_entity(
    entity: Dict
) -> bool:
    """
    Vérifie si une startup ou un investisseur
    est africain.
    """

    # 1. Validation déjà calculée
    validation = entity.get(
        "validation",
        {}
    )

    if validation.get(
        "is_african"
    ) is True:

        return True

    # 2. Country
    if is_african_country(

        entity.get(
            "country",
            ""
        )

    ):

        return True

    # 3. Headquarters
    if has_african_headquarters(

        entity.get(
            "headquarters",
            ""
        )

    ):

        return True
    
    # 4. Phones
    contact = entity.get(
        "contact",
        {}
    )

    if isinstance(contact, dict):

        phones = contact.get(
            "phones",
            []
        )

        if has_african_phone(
            phones
        ):

            return True
        
    # 5. Operating countries

    operating_countries = entity.get(
        "operating_countries",
        []
    )

    if isinstance(
        operating_countries,
        list
    ):

        for country in operating_countries:

            if is_african_country(
                country
            ):

                return True

    # 6. Website
    if has_african_domain(

        entity.get(
            "website",
            ""
        )

    ):

        return True

    return False
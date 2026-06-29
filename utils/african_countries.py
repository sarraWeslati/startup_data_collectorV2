AFRICAN_COUNTRIES = {

    "Algeria",
    "Angola",
    "Benin",
    "Botswana",
    "Burkina Faso",
    "Burundi",
    "Cameroon",
    "Cape Verde",
    "Central African Republic",
    "Chad",
    "Comoros",
    "Congo",
    "Democratic Republic of the Congo",
    "Djibouti",
    "Egypt",
    "Equatorial Guinea",
    "Eritrea",
    "Eswatini",
    "Ethiopia",
    "Gabon",
    "Gambia",
    "Ghana",
    "Guinea",
    "Guinea-Bissau",
    "Ivory Coast",
    "Côte d'Ivoire",
    "Kenya",
    "Lesotho",
    "Liberia",
    "Libya",
    "Madagascar",
    "Malawi",
    "Mali",
    "Mauritania",
    "Mauritius",
    "Morocco",
    "Mozambique",
    "Namibia",
    "Niger",
    "Nigeria",
    "Rwanda",
    "Senegal",
    "Seychelles",
    "Sierra Leone",
    "Somalia",
    "South Africa",
    "South Sudan",
    "Sudan",
    "Tanzania",
    "Togo",
    "Tunisia",
    "Uganda",
    "Zambia",
    "Zimbabwe"

}

from typing import Dict

from utils.african_countries import (
    AFRICAN_COUNTRIES
)


def normalize_country(
    country: str
) -> str:
    """
    Normalise le nom d'un pays.
    """

    if not country:
        return ""

    return (
        country
        .strip()
        .lower()
    )


def is_african_country(
    country: str
) -> bool:
    """
    Vérifie si un pays appartient
    au continent africain.
    """

    if not country:
        return False

    normalized = normalize_country(
        country
    )

    return normalized in {

        c.lower()

        for c in AFRICAN_COUNTRIES

    }


def is_african_startup(
    startup: Dict
) -> bool:
    """
    Vérifie si une startup est africaine.
    """

    return is_african_country(

        startup.get(
            "country",
            ""
        )

    )
# etl/normalizers/country_normalizer.py
import re
from dataclasses import dataclass
from typing import Dict, List, Optional
from collections import Counter

from urllib.parse import urlparse

from utils.african_countries import AFRICAN_COUNTRIES
from utils.phone_country_codes import PHONE_COUNTRY_CODES
from utils.african_locations import (
    AFRICAN_LOCATIONS
)

# =====================================================
# COUNTRY ALIASES
# =====================================================

COUNTRY_ALIASES = {

    # Tunisia
    "tunisie": "Tunisia",
    "tn": "Tunisia",

    # Algeria
    "algérie": "Algeria",
    "algerie": "Algeria",
    "dz": "Algeria",

    # Morocco
    "maroc": "Morocco",
    "ma": "Morocco",

    # Côte d'Ivoire
    "ivory coast": "Côte d'Ivoire",
    "côte d'ivoire": "Côte d'Ivoire",
    "cote d'ivoire": "Côte d'Ivoire",

    # South Africa
    "south africa": "South Africa",
    "rsa": "South Africa",

    # Egypt
    "egypte": "Egypt",

    # Nigeria
    "ng": "Nigeria",

    # Kenya
    "ke": "Kenya",

    # Ghana
    "gh": "Ghana",

    # Senegal
    "sn": "Senegal"

}


# =====================================================
# WEBSITE TLD
# =====================================================

TLD_COUNTRIES = {

    ".tn": "Tunisia",

    ".dz": "Algeria",

    ".ma": "Morocco",

    ".ng": "Nigeria",

    ".gh": "Ghana",

    ".ke": "Kenya",

    ".ug": "Uganda",

    ".rw": "Rwanda",

    ".za": "South Africa",

    ".ci": "Côte d'Ivoire",

    ".sn": "Senegal",

    ".tz": "Tanzania",

    ".et": "Ethiopia",

    ".cm": "Cameroon",

    ".cv": "Cape Verde"

}


# =====================================================
# CONFIDENCE
# =====================================================

COUNTRY_CONFIDENCE = {

    "country": 1.00,

    "phone": 0.95,

    "headquarters": 0.90,

    "operating": 0.85,

    "domain": 0.80,

    "website_content": 0.60

}


# =====================================================
# COUNTRY CANDIDATE
# =====================================================

@dataclass
class CountryCandidate:

    country: str

    source: str

    confidence: float

# =====================================================
# NORMALIZE COUNTRY NAME
# =====================================================

def normalize_country_name(
    country: str
) -> str:
    """
    Normalise le nom d'un pays.

    Exemples :

    tunisie -> Tunisia

    TN -> Tunisia

    maroc -> Morocco
    """

    if not country:

        return ""

    country = str(country).strip()

    if not country:

        return ""

    lower = country.lower()

    if lower in COUNTRY_ALIASES:

        return COUNTRY_ALIASES[lower]

    return country.title()



# =====================================================
# COUNTRY FROM HEADQUARTERS
# =====================================================

def detect_country_from_headquarters(
    headquarters: str
) -> str:

    if not headquarters:

        return ""

    headquarters = headquarters.lower()

    for country in AFRICAN_COUNTRIES:

        if country.lower() in headquarters:

            return country

    return ""

# =====================================================
# IS AFRICAN COUNTRY
# =====================================================

def is_african_country(
    country: str
) -> bool:
    """
    Vérifie si un pays appartient
    au continent africain.
    """

    if not country:

        return False

    country = normalize_country_name(
        country
    )

    return country in AFRICAN_COUNTRIES


# =====================================================
# ADD CANDIDATE
# =====================================================

def add_candidate(
    candidates: List[CountryCandidate],
    country: str,
    source: str
) -> None:
    """
    Ajoute un candidat si le pays est valide.
    """

    if not country:

        return

    country = normalize_country_name(
        country
    )

    if not is_african_country(
        country
    ):

        return

    candidates.append(

        CountryCandidate(

            country=country,

            source=source,

            confidence=COUNTRY_CONFIDENCE[source]

        )

    )


# =====================================================
# BEST COUNTRY
# =====================================================

def get_best_country(
    candidates: List[CountryCandidate]
) -> Optional[CountryCandidate]:
    """
    Retourne le candidat ayant
    la meilleure confiance.
    """

    if not candidates:
        return None

    scores = {}

    for candidate in candidates:

        if candidate.country not in scores:

            scores[candidate.country] = {

                "score": 0,

                "best": candidate

            }

        scores[candidate.country]["score"] += candidate.confidence

        if (
            candidate.confidence
            >
            scores[candidate.country]["best"].confidence
        ):

            scores[candidate.country]["best"] = candidate

    best = max(

        scores.values(),

        key=lambda value: value["score"]

    )

    return best["best"]


# =====================================================
# COUNTRY REPORT
# =====================================================

def build_country_report(
    candidates: List[CountryCandidate]
) -> Dict:
    """
    Génère un rapport ETL.
    """

    return {

        "count": len(candidates),

        "candidates": [

            {

                "country": c.country,

                "source": c.source,

                "confidence": c.confidence

            }

            for c in candidates

        ]

    }



# =====================================================
# COUNTRY FROM OPERATING COUNTRIES
# =====================================================

def detect_country_from_operating(
    countries: List[str]
) -> str:
    """
    Détecte le premier pays africain
    dans operating_countries.
    """

    if not countries:

        return ""

    for country in countries:

        country = normalize_country_name(
            country
        )

        if is_african_country(
            country
        ):

            return country

    return ""

  # =====================================================
# COUNTRY FROM PHONE
# =====================================================

def detect_country_from_phone(
    phones: List[str]
) -> str:
    """
    Détecte le pays à partir des numéros
    de téléphone.

    Si plusieurs numéros existent,
    le pays le plus fréquent est retenu.

    Les téléphones doivent être déjà
    normalisés par phone_normalizer.py
    """

    if not phones:

        return ""
    
    detected_countries = []

    for phone in phones:

        if not phone:

            continue

        # Cas où phone est un objet
        if isinstance(phone, dict):

            phone = phone.get(
                "number",
                ""
            )

        phone = str(phone).strip()

        if not phone:

            continue

        phone = re.sub(
            r"[^\d+]",
            "",
            phone
        )

        for code, country in sorted(

            PHONE_COUNTRY_CODES.items(),

            key=lambda item: len(item[0]),

            reverse=True

        ):

            if phone.startswith(code):

                detected_countries.append(
                    normalize_country_name(
                        country
                    )
                )
                break

    if not detected_countries:

        return ""
    counter = Counter(
        detected_countries
    )
    country, _ = counter.most_common(1)[0]
    return country

# =====================================================
# COUNTRY FROM WEBSITE DOMAIN
# =====================================================

def detect_country_from_domain(
    website: str
) -> str:
    """
    Détecte le pays grâce au TLD
    du domaine.

    Exemple :

    startup.tn
        -> Tunisia

    company.ng
        -> Nigeria
    """

    if not website:

        return ""

    try:

        domain = urlparse(
            website
        ).netloc.lower()

    except Exception:

        return ""

    for suffix, country in TLD_COUNTRIES.items():

        if domain.endswith(
            suffix
        ):

            return normalize_country_name(
                country
            )

    return ""
# =====================================================
# COUNTRY FROM WEBSITE CONTENT
# =====================================================

def detect_country_from_content(
    content: str
) -> str:
    """
    Détecte le pays le plus probable
    à partir du contenu du site.

    Recherche :
        - les pays
        - les villes africaines

    Retourne le pays le plus fréquent.
    """

    if not content:

        return ""

    content = content.lower()

    detected_countries = []

    # -----------------------------------------
    # Recherche des pays
    # -----------------------------------------

    for country in AFRICAN_COUNTRIES:

        occurrences = content.count(
            country.lower()
        )

        if occurrences:

            detected_countries.extend(

                [country] * occurrences

            )

    # -----------------------------------------
    # Recherche des villes
    # -----------------------------------------

    for city, country in AFRICAN_LOCATIONS.items():

        occurrences = content.count(
            city.lower()
        )

        if occurrences:

            detected_countries.extend(

                [country] * occurrences

            )

    if not detected_countries:

        return ""

    counter = Counter(
        detected_countries
    )

    country, _ = counter.most_common(1)[0]

    return normalize_country_name(
        country
    )

# =====================================================
# MAIN NORMALIZER
# =====================================================

def normalize_country(
    entity: Dict
) -> Dict:
    """
    Détecte le pays à partir de plusieurs
    sources puis choisit la plus fiable.
    """

    candidates: List[CountryCandidate] = []

    # -------------------------------------------------
    # Country
    # -------------------------------------------------

    add_candidate(

        candidates,

        normalize_country_name(

            entity.get(
                "country",
                ""
            )

        ),

        "country"

    )

    # -------------------------------------------------
    # Phones
    # -------------------------------------------------

    phones = entity.get(
        "contact",
        {}
    ).get(
        "phones",
        []
    )

    add_candidate(

        candidates,

        detect_country_from_phone(
            phones
        ),

        "phone"

    )

    # -------------------------------------------------
    # Headquarters
    # -------------------------------------------------

    add_candidate(

        candidates,

        detect_country_from_headquarters(

            entity.get(
                "headquarters",
                ""
            )

        ),

        "headquarters"

    )

    # -------------------------------------------------
    # Operating countries
    # -------------------------------------------------

    add_candidate(

        candidates,

        detect_country_from_operating(

            entity.get(
                "operating_countries",
                []
            )

        ),

        "operating"

    )

    # -------------------------------------------------
    # Website domain
    # -------------------------------------------------

    add_candidate(

        candidates,

        detect_country_from_domain(

            entity.get(
                "website",
                ""
            )

        ),

        "domain"

    )

    # -------------------------------------------------
    # Website content
    # -------------------------------------------------

    add_candidate(

        candidates,

        detect_country_from_content(

            entity.get(
                "website_content",
                ""
            )

        ),

        "website_content"

    )

    # -------------------------------------------------
    # BEST COUNTRY
    # -------------------------------------------------

    best = get_best_country(
        candidates
    )

    if best:

        entity["country"] = best.country

    else:

        entity["country"] = ""

    # -------------------------------------------------
    # ETL REPORT
    # -------------------------------------------------

    entity.setdefault(
        "etl",
        {}
    )

    entity["etl"]["country_detection"] = {

        "selected_country": entity["country"],

        "selected_source": (

            best.source

            if best

            else ""

        ),

        "confidence": (

            best.confidence

            if best

            else 0

        ),

        "report": build_country_report(
            candidates
        )

    }

    return entity

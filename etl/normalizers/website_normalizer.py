# etl/normalizers/website_normalizer.py

from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import (
    urlparse,
    urlunparse,
    parse_qsl,
    urlencode
)

import re
# =====================================================
# INVALID VALUES
# =====================================================

INVALID_VALUES = {

    "",

    "-",

    "--",

    "---",

    "null",

    "none",

    "n/a",

    "na",

    "undefined",

    "unknown"

}
# =====================================================
# TRACKING PARAMETERS
# =====================================================

TRACKING_PARAMETERS = {

    "utm_source",

    "utm_medium",

    "utm_campaign",

    "utm_content",

    "utm_term",

    "fbclid",

    "gclid",

    "mc_cid",

    "mc_eid"

}
# =====================================================
# SOCIAL DOMAINS
# =====================================================

SOCIAL_DOMAINS = {

    "linkedin.com": "linkedin",

    "www.linkedin.com": "linkedin",

    "facebook.com": "facebook",

    "www.facebook.com": "facebook",

    "instagram.com": "instagram",

    "www.instagram.com": "instagram",

    "x.com": "twitter",

    "twitter.com": "twitter",

    "github.com": "github",

    "www.github.com": "github",

    "youtube.com": "youtube",

    "www.youtube.com": "youtube",

    "crunchbase.com": "crunchbase",

    "www.crunchbase.com": "crunchbase",

    "wellfound.com": "wellfound",

    "dealroom.co": "dealroom",

    "pitchbook.com": "pitchbook",

    "medium.com": "medium"

}
# =====================================================
# WEBSITE INFO
# =====================================================

@dataclass

class WebsiteInfo:

    original: str

    normalized: str

    domain: str

    root_domain: str

    url_type: str

    valid: bool
 # =====================================================
# CLEAN URL
# =====================================================

def clean_url(
    url: str
) -> str:
    """
    Nettoie une URL brute.

    Exemple :

    " https://site.com/ ) "

        ↓

    https://site.com
    """

    if not url:

        return ""

    url = str(url).strip()

    if not url:

        return ""

    lower = url.lower()

    if lower in INVALID_VALUES:

        return ""

    return url
 # =====================================================
# REMOVE TRAILING CHARACTERS
# =====================================================

def remove_trailing_characters(
    url: str
) -> str:
    """
    Supprime les caractères parasites
    trouvés à la fin des URL.
    """

    if not url:

        return ""

    while url.endswith(

        (
            ")",
            "]",
            "}",
            ",",
            ";",
            "."
        )

    ):

        url = url[:-1]

    return url
# =====================================================
# REMOVE TRACKING PARAMETERS
# =====================================================

def remove_tracking_parameters(
    url: str
) -> str:
    """
    Supprime les paramètres marketing.

    Exemple :

    https://site.com/?utm_source=google

        ↓

    https://site.com
    """

    if not url:

        return ""

    try:

        parsed = urlparse(url)

    except Exception:

        return url

    query = [

        (key, value)

        for key, value

        in parse_qsl(

            parsed.query,

            keep_blank_values=True

        )

        if key not in TRACKING_PARAMETERS

    ]

    parsed = parsed._replace(

        query=urlencode(query)

    )

    return urlunparse(parsed)

# =====================================================
# NORMALIZE URL
# =====================================================

def normalize_url(
    url: str
) -> str:
    """
    Normalise complètement une URL.
    """

    url = clean_url(
        url
    )

    if not url:

        return ""

    url = remove_trailing_characters(
        url
    )

    # www.site.com

    if url.startswith("www."):

        url = "https://" + url

    # site.com

    elif (

        "." in url

        and not url.startswith(

            (
                "http://",

                "https://"

            )

        )

    ):

        url = "https://" + url

    url = remove_tracking_parameters(
        url
    )

    # suppression du "/" final

    if url.endswith("/"):

        url = url[:-1]

    return url

# =====================================================
# EXTRACT DOMAIN
# =====================================================

def extract_domain(
    url: str
) -> str:
    """
    Retourne le domaine complet.

    Exemple :

    https://www.linkedin.com/company/openai

            ↓

    www.linkedin.com
    """

    url = normalize_url(
        url
    )

    if not url:

        return ""

    try:

        return urlparse(
            url
        ).netloc.lower()

    except Exception:

        return ""  
    
# =====================================================
# EXTRACT ROOT DOMAIN
# =====================================================

def extract_root_domain(
    url: str
) -> str:
    """
    Retourne uniquement le domaine principal.

    Exemple :

    www.linkedin.com

        ↓

    linkedin.com

    startup.company.co.tn

        ↓

    company.co.tn
    """

    domain = extract_domain(
        url
    )

    if not domain:

        return ""

    if domain.startswith("www."):

        domain = domain[4:]

    parts = domain.split(".")

    if len(parts) <= 2:

        return domain

    # Gestion des TLD africains

    if parts[-2] == "co":

        return ".".join(

            parts[-3:]

        )

    return ".".join(

        parts[-2:]

    )

# =====================================================
# VALID URL
# =====================================================

def is_valid_url(
    url: str
) -> bool:
    """
    Vérifie qu'une URL est valide.
    """

    url = normalize_url(
        url
    )

    if not url:

        return False

    try:

        parsed = urlparse(
            url
        )

    except Exception:

        return False

    return (

        parsed.scheme

        in (

            "http",

            "https"

        )

        and

        bool(parsed.netloc)

    )

# =====================================================
# DETECT URL TYPE
# =====================================================

def detect_url_type(
    url: str
) -> str:
    """
    Détermine automatiquement
    le type d'URL.
    """

    domain = extract_root_domain(
        url
    )

    if not domain:

        return "unknown"

    if domain in SOCIAL_DOMAINS:

        return SOCIAL_DOMAINS[
            domain
        ]

    return "official"

# =====================================================
# SOCIAL URL
# =====================================================

def is_social_url(
    url: str
) -> bool:
    """
    Vérifie si une URL est
    un réseau social.
    """

    return (

        detect_url_type(
            url
        )

        != "official"

    )
# =====================================================
# NORMALIZE SOCIAL PROFILES
# =====================================================

def normalize_social_profiles(
    profiles: Dict
) -> Dict:
    """
    Normalise tous les profils sociaux.
    """

    if not isinstance(
        profiles,
        dict
    ):

        return {}

    normalized = {}

    for network, url in profiles.items():

        url = normalize_url(
            url
        )

        if not url:

            continue

        normalized[
            network.lower()
        ] = url

    return normalized

# =====================================================
# NORMALIZE EXTERNAL PROFILES
# =====================================================

def normalize_external_profiles(
    profiles: Dict
) -> Dict:
    """
    Normalise Crunchbase,
    Dealroom,
    PitchBook,
    GitHub,
    Wellfound...
    """

    if not isinstance(
        profiles,
        dict
    ):

        return {}

    normalized = {}

    for source, url in profiles.items():

        url = normalize_url(
            url
        )

        if not url:

            continue

        normalized[
            source.lower()
        ] = url

    return normalized

# =====================================================
# BUILD WEBSITE REPORT
# =====================================================

def build_website_report(
    entity: Dict
) -> Dict:
    """
    Génère un rapport ETL
    sur les URLs.
    """

    social_profiles = entity.get(
        "social_media",
        {}
    )

    external_profiles = entity.get(
        "external_profiles",
        {}
    )

    report = {

        "website_valid":

            is_valid_url(

                entity.get(
                    "website",
                    ""
                )

            ),

        "website_domain":

            extract_root_domain(

                entity.get(
                    "website",
                    ""
                )

            ),

        "website_type":

            detect_url_type(

                entity.get(
                    "website",
                    ""
                )

            ),

        "social_profiles":

            len(

                social_profiles

            ),

        "external_profiles":

            len(

                external_profiles

            )

    }

    return report

# =====================================================
# MAIN WEBSITE NORMALIZER
# =====================================================

def normalize_entity_websites(
    entity: Dict
) -> Dict:
    """
    Normalise toutes les URLs
    d'une startup ou d'un investisseur.
    """

    # ----------------------------------
    # Website
    # ----------------------------------

    entity["website"] = normalize_url(

        entity.get(
            "website",
            ""
        )

    )

    # ----------------------------------
    # LinkedIn
    # ----------------------------------

    if entity.get(
        "linkedin_url"
    ):

        entity["linkedin_url"] = normalize_url(

            entity[
                "linkedin_url"
            ]

        )

    # ----------------------------------
    # Social media
    # ----------------------------------

    entity["social_media"] = normalize_social_profiles(

        entity.get(
            "social_media",
            {}
        )

    )

    # ----------------------------------
    # External profiles
    # ----------------------------------

    entity["external_profiles"] = normalize_external_profiles(

        entity.get(
            "external_profiles",
            {}
        )

    )

    # ----------------------------------
    # ETL REPORT
    # ----------------------------------

    entity.setdefault(
        "etl",
        {}
    )

    entity["etl"]["w" \
    "ebsite_validation"] = build_website_report(
        entity
    )

    return entity
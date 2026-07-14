# etl/normalizers/social_normalizer.py

from dataclasses import dataclass
from typing import Dict
from urllib.parse import urlparse

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
# SOCIAL DOMAINS
# =====================================================

SOCIAL_DOMAINS = {

    "linkedin": "linkedin.com",

    "facebook": "facebook.com",

    "instagram": "instagram.com",

    "twitter": "twitter.com",

    "x": "x.com",

    "youtube": "youtube.com",

    "github": "github.com",

    "tiktok": "tiktok.com",

    "medium": "medium.com"

}

# =====================================================
# SOCIAL PROFILE
# =====================================================

@dataclass
class SocialProfile:

    platform: str

    original: str

    normalized: str

    username: str

    valid: bool

    official: bool = True

    source: str = "social_media"

    confidence: float = 1.0

    def to_dict(self) -> Dict:

        return {

            "platform": self.platform,

            "original": self.original,

            "normalized": self.normalized,

            "username": self.username,

            "valid": self.valid,

            "official": self.official

        }
    
    # =====================================================
# CLEAN SOCIAL URL
# =====================================================

def clean_social_url(
    url: str
) -> str:
    """
    Nettoie une URL de réseau social.
    """

    if not url:

        return ""

    url = str(url).strip()

    if not url:

        return ""

    if url.lower() in INVALID_VALUES:

        return ""

    url = url.replace(
        " ",
        ""
    )

    url = url.rstrip(
        ")]}>;,."
    )

    if url.startswith("www."):

        url = "https://" + url

    elif (

        "." in url

        and

        not url.startswith(

            (
                "http://",
                "https://"
            )

        )

    ):

        url = "https://" + url

    return url

# =====================================================
# DETECT PLATFORM
# =====================================================

def detect_platform(
    url: str
) -> str:
    """
    Détecte automatiquement
    la plateforme d'une URL.
    """

    url = clean_social_url(
        url
    )

    if not url:
        return ""

    try:

        domain = urlparse(
            url
        ).netloc.lower()

    except Exception:

        return ""

    if domain.startswith("www."):

        domain = domain[4:]

    for platform, social_domain in SOCIAL_DOMAINS.items():

        if social_domain == domain:

            return platform

    return ""

# =====================================================
# NORMALIZE SOCIAL URL
# =====================================================

def normalize_social_url(
    url: str
) -> str:
    """
    Normalise une URL de réseau social.
    """

    url = clean_social_url(
        url
    )

    if not url:

        return ""

    try:

        parsed = urlparse(
            url
        )

    except Exception:

        return ""

    domain = parsed.netloc.lower()

    if domain.startswith("www."):

        domain = domain[4:]

    path = parsed.path.rstrip("/")

    return f"https://{domain}{path}"

# =====================================================
# EXTRACT USERNAME
# =====================================================

def extract_username(
    url: str
) -> str:
    """
    Extrait le nom du profil.

    Exemples :

    linkedin.com/company/openai

        -> openai

    github.com/openai

        -> openai
    """

    url = normalize_social_url(
        url
    )

    if not url:

        return ""

    try:

        parsed = urlparse(
            url
        )

    except Exception:

        return ""

    parts = [

        part

        for part in parsed.path.split("/")

        if part

    ]

    if not parts:

        return ""

    # company/openai
    if len(parts) >= 2:

        if parts[0] in {

            "company",

            "in",

            "school",

            "organization",

            "org"

        }:

            return parts[1]

    return parts[0]

# =====================================================
# VALID SOCIAL URL
# =====================================================

def is_valid_social_url(
    url: str
) -> bool:
    """
    Vérifie qu'une URL appartient
    réellement à un réseau social connu.
    """

    platform = detect_platform(
        url
    )

    return bool(platform)

# =====================================================
# BUILD SOCIAL PROFILE
# =====================================================

def build_social_profile(
    url: str
) -> SocialProfile:
    """
    Construit un SocialProfile à partir
    d'une URL.
    """

    normalized = normalize_social_url(
        url
    )

    platform = detect_platform(
        normalized
    )

    valid = bool(
        platform
    )

    username = ""

    if valid:

        username = extract_username(
            normalized
        )

    return SocialProfile(

        platform=platform,

        original=url,

        normalized=normalized,

        username=username,

        valid=valid,

        official=True

    )

# =====================================================
# NORMALIZE SOCIAL PROFILES
# =====================================================

def normalize_social_profiles(
    socials: Dict[str, str]
) -> Dict[str, SocialProfile]:
    """
    Nettoie tous les profils sociaux.

    Retourne un dictionnaire :

    {
        "linkedin": SocialProfile(...),
        "github": SocialProfile(...)
    }
    """

    profiles = {}

    seen = set()

    for _, url in socials.items():

        if not url:

            continue

        profile = build_social_profile(
            url
        )

        if not profile.valid:

            continue

        if profile.normalized in seen:

            continue

        seen.add(
            profile.normalized
        )

        profiles[
            profile.platform
        ] = profile

    return profiles

# =====================================================
# MERGE SOCIALS
# =====================================================

def merge_social_profiles(
    *social_dicts: Dict[str, str]
) -> Dict[str, SocialProfile]:
    """
    Fusionne plusieurs dictionnaires
    de réseaux sociaux.

    Exemple :

        social_media

        external_profiles

    ↓

        un seul dictionnaire
    """

    merged = {}

    for socials in social_dicts:

        if not socials:

            continue

        profiles = normalize_social_profiles(
            socials
        )

        for platform, profile in profiles.items():

            if platform not in merged:

                merged[
                    platform
                ] = profile

    return merged

# =====================================================
# SOCIAL LIST
# =====================================================

def social_profiles_to_dict(
    profiles: Dict[str, SocialProfile]
) -> Dict[str, str]:
    """
    Convertit les SocialProfile
    vers un JSON simple.
    """

    return {

        platform: profile.normalized

        for platform, profile in profiles.items()

    }

# =====================================================
# SOCIAL REPORT
# =====================================================

def build_social_report(
    profiles: Dict[str, SocialProfile]
) -> Dict:
    """
    Génère un rapport qualité
    sur les profils sociaux.
    """

    return {

        "total": len(profiles),

        "valid": sum(

            profile.valid

            for profile in profiles.values()

        ),

        "official": sum(

            profile.official

            for profile in profiles.values()

        ),

        "platforms": sorted(

            profiles.keys()

        )

    }

# =====================================================
# SOCIAL STATISTICS
# =====================================================

def build_social_statistics(
    profiles: Dict[str, SocialProfile]
) -> Dict:
    """
    Statistiques utilisées
    dans MongoDB et le Dashboard.
    """

    stats = {

        "profiles_count": len(profiles)

    }

    for platform in SOCIAL_DOMAINS:

        stats[platform] = (

            platform in profiles

        )

    return stats

# =====================================================
# SOCIAL DETAILS
# =====================================================

def build_social_details(
    profiles: Dict[str, SocialProfile]
) -> Dict:
    """
    Retourne tous les profils
    sous forme JSON.
    """

    return {

        platform: profile.to_dict()

        for platform, profile in profiles.items()

    }

# =====================================================
# PRIMARY SOCIAL
# =====================================================

SOCIAL_PRIORITY = {

    "linkedin": 100,

    "github": 90,

    "twitter": 80,

    "x": 80,

    "facebook": 70,

    "instagram": 60,

    "youtube": 50,

    "tiktok": 40,

    "medium": 30

}


# =====================================================
# PRIMARY SOCIAL
# =====================================================

def resolve_primary_social(
    profiles: Dict[str, SocialProfile]
) -> str:
    """
    Retourne le profil social
    le plus important.
    """

    if not profiles:

        return ""

    best = max(

        profiles.values(),

        key=lambda profile: SOCIAL_PRIORITY.get(

            profile.platform,

            0

        )

    )

    return best.normalized

# =====================================================
# NORMALIZE ENTITY SOCIALS
# =====================================================

def normalize_entity_socials(
    entity: Dict
) -> Dict:
    """
    Normalise tous les profils sociaux
    d'une startup ou d'un investisseur.
    """

    # -----------------------------------------
    # social_media
    # -----------------------------------------

    social_media = entity.get(
        "social_media",
        {}
    )

    if not isinstance(
        social_media,
        dict
    ):

        social_media = {}

    # -----------------------------------------
    # external_profiles
    # -----------------------------------------

    external_profiles = entity.get(
        "external_profiles",
        {}
    )

    if not isinstance(
        external_profiles,
        dict
    ):

        external_profiles = {}

    # -----------------------------------------
    # Fusion
    # -----------------------------------------

    profiles = merge_social_profiles(

        social_media,

        external_profiles

    )

    # -----------------------------------------
    # Sauvegarde
    # -----------------------------------------

    entity["social_media"] = social_profiles_to_dict(
        profiles
    )

    # -----------------------------------------
    # Primary Social
    # -----------------------------------------

    entity.setdefault(
        "contact",
        {}
    )

    entity["contact"]["primary_social"] = resolve_primary_social(
        profiles
    )

    # -----------------------------------------
    # ETL Report
    # -----------------------------------------

    entity.setdefault(
        "etl",
        {}
    )

    entity["etl"]["social_validation"] = {

        "report": build_social_report(
            profiles
        ),

        "details": build_social_details(
            profiles
        )

    }

    # -----------------------------------------
    # Statistics
    # -----------------------------------------

    entity.setdefault(
        "stats",
        {}
    )

    entity["stats"]["social"] = build_social_statistics(
        profiles
    )

    return entity


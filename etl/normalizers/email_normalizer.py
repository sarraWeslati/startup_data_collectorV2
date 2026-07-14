# etl/normalizers/email_normalizer.py

from dataclasses import dataclass
from typing import Dict, List
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
# GENERIC EMAIL PROVIDERS
# =====================================================

GENERIC_EMAIL_PROVIDERS = {

    "gmail.com",

    "hotmail.com",

    "outlook.com",

    "live.com",

    "icloud.com",

    "yahoo.com",

    "yahoo.fr",

    "proton.me",

    "protonmail.com",

    "aol.com",

    "msn.com",

    "mail.com",

    "gmx.com"

}


# =====================================================
# EMAIL INFO
# =====================================================

@dataclass

class EmailInfo:

    original: str

    normalized: str

    domain: str

    valid: bool

    generic: bool

    business: bool

    official: bool = False

    source: str = "contact"

    def to_dict(self) -> Dict:

        return {

            "original": self.original,

            "normalized": self.normalized,

            "domain": self.domain,

            "valid": self.valid,

            "generic": self.generic,

            "business": self.business,

            "official": self.official,

            "source": self.source

        }


# =====================================================
# CLEAN EMAIL
# =====================================================

def clean_email(
    email: str
) -> str:
    """
    Nettoie un email brut.

    Exemple :

        " Contact@Startup.com ) "

            ↓

        contact@startup.com
    """

    if not email:

        return ""

    email = str(email).strip()

    if not email:

        return ""

    if email.lower() in INVALID_VALUES:

        return ""

    # Minuscules

    email = email.lower()

    # Suppression espaces

    email = email.replace(" ", "")

    # Parenthèses

    email = email.rstrip(")]}>;,.")

    # Cas fréquents du scraping

    email = email.replace("(at)", "@")

    email = email.replace("[at]", "@")

    email = email.replace("{at}", "@")

    email = email.replace(" at ", "@")

    email = email.replace("(dot)", ".")

    email = email.replace("[dot]", ".")

    email = email.replace("{dot}", ".")

    email = email.replace(" dot ", ".")

    return email

# =====================================================
# EMAIL REGEX
# =====================================================

EMAIL_REGEX = re.compile(

    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

)


# =====================================================
# VALID EMAIL
# =====================================================

def is_valid_email(
    email: str
) -> bool:
    """
    Vérifie qu'un email est valide.

    Exemples valides :

        contact@startup.com

        info@company.co.ke

        hello@startup.tn
    """

    email = clean_email(
        email
    )

    if not email:

        return False

    if len(email) > 254:

        return False

    if email.count("@") != 1:

        return False

    if not EMAIL_REGEX.match(
        email
    ):

        return False

    local, domain = email.split("@")

    if not local:

        return False

    if not domain:

        return False

    if ".." in email:

        return False

    if domain.startswith("."):

        return False

    if domain.endswith("."):

        return False

    return True

# =====================================================
# EMAIL DOMAIN
# =====================================================

def extract_email_domain(
    email: str
) -> str:
    """
    Retourne uniquement le domaine.

    contact@startup.com

    →

    startup.com
    """

    email = clean_email(
        email
    )

    if not is_valid_email(
        email
    ):

        return ""

    return email.split(
        "@",
        1
    )[1]

# =====================================================
# NORMALIZE EMAIL
# =====================================================

def normalize_email(
    email: str
) -> str:
    """
    Nettoie puis valide un email.

    Retourne :

        email normalisé

    ou ""

    si invalide.
    """

    email = clean_email(
        email
    )

    if not is_valid_email(
        email
    ):

        return ""

    return email


# =====================================================
# GENERIC EMAIL
# =====================================================

def is_generic_email(
    email: str
) -> bool:
    """
    Vérifie si un email appartient
    à un fournisseur générique.

    Exemple :

        gmail.com
        yahoo.com
        outlook.com
    """

    email = normalize_email(
        email
    )

    if not email:
        return False

    domain = extract_email_domain(
        email
    )

    return domain in GENERIC_EMAIL_PROVIDERS

# =====================================================
# BUSINESS EMAIL
# =====================================================

def is_business_email(
    email: str
) -> bool:
    """
    Vérifie si un email est professionnel.
    """

    email = normalize_email(
        email
    )

    if not email:
        return False

    return not is_generic_email(
        email
    )

# =====================================================
# WEBSITE DOMAIN
# =====================================================

def extract_website_domain(
    website: str
) -> str:
    """
    Extrait le domaine d'un site web.

    https://www.startup.com/about

        →

    startup.com
    """

    if not website:
        return ""

    try:

        domain = urlparse(
            website
        ).netloc.lower()

    except Exception:

        return ""

    if domain.startswith("www."):

        domain = domain[4:]

    return domain

# =====================================================
# EMAIL MATCHES WEBSITE
# =====================================================

def email_matches_website(
    email: str,
    website: str
) -> bool:
    """
    Vérifie si le domaine de l'email
    correspond au site officiel.
    """

    email = normalize_email(
        email
    )

    if not email:
        return False

    email_domain = extract_email_domain(
        email
    )

    website_domain = extract_website_domain(
        website
    )

    if not website_domain:
        return False

    return email_domain == website_domain

# =====================================================
# BUILD EMAIL INFO
# =====================================================

def build_email_info(
    email: str,
    website: str = "",
    source: str = "website"
) -> EmailInfo:
    """
    Construit un objet EmailInfo.
    """

    normalized = normalize_email(
        email
    )

    valid = bool(normalized)

    domain = ""

    if valid:

        domain = extract_email_domain(
            normalized
        )

    generic = False

    business = False

    if valid:

        generic = is_generic_email(
            normalized
        )

        business = is_business_email(
            normalized
        )

    return EmailInfo(

        original=email,

        normalized=normalized,

        domain=domain,

        valid=valid,

        generic=generic,

        business=business,

        official=email_matches_website(
            normalized,
            website
        ) if valid else False,

        source=source

    )

# =====================================================
# NORMALIZE EMAIL LIST
# =====================================================

def normalize_email_list(
    emails: List[str],
    website: str = ""
) -> List[EmailInfo]:
    """
    Nettoie une liste d'emails.

    - suppression des doublons
    - suppression des emails invalides
    - création des EmailInfo
    """

    normalized = []

    seen = set()

    for email in emails:

        info = build_email_info(
            email,
            website
        )

        if not info.valid:
            continue

        if info.normalized in seen:
            continue

        seen.add(
            info.normalized
        )

        info.official = email_matches_website(
            info.normalized,
            website
        )

        normalized.append(
            info
        )

    return normalized

# =====================================================
# EMAIL REPORT
# =====================================================

def build_email_report(
    emails: List[EmailInfo]
) -> Dict:
    """
    Génère un rapport qualité.
    """

    return {

        "total": len(emails),

        "business": sum(

            email.business

            for email in emails

        ),

        "generic": sum(

            email.generic

            for email in emails

        ),

        "official": sum(

            email.official

            for email in emails

        ),

        "domains": sorted({

            email.domain

            for email in emails

        })

    }

# =====================================================
# EMAIL STATISTICS
# =====================================================

def build_email_statistics(
    emails: List[EmailInfo]
) -> Dict:
    """
    Statistiques utiles
    pour MongoDB et le Dashboard.
    """

    return {

        "count": len(emails),

        "business_count": sum(

            e.business

            for e in emails

        ),

        "generic_count": sum(

            e.generic

            for e in emails

        ),

        "official_count": sum(

            e.official

            for e in emails

        ),

        "domains": extract_domains(
            emails
        )

    }

# =====================================================
# NORMALIZE ENTITY EMAILS
# =====================================================

def normalize_entity_emails(
    entity: Dict
) -> Dict:
    """
    Normalise tous les emails
    d'une startup ou d'un investisseur.
    """

    contact = entity.get(
        "contact",
        {}
    )

    if not isinstance(
        contact,
        dict
    ):

        contact = {}

    emails = contact.get(
        "emails",
        []
    )

    if not isinstance(
        emails,
        list
    ):

        emails = []

    website = entity.get(
        "website",
        ""
    )

    normalized = normalize_email_list(

        emails,

        website

    )

    contact["emails"] = [

        email.normalized

        for email in normalized

    ]

    entity["primary_email"] = resolve_primary_email(normalized)

    entity["contact"] = contact

    entity.setdefault(
        "etl",
        {}
    )

    entity.setdefault(
        "stats",
        {}
    )

    entity["stats"]["emails"] = build_email_statistics(
        normalized
    )

    entity["etl"]["email_validation"] = {

        "report": build_email_report(
            normalized
        ),

        "official": get_official_emails(
            normalized
        ),

        "details":[

            email.to_dict()

            for email in normalized

        ]

    }

    return entity

# =====================================================
# RESOLVE PRIMARY EMAIL
# =====================================================

def resolve_primary_email(
    emails: List[EmailInfo]
) -> str:
    """
    Choisit le meilleur email.

    Priorité :

        1. officiel

        2. business

        3. générique
    """

    if not emails:
        return ""

    official = [

        email

        for email in emails

        if email.official

    ]

    if official:

        return official[0].normalized

    business = [

        email

        for email in emails

        if email.business

    ]

    if business:

        return business[0].normalized

    return emails[0].normalized

# =====================================================
# EMAIL DOMAINS
# =====================================================

def extract_domains(
    emails: List[EmailInfo]
) -> List[str]:

    return sorted({

        email.domain

        for email in emails

    })

# =====================================================
# OFFICIAL EMAILS
# =====================================================

def get_official_emails(
    emails: List[EmailInfo]
) -> List[str]:

    return [

        email.normalized

        for email in emails

        if email.official

    ]


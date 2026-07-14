# utils/company_matching.py

from typing import Optional

from utils.name_normalizer import (
    normalize_name
)

from utils.url_normalizer import (
    get_domain
)


# =====================================================
# COMPANY NAME VS WEBSITE
# =====================================================

def is_matching_company(
    company_name: str,
    website: Optional[str]
) -> bool:
    """
    Vérifie si un nom d'entreprise
    correspond au domaine du site web.

    Exemple :

    InstaDeep
        ↔
    https://instadeep.com

    216 Capital
        ↔
    https://216capital.vc
    """

    if not company_name or not website:
        return False

    normalized_name = normalize_name(
        company_name
    )

    domain = get_domain(
        website
    )

    if not domain:
        return False

    # instadeep.com -> instadeep
    domain = domain.split(".")[0]

    domain = normalize_name(
        domain
    )

    # Correspondance exacte
    if normalized_name == domain:
        return True

    # Le nom contient le domaine
    if domain in normalized_name:
        return True

    # Le domaine contient le nom
    if normalized_name in domain:
        return True

    return False
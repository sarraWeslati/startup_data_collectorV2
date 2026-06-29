from urllib.parse import urlparse
import re


def normalize_name(name: str) -> str:
    """
    Normalise un nom d'entreprise.
    """

    if not name:
        return ""

    name = name.lower()

    name = re.sub(r"[^a-z0-9]", "", name)

    return name


def get_domain(url: str) -> str:
    """
    Extrait le domaine principal.
    """

    if not url:
        return ""

    try:

        domain = urlparse(url).netloc.lower()

        domain = domain.replace("www.", "")

        return domain

    except Exception:

        return ""
    
def is_matching_company(
    company_name: str,
    url: str
) -> bool:
    """
    Vérifie si une URL correspond
    réellement à l'entreprise recherchée.
    """

    if not company_name or not url:
        return False

    company = normalize_name(company_name)

    try:

        parsed = urlparse(url)

        domain = normalize_name(
            parsed.netloc.replace(
                "www.",
                ""
            )
        )

        path = normalize_name(
            parsed.path
        )

        full = domain + path

    except Exception:

        return False

    # Correspondance exacte
    if company == domain:
        return True

    # Domaine contenant le nom
    if company in domain:
        return True

    # Nom contenant le domaine
    if domain in company:
        return True

    # Vérifie aussi le chemin de l'URL
    if company in path:
        return True

    # Vérifie l'ensemble domaine + chemin
    if company in full:
        return True

    return False
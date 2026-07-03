from urllib.parse import urlparse
import unicodedata
import re

STOP_WORDS = {

    "inc",
    "llc",
    "ltd",
    "limited",
    "group",
    "holding",
    "holdings",
    "company",
    "corp",
    "corporation",
    "sa",
    "sas",
    "sarl",
    "plc"

}

def normalize_name(
    name: str
) -> str:

    if not name:
        return ""

    # Supprime les accents
    name = unicodedata.normalize(
        "NFKD",
        name
    )

    name = "".join(

        c

        for c in name

        if not unicodedata.combining(c)

    )

    name = name.lower()

    words = re.findall(
        r"[a-z0-9]+",
        name
    )

    words = [

        w

        for w in words

        if w not in STOP_WORDS

    ]

    return "".join(words)


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
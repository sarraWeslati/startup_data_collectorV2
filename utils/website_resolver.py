from urllib.parse import urlparse

from utils.url_normalizer import normalize_website


PREFERRED_TLDS = (
    ".co.tz",
    ".co.ke",
    ".co.za",
    ".com.ng",
    ".com.gh",
    ".com.tn",
    ".tn",
    ".za",
    ".ng",
    ".ke",
    ".gh",
    ".rw",
    ".ug",
    ".ma",
    ".dz",
    ".sn",
    ".ci",
    ".et",
    ".tz",
)

BLACKLIST_DOMAINS = {

    "linkedin.com",
    "www.linkedin.com",

    "facebook.com",
    "www.facebook.com",

    "twitter.com",
    "x.com",

    "instagram.com",

    "youtube.com",

    "github.com",

    "crunchbase.com",

    "wellfound.com",

    "angel.co",

    "pitchbook.com",

    "dealroom.co",

    "startupblink.com",

    "medium.com",

    "wikipedia.org"

}

def get_domain(url: str) -> str:

    if not url:
        return ""

    url = normalize_website(url)

    try:

        return urlparse(url).netloc.lower()

    except Exception:

        return ""


def compute_score(url: str) -> int:
    """
    Attribue un score de confiance à une URL.
    """

    if not isinstance(url, str):
        return -100

    url = normalize_website(url)

    if not url:
        return -100

    domain = get_domain(url)

    score = 0

    # -----------------------------
    # Blacklist
    # -----------------------------

    if domain in BLACKLIST_DOMAINS:
        return -100

    # -----------------------------
    # HTTPS
    # -----------------------------

    if url.startswith("https://"):
        score += 5

    elif url.startswith("http://"):
        score += 2

    # -----------------------------
    # WWW
    # -----------------------------

    if domain.startswith("www."):
        score += 1

    # -----------------------------
    # TLD
    # -----------------------------

    if domain.endswith(".com"):
        score += 5

    elif domain.endswith(".io"):
        score += 4

    elif domain.endswith(".ai"):
        score += 4

    elif domain.endswith(".tech"):
        score += 4

    elif domain.endswith(".app"):
        score += 3

    elif domain.endswith(".org"):
        score += 1

    elif domain.endswith(".net"):
        score += 1

    for suffix in PREFERRED_TLDS:

        if domain.endswith(suffix):

            score += 10

            break

    # -----------------------------
    # Longueur
    # -----------------------------

    if len(domain.split(".")) <= 3:
        score += 2

    return score


def resolve_official_website(*urls: str) -> str:
    """
    Choisit le meilleur site parmi toutes les sources.
    """

    candidates = []

    seen = set()

    for url in urls:

        if not url:
            continue

        url = normalize_website(url)

        if not url:
            continue

        if url in seen:
            continue

        seen.add(url)

        domain = get_domain(url)

        if domain in BLACKLIST_DOMAINS:
            continue

        candidates.append(url)

    if not candidates:

        return ""

    candidates.sort(
        key=compute_score,
        reverse=True
    )

    return candidates[0]
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

    if not url:
        return -100

    url = normalize_website(url)

    domain = get_domain(url)

    score = 0

    if domain.startswith("www."):
        score += 1

    if domain.endswith(".org"):
        score -= 2

    if domain.endswith(".net"):
        score -= 2

    if domain.endswith(".io"):
        score += 2

    if domain.endswith(".ai"):
        score += 2

    if domain.endswith(".tech"):
        score += 2

    if domain.endswith(".app"):
        score += 2

    if domain.endswith(".com"):
        score += 3

    for suffix in PREFERRED_TLDS:

        if domain.endswith(suffix):

            score += 8

            break

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

        candidates.append(url)

    if not candidates:

        return ""

    candidates.sort(
        key=compute_score,
        reverse=True
    )

    return candidates[0]
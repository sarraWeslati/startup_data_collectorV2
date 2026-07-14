# utils/website_resolver.py

from urllib.parse import urlparse

from utils.url_normalizer import normalize_website
from utils.name_normalizer import normalize_name


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
    "www.youtube.com",

    "github.com",

    "crunchbase.com",
    "www.crunchbase.com",

    "wellfound.com",

    "angel.co",

    "pitchbook.com",

    "dealroom.co",

    "startupblink.com",

    "medium.com",
    "www.medium.com",

    "wikipedia.org",
    "www.wikipedia.org",

    "techcrunch.com",
    "www.techcrunch.com",

    "forbes.com",
    "www.forbes.com",

    "reuters.com",
    "www.reuters.com",

    "bloomberg.com",
    "www.bloomberg.com",
}


def get_domain(url: str) -> str:

    if not url:
        return ""

    url = normalize_website(url)

    try:
        return urlparse(url).netloc.lower()

    except Exception:
        return ""


# =====================================================
# COMPANY SCORE
# =====================================================

def company_name_score(
    company_name: str,
    url: str
) -> int:

    if not company_name:
        return 0

    company = normalize_name(
        company_name
    )

    domain = get_domain(
        url
    )

    if not domain:
        return 0

    # enlève www.
    domain = domain.replace(
        "www.",
        ""
    )

    # 2binnovations.com -> 2binnovations
    domain = domain.split(".")[0]

    domain = normalize_name(
        domain
    )

    if company == domain:
        return 100

    if company in domain:
        return 80

    if domain in company:
        return 60

    return 0


# =====================================================
# URL SCORE
# =====================================================

def compute_score(
    company_name: str,
    url: str
) -> int:

    if not isinstance(url, str):
        return -100

    url = normalize_website(url)

    if not url:
        return -100

    domain = get_domain(url)

    if domain in BLACKLIST_DOMAINS:
        return -100

    score = 0

    # HTTPS
    if url.startswith("https://"):
        score += 5

    elif url.startswith("http://"):
        score += 2

    # WWW
    if domain.startswith("www."):
        score += 1

    # Domaine
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

    # Domaine court
    if len(domain.split(".")) <= 3:
        score += 2

    # Similarité avec le nom
    score += company_name_score(
        company_name,
        url
    )

    # Pénalise les articles
    path = urlparse(url).path.lower()

    ARTICLE_KEYWORDS = [

        "/news/",
        "/article/",
        "/articles/",
        "/blog/",
        "/posts/",
        "/story/",
        "/stories/",

    ]

    for keyword in ARTICLE_KEYWORDS:

        if keyword in path:
            score -= 20

    if len(path.split("/")) > 3:
        score -= 5

    return score


# =====================================================
# RESOLVE WEBSITE
# =====================================================

def resolve_official_website(
    company_name: str,
    urls: list
) -> str:

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

        if get_domain(url) in BLACKLIST_DOMAINS:
            continue

        candidates.append(url)

    if not candidates:
        return ""

    candidates.sort(

        key=lambda url: compute_score(
            company_name,
            url
        ),

        reverse=True

    )

    return candidates[0]
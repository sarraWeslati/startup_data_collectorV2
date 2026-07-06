import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urldefrag, urlparse

from config import DISCOVERY_WORKERS, MAX_LINKS_PER_SOURCE, REQUEST_TIMEOUT

HEADERS = {"User-Agent": "Mozilla/5.0"}

ARTICLE_HINTS = (
    "/20", "202", "/news/", "/article/", "/articles/", "/startup/", "/startups/",
    "/funding/", "/investment/", "/investor/", "/venture-capital/", "/business/",
    "/economie/", "/banking/", "/report/", "/insights/", "/member-news/"
)

SKIP_HINTS = (
    "#", "mailto:", "tel:", "/tag/", "/tags/", "/author/", "/category/",
    "/categories/", "/page/", "/privacy", "/terms", "/contact", "/about",
    "/login", "/register", "/wp-content/", ".jpg", ".jpeg", ".png", ".gif",
    ".webp", ".svg", ".pdf", ".zip"
)

KEYWORDS = (
    "startup", "start-up", "startups", "funding", "financement", "levee",
    "invest", "investor", "vc", "venture", "capital", "fintech",
    "africa", "afrique", "tunisia", "tunisie", "bank", "banque", "fonds",
    "seed", "pre-seed", "serie-a", "series-a"
)


def clean_url(url):
    url, _ = urldefrag(url)
    return url.rstrip("/")


def is_same_site_or_subdomain(source_url, candidate_url):
    source_host = urlparse(source_url).netloc.replace("www.", "")
    candidate_host = urlparse(candidate_url).netloc.replace("www.", "")
    return candidate_host == source_host or candidate_host.endswith("." + source_host)


def looks_like_article(url, anchor_text=""):
    lower_url = url.lower()
    lower_text = anchor_text.lower()

    if any(x in lower_url for x in SKIP_HINTS):
        return False

    has_article_shape = any(x in lower_url for x in ARTICLE_HINTS)
    has_keyword = any(x in lower_url or x in lower_text for x in KEYWORDS)

    return has_article_shape and has_keyword


def discover_source(url):
    article_urls = []
    seen_urls = set()

    try:
        print(f"[EXPANDING] {url}")

        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        for a in soup.find_all("a", href=True):
            full_url = clean_url(urljoin(url, a["href"]))
            text = a.get_text(" ", strip=True)

            if not is_same_site_or_subdomain(url, full_url):
                continue

            if full_url not in seen_urls and looks_like_article(full_url, text):
                seen_urls.add(full_url)
                article_urls.append(full_url)

            if len(article_urls) >= MAX_LINKS_PER_SOURCE:
                break

    except Exception as e:
        print("[EXPAND ERROR]", url, e)

    return article_urls


def expand_urls(urls):
    all_urls = set()

    with ThreadPoolExecutor(max_workers=DISCOVERY_WORKERS) as executor:
        futures = {executor.submit(discover_source, url): url for url in urls}

        for future in as_completed(futures):
            source_url = futures[future]

            try:
                discovered = future.result()
            except Exception as e:
                print("[EXPAND ERROR]", source_url, e)
                continue

            all_urls.update(discovered)

    all_urls.update(clean_url(url) for url in urls if looks_like_article(url, url))

    return sorted(all_urls)

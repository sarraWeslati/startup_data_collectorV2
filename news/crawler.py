from bs4 import BeautifulSoup
from bs4 import FeatureNotFound
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urldefrag, urlparse

from config import (
    DISCOVERY_WORKERS,
    MAX_LINKS_PER_SOURCE,
    MAX_PAGES_PER_SOURCE,
)
from http_client import get_html

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

NEXT_TEXT_HINTS = (
    "next", "older", "more", "load more", "suivant", "suivante", "plus",
    "ancien", "ancienne", "prochaine", "weiter", "siguiente", "older posts",
    "next page", "page suivante", "articles suivants", ">", "\u00bb", "\u203a"
)

NEXT_ATTR_HINTS = (
    "next", "older", "load-more", "load_more", "pagination-next",
    "pager-next", "nav-next", "page-next", "suivant", "suivante"
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


def reached_link_limit(article_urls):
    return MAX_LINKS_PER_SOURCE > 0 and len(article_urls) >= MAX_LINKS_PER_SOURCE


def fetch_soup(url):
    html = get_html(url)
    try:
        return BeautifulSoup(html, "lxml")
    except FeatureNotFound:
        return BeautifulSoup(html, "html.parser")


def add_article_links(soup, source_url, page_url, article_urls, seen_urls):
    for a in soup.find_all("a", href=True):
        full_url = clean_url(urljoin(page_url, a["href"]))
        text = a.get_text(" ", strip=True)

        if not is_same_site_or_subdomain(source_url, full_url):
            continue

        if full_url not in seen_urls and looks_like_article(full_url, text):
            seen_urls.add(full_url)
            article_urls.append(full_url)

        if reached_link_limit(article_urls):
            return


def get_link_signature(link):
    text = link.get_text(" ", strip=True).lower()
    attrs = " ".join(
        " ".join(link.get(attr, [])) if isinstance(link.get(attr), list) else str(link.get(attr, ""))
        for attr in ("rel", "class", "id", "aria-label", "title")
    ).lower()
    return text, attrs


def find_next_page(soup, source_url, page_url, visited_pages):
    next_candidates = []

    for link in soup.find_all("a", href=True):
        full_url = clean_url(urljoin(page_url, link["href"]))

        if full_url in visited_pages:
            continue

        if not is_same_site_or_subdomain(source_url, full_url):
            continue

        text, attrs = get_link_signature(link)
        rel = link.get("rel") or []
        rel_values = {value.lower() for value in rel} if isinstance(rel, list) else {str(rel).lower()}

        is_next = (
            "next" in rel_values
            or any(hint == text or hint in text for hint in NEXT_TEXT_HINTS)
            or any(hint in attrs for hint in NEXT_ATTR_HINTS)
        )

        if is_next:
            next_candidates.append(full_url)

    return next_candidates[0] if next_candidates else None


def discover_source(url):
    article_urls = []
    seen_urls = set()
    visited_pages = set()
    page_url = clean_url(url)

    try:
        print(f"[EXPANDING] {url}")

        while page_url and page_url not in visited_pages:
            if MAX_PAGES_PER_SOURCE > 0 and len(visited_pages) >= MAX_PAGES_PER_SOURCE:
                print(f"[PAGINATION LIMIT] {url} reached {MAX_PAGES_PER_SOURCE} pages")
                break

            print(f"[DISCOVER PAGE] {page_url}")
            visited_pages.add(page_url)

            soup = fetch_soup(page_url)
            add_article_links(soup, url, page_url, article_urls, seen_urls)

            if reached_link_limit(article_urls):
                break

            page_url = find_next_page(soup, url, page_url, visited_pages)

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

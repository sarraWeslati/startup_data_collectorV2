import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT

HEADERS = {"User-Agent": "Mozilla/5.0"}


def content_length(tag):
    if not tag:
        return 0
    return len(tag.get_text(" ", strip=True))


def find_best_content(soup):
    selectors = [
        "article",
        "main",
        ".entry-content",
        ".post-content",
        ".td-post-content",
        ".jeg_singlepage",
        ".jeg_main_content",
        "[class*=article]",
        "[class*=content]",
    ]
    candidates = []

    for selector in selectors:
        candidates.extend(soup.select(selector))

    return max(candidates, key=content_length, default=soup)


def scrape_url(url):
    try:
        print(f"[SCRAPER] Fetching: {url}")

        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        article = find_best_content(soup)
        paragraphs = article.find_all("p")
        text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)

        if len(text) < 200:
            text = article.get_text(" ", strip=True)

        if len(text) < 200:
            text = soup.get_text(" ", strip=True)

        text = " ".join(text.split())

        if len(text) < 200:
            return None

        return {
            "url": url,
            "content": text[:6000],
        }

    except Exception as e:
        print("[SCRAPER ERROR]", url, e)
        return None

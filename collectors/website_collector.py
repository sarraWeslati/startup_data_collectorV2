# collectors/website_collector.py

import asyncio
import requests
from bs4 import BeautifulSoup

try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except Exception:
    CRAWL4AI_AVAILABLE = False


def clean_text(text: str) -> str:
    """
    Nettoyage basique du texte.
    """

    if not text:
        return ""

    lines = text.splitlines()

    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


def fallback_scrape(url: str) -> str:
    """
    Fallback Requests + BeautifulSoup.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for tag in soup([
        "script",
        "style",
        "noscript",
        "iframe"
    ]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    return clean_text(text)


async def crawl4ai_scrape(url: str) -> str:
    """
    Scraping avec Crawl4AI.
    """

    async with AsyncWebCrawler() as crawler:

        result = await crawler.arun(
            url=url
        )

        if not result:
            return ""

        markdown = getattr(
            result,
            "markdown",
            ""
        )

        return clean_text(markdown)


async def scrape_url(url: str) -> str:
    """
    Fonction principale.
    """

    print(f"[SCRAPING] {url}")

    if CRAWL4AI_AVAILABLE:

        try:

            content = await crawl4ai_scrape(url)

            if content and len(content) > 100:
                print("[OK] Crawl4AI")
                return content

            print(
                "[WARNING] Crawl4AI a retourné peu de contenu."
            )

        except Exception as e:

            print(
                f"[ERROR] Crawl4AI : {e}"
            )

    try:

        content = fallback_scrape(url)

        print("[OK] Fallback Requests")

        return content

    except Exception as e:

        print(
            f"[ERROR] Fallback : {e}"
        )

        return ""


async def scrape_multiple_urls(
    urls: list[str]
) -> dict:
    """
    Scraping multiple URLs.
    """

    results = {}

    for url in urls:

        try:

            content = await scrape_url(url)

            results[url] = content

        except Exception as e:

            print(
                f"[ERROR] {url} : {e}"
            )

            results[url] = ""

    return results


# Test local

if __name__ == "__main__":

    async def test():

        urls = [
            "https://startup.gov.tn",
            "https://216capital.vc"
        ]

        results = await scrape_multiple_urls(
            urls
        )

        for url, content in results.items():

            print("\n" + "=" * 50)
            print(url)
            print("=" * 50)

            print(content[:1000])

    asyncio.run(test())
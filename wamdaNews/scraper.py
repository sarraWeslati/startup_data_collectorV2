# scraper.py

import asyncio
import re
from urllib.parse import urljoin, urlparse

import requests
import trafilatura
from bs4 import BeautifulSoup

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode
)


WAMDA_BASE = "https://www.wamda.com"
WAMDA_NEWS = "https://www.wamda.com/news"
WAMDA_SECTIONS = (
    "https://www.wamda.com/news",
    "https://www.wamda.com/articles",
)
MAX_CONSECUTIVE_FAILED_PAGES = 2
ARTICLE_CRAWL_DELAY_SECONDS = 6
ARTICLE_CONCURRENCY = 1
ARTICLE_PREVIEWS = {}

BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    "Referer": WAMDA_BASE,
}


# ---------------------------------------------------------
# Configuration Crawl4AI
# ---------------------------------------------------------

browser_config = BrowserConfig(
    headless=True,
    verbose=False,
    enable_stealth=True,
    user_agent=BROWSER_USER_AGENT,
    headers=BROWSER_HEADERS,
    viewport_width=1366,
    viewport_height=768,
)


crawler_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    word_count_threshold=20,
    remove_overlay_elements=True,
    process_iframes=False,
    simulate_user=True,
    override_navigator=True,
    magic=True,
    delay_before_return_html=1.5,
    mean_delay=2.0,
    max_range=1.5,
    page_timeout=30000,
    verbose=False,
    user_agent=BROWSER_USER_AGENT,
)


# ---------------------------------------------------------
# Nettoyage URL
# ---------------------------------------------------------

def clean_url(url):

    url = url.split("?")[0]
    url = url.rstrip("/")

    return url



# ---------------------------------------------------------
# DÃ©tection article Wamda
# ---------------------------------------------------------

def is_article(url):

    parsed = urlparse(url)
    path = parsed.path.rstrip("/")

    skip_patterns = [
        "/tag/",
        "/tags/",
        "/author/",
        "/authors/",
        "/category/",
        "/categories/",
        "/about",
        "/contact",
        "/events",
        "/research",
        "/podcasts",
        "/partner-projects",
    ]

    if any(p in path for p in skip_patterns):
        return False

    if re.match(r"^/\d{4}/\d{2}/[a-z0-9-]+$", path):
        return True

    patterns = [
        "/articles/",
        "/startup/",
        "/investment/",
        "/news/"
    ]

    return any(
        p in path
        for p in patterns
    )



# ---------------------------------------------------------
# Extraction des liens
# ---------------------------------------------------------

def extract_links(html):

    links = set()

    matches = re.findall(
        r'href=["\'](.*?)["\']',
        html
    )

    for link in matches:

        if link.startswith("/"):

            link = urljoin(
                WAMDA_BASE,
                link
            )

        if link.startswith("http"):

            link = clean_url(link)

            if "wamda.com" in link:
                links.add(link)


    return links


def extract_article_previews(html):

    previews = {}

    try:

        soup = BeautifulSoup(
            html or "",
            "lxml"
        )

    except Exception:

        soup = BeautifulSoup(
            html or "",
            "html.parser"
        )

    for anchor in soup.find_all("a", href=True):

        link = anchor["href"]

        if link.startswith("/"):

            link = urljoin(
                WAMDA_BASE,
                link
            )

        link = clean_url(link)

        if not is_article(link):

            continue

        container = anchor

        for _ in range(5):

            parent = container.parent

            if not parent:

                break

            text = parent.get_text(
                " ",
                strip=True
            )

            if len(text) > 120:

                container = parent

                break

            container = parent

        text = container.get_text(
            " ",
            strip=True
        )

        if len(text) > 80:

            previews[link] = text[:3000]

    return previews


def fetch_article_with_requests(url):

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": BROWSER_USER_AGENT,
                **BROWSER_HEADERS,
            },
            timeout=20
        )

        if response.status_code == 403:

            return None

        response.raise_for_status()

        extracted = trafilatura.extract(
            response.text,
            url=url,
            include_comments=False,
            include_tables=False,
        )

        if extracted and len(extracted) > 200:

            return {
                "url": url,
                "markdown": extracted,
                "html": response.text
            }

    except Exception as e:

        print(
            "[REQUESTS FALLBACK ERROR]",
            url,
            e
        )

    return None


def get_crawl_error(result):

    for attr in ("error_message", "error", "status_code"):

        value = getattr(result, attr, None)

        if value:

            return str(value)

    return ""



# ---------------------------------------------------------
# DÃ©couverte de toutes les pages articles
# ---------------------------------------------------------

async def discover_articles(
        crawler,
        max_pages=200
):

    print("ðŸ”Ž Discovering Wamda articles...")


    articles = set()


    for section_url in WAMDA_SECTIONS:

        failed_pages = 0

        for page in range(1, max_pages + 1):

            if page == 1:

                url = section_url

            else:

                url = (
                    f"{section_url}"
                    f"?page={page}"
                )


            print(
                f"[DISCOVERY] {section_url} page {page}"
            )


            try:

                result = await crawler.arun(
                    url=url,
                    config=crawler_config
                )


                if not result.success:

                    failed_pages += 1

                    error = get_crawl_error(
                        result
                    )

                    print(
                        f"  ! skipped page {page}: {error or 'crawl failed'}"
                    )

                    if "403" in error or failed_pages >= MAX_CONSECUTIVE_FAILED_PAGES:

                        print(
                            f"  ! stopping {section_url}: Wamda blocked or pages are unavailable"
                        )

                        break

                    continue

                failed_pages = 0


                links = extract_links(
                    result.html
                )

                ARTICLE_PREVIEWS.update(
                    extract_article_previews(result.html)
                )


                before = len(articles)


                for link in links:

                    if is_article(link):

                        articles.add(link)



                after = len(articles)



                print(
                    f"  +{after-before} articles"
                )



                # arrÃªt automatique
                if after == before:

                    if page > 5:

                        break



            except Exception as e:

                print(
                    "[DISCOVERY ERROR]",
                    e
                )



    print(
        f"âœ… Total articles found : {len(articles)}"
    )


    return list(articles)




# ---------------------------------------------------------
# Crawl d'un article
# ---------------------------------------------------------

async def crawl_article(
        crawler,
        url
):


    try:

        result = await crawler.arun(
            url=url,
            config=crawler_config
        )


        if not result.success:

            fallback = await asyncio.to_thread(
                fetch_article_with_requests,
                url
            )

            if fallback:

                print(
                    "[CRAWL FALLBACK]",
                    url
                )

                return fallback

            preview = ARTICLE_PREVIEWS.get(
                clean_url(url)
            )

            if preview:

                print(
                    "[CRAWL PREVIEW]",
                    url
                )

                return {
                    "url": url,
                    "markdown": preview,
                    "html": ""
                }

            print(
                "[CRAWL SKIP]",
                url,
                get_crawl_error(result) or "crawl failed"
            )

            return None



        markdown = result.markdown



        if not markdown:

            return None



        return {

            "url": url,

            "markdown": markdown,

            "html": result.html

        }



    except Exception as e:

        print(
            "[CRAWL ERROR]",
            url,
            e
        )

        return None




# ---------------------------------------------------------
# Crawl complet
# ---------------------------------------------------------

async def crawl_all_articles(
        max_pages=200
):


    async with AsyncWebCrawler(
        config=browser_config
    ) as crawler:


        urls = await discover_articles(
            crawler,
            max_pages
        )


        print(
            "\nðŸš€ Crawling articles..."
        )


        articles = []


        semaphore = asyncio.Semaphore(ARTICLE_CONCURRENCY)



        async def worker(url):

            async with semaphore:

                await asyncio.sleep(
                    ARTICLE_CRAWL_DELAY_SECONDS
                )

                data = await crawl_article(
                    crawler,
                    url
                )

                if data:

                    articles.append(data)



        tasks = [

            worker(url)

            for url in urls

        ]


        await asyncio.gather(
            *tasks
        )



        print(
            f"âœ… Crawled : {len(articles)}"
        )


        return articles



# ---------------------------------------------------------
# Test direct
# ---------------------------------------------------------

if __name__ == "__main__":


    data = asyncio.run(
        crawl_all_articles()
    )


    print(
        len(data)
    )

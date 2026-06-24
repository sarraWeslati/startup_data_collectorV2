import requests
import trafilatura

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def scrape_article(url):

    try:
        response = requests.get(url, headers=HEADERS, timeout=12)

        if response.status_code != 200:
            return None

        text = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=False,
            favor_recall=False
        )

        if text:
            text = " ".join(text.split())  # clean whitespace

        return text

    except Exception as e:
        print(f"[SCRAPER ERROR] {url}: {e}")
        return None
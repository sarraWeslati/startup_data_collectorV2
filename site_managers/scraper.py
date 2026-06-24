import requests
import trafilatura


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def scrape_article(url):

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)

        if response.status_code != 200:
            print(f"❌ HTTP error {response.status_code}")
            return None

        downloaded = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=False
        )

        if not downloaded:
            return None

        return downloaded

    except Exception as e:
        print(f"❌ scraping error {url}: {e}")
        return None
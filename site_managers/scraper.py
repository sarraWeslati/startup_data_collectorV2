import requests
import trafilatura

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_article(url):

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            return None, None

        text = trafilatura.extract(r.text)

        if not text:
            return None, None

        metadata = trafilatura.extract_metadata(r.text)
        date = metadata.date if metadata and metadata.date else ""

        return " ".join(text.split()), date

    except Exception as e:
        print("[SCRAPER ERROR]", e)
        return None, None
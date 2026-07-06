import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}


def scrape_url(url):
    try:
        print(f"[SCRAPER] Fetching: {url}")

        r = requests.get(url, headers=HEADERS, timeout=20)

        soup = BeautifulSoup(r.text, "lxml")

        # remove noise
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # extract better content
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])

        if len(text) < 200:
            text = soup.get_text(" ", strip=True)

        return {
            "url": url,
            "content": text[:6000]
        }

    except Exception as e:
        print("[SCRAPER ERROR]", e)
        return None
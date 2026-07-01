import requests
from bs4 import BeautifulSoup
from config import HEADERS


def scrape(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)

        if r.status_code != 200:
            print(f"❌ SCRAPE FAIL {url} -> {r.status_code}")
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # enlever scripts inutiles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        lines = [t.strip() for t in text.splitlines() if t.strip()]

        return "\n".join(lines)

    except Exception as e:
        print("Scraper error:", e)
        return None
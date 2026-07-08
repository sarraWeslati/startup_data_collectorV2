from bs4 import BeautifulSoup
from http_client import fetch


def parse(html):
    try:
        return BeautifulSoup(html, "lxml")
    except:
        return BeautifulSoup(html, "html.parser")


def scrape_url(url):
    try:
        html = fetch(url)

        if not html:
            return None

        soup = parse(html)

        for t in soup(["script", "style", "noscript"]):
            t.decompose()

        text = soup.get_text(" ", strip=True)

        if len(text) < 200:
            return None

        return {
            "url": url,
            "content": text[:6000]
        }

    except:
        return None
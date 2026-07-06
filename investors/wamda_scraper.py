import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_articles(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    articles = []

    for block in soup.select("article, .post, .news-item, .card"):
        text = block.get_text(" ", strip=True)

        if len(text) > 200:
            articles.append({
                "text": text
            })

    return articles
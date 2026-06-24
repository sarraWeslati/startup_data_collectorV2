import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_article_links(base_url, max_pages=75):

    page = 1
    all_links = set()

    while page <= max_pages:

        url = f"{base_url}?paged={page}"
        print(f"📄 Crawling page {page}: {url}")

        try:
            r = requests.get(url, headers=HEADERS, timeout=10)

            if r.status_code != 200:
                break

            soup = BeautifulSoup(r.text, "html.parser")

            articles = soup.select("a[href*='/202']")  # plus précis

            new_links = 0

            for a in articles:
                href = a.get("href")

                if href and "managers.tn" in href:
                    if href not in all_links:
                        all_links.add(href)
                        new_links += 1

            if new_links == 0:
                break

            page += 1

        except Exception as e:
            print(f"❌ ERROR page {page}: {e}")
            break

    return list(all_links)
import requests
from bs4 import BeautifulSoup


def get_article_links(base_url):

    page = 1
    all_links = set()

    while True:

        url = f"{base_url}?paged={page}"
        print(f"📄 Crawling page {page}: {url}")

        try:
            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                break

            soup = BeautifulSoup(r.text, "html.parser")

            links = soup.find_all("a")

            new_links = 0

            for a in links:
                href = a.get("href")

                if href and "managers.tn" in href:
                    if "/2026/" in href or "/2025/" in href:
                        if href not in all_links:
                            all_links.add(href)
                            new_links += 1

            # 🛑 stop condition
            if new_links == 0:
                break

            page += 1

        except Exception as e:
            print(f"ERROR page {page}: {e}")
            break

    return list(all_links)
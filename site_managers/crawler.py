import requests
from bs4 import BeautifulSoup


HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_article_links(base_urls, limit=None, max_pages=200):
    if isinstance(base_urls, str):
        base_urls = [base_urls]

    links = []
    seen = set()

    for base_url in base_urls:
        print(f"\nCrawling category: {base_url}")

        for page in range(1, max_pages + 1):
            url = f"{base_url}?paged={page}"
            print(f"Page {page}")

            try:
                response = requests.get(url, headers=HEADERS, timeout=10)

                if response.status_code != 200:
                    print("End of pagination (HTTP)")
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                found = False

                for link in soup.find_all("a", href=True):
                    href = link["href"]

                    if (
                        "managers.tn" in href
                        and ("/2025/" in href or "/2026/" in href)
                        and "/category/" not in href
                        and href not in seen
                    ):
                        seen.add(href)
                        links.append(href)
                        found = True

                print(f"Total links: {len(links)}")

                if limit and len(links) >= limit:
                    print("Limit reached")
                    return links[:limit]

                if not found:
                    print("No links found, stopping pagination")
                    break

            except Exception as e:
                print("CRAWLER ERROR:", e)
                break

    return links

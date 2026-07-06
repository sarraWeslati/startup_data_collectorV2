import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0"}


def expand_urls(urls):
    all_urls = set()

    for url in urls:
        try:
            print(f"[EXPANDING] {url}")

            r = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "lxml")

            links = soup.find_all("a", href=True)

            for a in links:
                href = a["href"]

                full_url = urljoin(url, href)

                # filter only useful news links
                if any(x in full_url.lower() for x in [
                    "news", "article", "202", "blog", "insight", "report", "startup"
                ]):
                    all_urls.add(full_url)

        except Exception as e:
            print("[EXPAND ERROR]", e)

    return list(all_urls)
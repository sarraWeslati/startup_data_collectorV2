import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_article_links(category_url):

    r = requests.get(category_url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    links = set()

    for a in soup.select("a[href]"):
        href = a["href"]

        # garder uniquement articles managers.tn
        if "managers.tn/" in href and "/category/" not in href:
            if href.startswith("https://managers.tn/"):
                links.add(href)

    return list(links)


def get_all_pages(base_url, max_pages=10):

    pages = [base_url]

    for i in range(2, max_pages + 1):
        pages.append(f"{base_url}page/{i}/")

    return pages
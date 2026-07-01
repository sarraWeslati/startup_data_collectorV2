from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

BLACKLIST = [
    "login", "signup", "privacy", "terms",
    "facebook", "twitter", "linkedin"
]

def is_valid(url):
    url = url.lower()
    return all(b not in url for b in BLACKLIST)

def get_links(base_url):
    try:
        r = requests.get(base_url, timeout=20)

        soup = BeautifulSoup(r.text, "html.parser")

        links = []

        for a in soup.find_all("a", href=True):
            full = urljoin(base_url, a["href"])

            # 🔥 ONLY SHIZUNE
            if "shizune.co" in full and is_valid(full):
                links.append(full)

        return list(set(links))

    except Exception as e:
        print("Crawler error:", e)
        return []
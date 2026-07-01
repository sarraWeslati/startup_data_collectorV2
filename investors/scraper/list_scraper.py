import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json


HEADERS = {"User-Agent": "Mozilla/5.0"}

KEYWORDS = [
    "invest", "vc", "capital", "fund",
    "portfolio", "startup", "accelerator",
    "angel", "partner", "investment"
]


def is_relevant(text, url):
    text = (text or "").lower()
    url = (url or "").lower()

    combined = text + " " + url

    return any(k in combined for k in KEYWORDS)


def scrape_links(url):

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        results = []

        for a in soup.find_all("a"):

            name = a.get_text(strip=True)
            link = a.get("href")

            if not link:
                continue

            # ❌ skip useless links
            if (
                link.startswith("#")
                or "javascript" in link.lower()
                or link.lower().startswith(("mailto:", "tel:"))
            ):
                continue

            # ✅ fix URL properly
            link = urljoin(url, link)

            if not name:
                continue

            # 🔥 SMART FILTER (IMPORTANT FIX)
            if not is_relevant(name, link):
                continue

            # extra noise filter
            if len(name) < 2:
                continue

            results.append({
                "name": name,
                "url": link,
                "source": url
            })

        return results

    except Exception as e:
        print(f"❌ Error {url}: {e}")
        return []


def run(sources_file, output_file):

    all_links = []

    with open(sources_file, "r", encoding="utf-8") as f:
        urls = []

        for line in f:
            line = line.strip()

            if not line:
                continue
            if line.startswith("#"):
                continue
            if not line.startswith("http"):
                continue

            urls.append(line)

    print(f"🔎 Sources: {len(urls)}")

    for url in urls:
        print(f"\nScraping: {url}")

        data = scrape_links(url)
        all_links.extend(data)

        print(f"  → {len(data)} links found")

    # dedup
    unique = {}
    for item in all_links:
        unique[item["url"]] = item

    final = list(unique.values())

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(final)} cleaned links")

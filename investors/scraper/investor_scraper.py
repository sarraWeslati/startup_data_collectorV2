import requests
from bs4 import BeautifulSoup


def scrape_investor_profile(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        name = soup.title.text.strip() if soup.title else ""

        paragraphs = soup.find_all("p")
        description = " ".join([p.get_text(strip=True) for p in paragraphs[:3]])

        return {
            "name": name,
            "website": "",
            "country": "",
            "description": description,
            "source_url": url
        }

    except Exception as e:
        print(f"Error profile {url}: {e}")
        return None


def run_profile_scraper(input_file, output_file):
    import json

    with open(input_file, "r", encoding="utf-8") as f:
        investors = json.load(f)

    results = []

    for i, inv in enumerate(investors):
        print(f"[{i+1}/{len(investors)}] {inv['name']}")

        data = scrape_investor_profile(inv["profile_url"])

        if data:
            results.append(data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(results)} investor profiles")
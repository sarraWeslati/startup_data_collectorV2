import json
from pathlib import Path

from crawler import get_article_links
from scraper import scrape_article
from extractor import extract_structured_data


BASE_URL = "https://managers.tn/category/startup/"


def main():
    print("🚀 START CLEAN SCRAPING")

    links = get_article_links(BASE_URL)

    if not links:
        print("❌ No links found")
        return

    results = []

    for i, url in enumerate(links):

        print(f"[{i+1}/{len(links)}] {url}")

        text = scrape_article(url)

        if not text or len(text) < 200:
            print("⚠️ skipped empty article")
            continue

        title = text.split("\n")[0][:120]  # meilleur fallback

        data = extract_structured_data(url, title, text)

        if data:
            results.append(data)

    # dossier storage
    Path("storage").mkdir(exist_ok=True)

    output_path = Path("storage/startups_clean.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ DONE CLEAN DATA -> {output_path}")


if __name__ == "__main__":
    main()
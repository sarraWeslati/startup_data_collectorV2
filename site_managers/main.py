import json
from pathlib import Path

from crawler import get_article_links
from scraper import scrape_article
from extractor import extract_structured_data

BASE_URL = "https://managers.tn/category/startup/"


def main():

    print("🚀 SMART LLM SCRAPING PIPELINE STARTED")

    links = get_article_links(BASE_URL)

    results = []

    for i, url in enumerate(links):

        print(f"[{i+1}/{len(links)}] Processing {url}")

        text = scrape_article(url)

        if not text:
            continue

        title = text[:120]

        data = extract_structured_data(url, title, text)

        if data:
            results.append(data)

    Path("storage").mkdir(exist_ok=True)

    with open("storage/startups_final.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("\n✅ DONE - CLEAN + INTELLIGENT DATA READY")


if __name__ == "__main__":
    main()
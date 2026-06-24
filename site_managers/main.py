import json
from pathlib import Path

from crawler import get_article_links
from scraper import scrape_article
from extractor import extract_structured_data

BASE_URL = "https://managers.tn/category/startup/"


def main():

    print("🚀 SMART SCRAPING PIPELINE STARTED")

    # 🎯 MODE INTERACTIF
    print("\nChoisis le mode :")
    print("1 - TEST (20 articles)")
    print("2 - FULL (tous les articles)")

    choice = input("👉 Tape 1 ou 2 : ").strip()

    links = get_article_links(BASE_URL)

    if choice == "1":
        links = links[:10]
        print(f"🧪 MODE TEST ACTIVÉ : {len(links)} articles")

    elif choice == "2":
        print(f"🚀 MODE FULL ACTIVÉ : {len(links)} articles")

    else:
        print("❌ Choix invalide, mode TEST par défaut")
        links = links[:10]

    results = []

    for i, url in enumerate(links):

        print(f"[{i+1}/{len(links)}] {url}")

        text = scrape_article(url)

        if not text:
            continue

        title = text[:120]

        data = extract_structured_data(url, title, text)

        if data:
            results.append(data)

    Path("storage").mkdir(exist_ok=True)

    filename = "startups_test.json" if choice == "1" else "startups_full.json"

    with open(f"storage/{filename}", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ DONE → {filename} created")


if __name__ == "__main__":
    main()
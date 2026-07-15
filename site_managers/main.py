from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import sys

from crawler import get_article_links
from extractor import find_country
from llm import llm_extract
from scraper import scrape_article


BASE_URL = "https://managers.tn/category/startup/"
MAX_WORKERS = 3
ROOT_DIR = Path(__file__).resolve().parent
STORAGE_DIR = ROOT_DIR / "storage"


def process_article(url):
    try:
        text, date = scrape_article(url)
        if not text:
            return None

        title = text.split(".")[0][:250]

        result = llm_extract(url, title, text)
        entity_type = result.get("entity_type", "other")
        data = result.get("data", {}) or {}

        if entity_type in ("startup", "investor") and not data.get("country"):
            data["country"] = find_country(text)

        data["entity_type"] = entity_type
        data["date"] = date
        data["source_article"] = {
            "url": url,
            "title": title,
            "content": text,
        }

        return data

    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    print("START MANAGERS PIPELINE")

    if len(sys.argv) > 1:
        mode = sys.argv[1].strip().lower()
    else:
        mode = input("Mode (20 / full): ").strip().lower()

    links = get_article_links(BASE_URL)

    if mode == "20":
        links = links[:20]
        print("TEST MODE")
    else:
        print("FULL MODE")

    print(f"Total links: {len(links)}")
    print(f"Workers: {MAX_WORKERS}")

    startups = []
    investors = []
    others = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_article, url): url for url in links}

        for completed, future in enumerate(as_completed(futures), start=1):
            url = futures[future]
            print(f"[{completed}/{len(links)}] Done: {url}")

            try:
                data = future.result()
                if not data:
                    continue

                entity_type = data.get("entity_type", "other")

                if entity_type == "startup":
                    startups.append(data)
                elif entity_type == "investor":
                    investors.append(data)
                else:
                    others.append(data)

            except Exception as e:
                print(f"[PROCESS ERROR] {url}: {e}")

    save_json(STORAGE_DIR / "startups.json", startups)
    save_json(STORAGE_DIR / "investors.json", investors)
    save_json(STORAGE_DIR / "articles.json", others)

    print("\n================================")
    print("DONE")
    print("STARTUPS :", len(startups))
    print("INVESTORS:", len(investors))
    print("OTHERS   :", len(others))
    print("================================")


if __name__ == "__main__":
    main()
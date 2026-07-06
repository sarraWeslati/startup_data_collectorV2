from scraper import scrape_url
from llm_extractor import safe_extract
from utils import save_news


def run_pipeline(urls):
    print("🚀 START PIPELINE")

    for url in urls:
        try:
            print(f"[PROCESSING] {url}")

            scraped = scrape_url(url)
            if not scraped:
                continue

            result = safe_extract(scraped["content"], url)

            if not result:
                print(f"[SKIP] {url}")
                continue

            save_news(result)
            print(f"[SAVED] {url}")

        except Exception as e:
            print("[ERROR]", e)

    print("✅ DONE PIPELINE")
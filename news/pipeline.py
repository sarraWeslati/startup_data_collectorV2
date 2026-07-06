from concurrent.futures import ThreadPoolExecutor, as_completed

from config import MAX_ARTICLES, PIPELINE_WORKERS
from scraper import scrape_url
from llm_extractor import safe_extract
from utils import existing_sources, save_news_batch


def process_url(url):
    try:
        print(f"[PROCESSING] {url}")

        scraped = scrape_url(url)
        if not scraped:
            return None

        result = safe_extract(scraped["content"], url)

        if not result:
            print(f"[SKIP] {url}")
            return None

        result["source"] = result.get("source") or url
        print(f"[EXTRACTED] {url}")
        return result

    except Exception as e:
        print("[ERROR]", url, e)
        return None


def run_pipeline(urls):
    print("START PIPELINE")

    already_saved = existing_sources()
    pending_urls = [url for url in urls if url not in already_saved]

    if MAX_ARTICLES > 0:
        pending_urls = pending_urls[:MAX_ARTICLES]

    print(f"[INFO] URLs to process: {len(pending_urls)}")

    results = []
    seen_sources = set()

    with ThreadPoolExecutor(max_workers=PIPELINE_WORKERS) as executor:
        futures = {executor.submit(process_url, url): url for url in pending_urls}

        for future in as_completed(futures):
            result = future.result()
            if not result:
                continue

            source = result.get("source")
            if source in seen_sources:
                continue

            seen_sources.add(source)
            results.append(result)

    saved_count = save_news_batch(results)

    print(f"DONE PIPELINE - saved {saved_count} new articles")

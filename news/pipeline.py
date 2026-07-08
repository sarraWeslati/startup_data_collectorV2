from concurrent.futures import ThreadPoolExecutor, as_completed

from config import MAX_ARTICLES, PIPELINE_WORKERS
from llm_extractor import safe_extract
from scraper import scrape_url
from utils import existing_sources, save_news_batch


def short_url(url, limit=110):
    if len(url) <= limit:
        return url
    return url[: limit - 3] + "..."


def process_scrape(url):
    try:
        scraped = scrape_url(url)
        if not scraped:
            return "skip", url, None

        content_length = len(scraped.get("content", ""))
        if content_length < 500:
            return "short", url, content_length

        return "ok", url, scraped

    except Exception as e:
        return "error", url, str(e)


def process_llm(item):
    url = item["url"]

    try:
        result = safe_extract(item["content"], url)
        if not result:
            return "skip", url, None

        result["source"] = result.get("source") or url
        return "ok", url, result

    except Exception as e:
        return "error", url, str(e)


def run_pipeline(urls):
    print("START PIPELINE", flush=True)

    already_saved = set(existing_sources())
    urls = [url for url in urls if url not in already_saved]

    if MAX_ARTICLES > 0:
        urls = urls[:MAX_ARTICLES]

    print(f"[INFO] URLs to process: {len(urls)}", flush=True)

    scraped = []
    scrape_ok = 0
    scrape_skip = 0
    scrape_error = 0
    scrape_workers = PIPELINE_WORKERS * 3

    print(f"[STEP 1/3] Scraping started with {scrape_workers} workers", flush=True)

    with ThreadPoolExecutor(max_workers=scrape_workers) as executor:
        futures = {executor.submit(process_scrape, url): url for url in urls}
        total = len(futures)

        for index, future in enumerate(as_completed(futures), start=1):
            original_url = futures[future]

            try:
                status, url, payload = future.result()
            except Exception as e:
                scrape_error += 1
                print(f"[SCRAPE ERROR] {short_url(original_url)} {e}", flush=True)
                continue

            if status == "ok":
                scrape_ok += 1
                scraped.append(payload)
            elif status == "short":
                scrape_skip += 1
                print(f"[SCRAPE SHORT] {short_url(url)} content_length={payload}", flush=True)
            elif status == "skip":
                scrape_skip += 1
                print(f"[SCRAPE SKIP] {short_url(url)}", flush=True)
            else:
                scrape_error += 1
                print(f"[SCRAPE ERROR] {short_url(url)} {payload}", flush=True)

            if index % 10 == 0 or index == total:
                print(
                    f"[SCRAPE PROGRESS] {index}/{total} done | "
                    f"ok={scrape_ok} skip={scrape_skip} error={scrape_error}",
                    flush=True,
                )

    print(
        f"[STEP 1/3 DONE] scraped={len(scraped)} "
        f"skip={scrape_skip} error={scrape_error}",
        flush=True,
    )

    results = []
    llm_ok = 0
    llm_skip = 0
    llm_error = 0
    llm_workers = PIPELINE_WORKERS * 2

    print(
        f"[STEP 2/3] LLM extraction started for {len(scraped)} articles "
        f"with {llm_workers} workers",
        flush=True,
    )

    with ThreadPoolExecutor(max_workers=llm_workers) as executor:
        futures = {executor.submit(process_llm, item): item for item in scraped}
        total = len(futures)

        for index, future in enumerate(as_completed(futures), start=1):
            item = futures[future]

            try:
                status, url, payload = future.result()
            except Exception as e:
                llm_error += 1
                print(f"[LLM ERROR] {short_url(item['url'])} {e}", flush=True)
                continue

            if status == "ok":
                llm_ok += 1
                results.append(payload)
            elif status == "skip":
                llm_skip += 1
                print(f"[LLM SKIP] {short_url(url)}", flush=True)
            else:
                llm_error += 1
                print(f"[LLM ERROR] {short_url(url)} {payload}", flush=True)

            print(
                f"[LLM PROGRESS] {index}/{total} done | "
                f"ok={llm_ok} skip={llm_skip} error={llm_error}",
                flush=True,
            )

    print(
        f"[STEP 2/3 DONE] extracted={len(results)} "
        f"skip={llm_skip} error={llm_error}",
        flush=True,
    )

    print(f"[STEP 3/3] Saving {len(results)} extracted articles", flush=True)
    saved = save_news_batch(results)

    print(f"DONE PIPELINE - saved {saved}", flush=True)

from config import URLS
from pipeline import run_pipeline
from crawler import expand_urls

if __name__ == "__main__":
    print("🚀 START SYSTEM")

    expanded_urls = expand_urls(URLS)

    print(f"[INFO] Total URLs after expansion: {len(expanded_urls)}")

    run_pipeline(expanded_urls)
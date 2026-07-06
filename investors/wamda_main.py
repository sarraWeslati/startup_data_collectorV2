import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from wamda_scraper import scrape_articles
from extractorwamda import extract_wamda
from storagewamda import save_all


# =========================
# ⚡ CONFIG
# =========================
MAX_WORKERS = 2  # 🔥 speed boost
URL = "https://wamdacapital.com/news/"


# =========================
# 🧠 PROCESS ARTICLE
# =========================
def process_article(article):
    text = article.get("text")

    data = extract_wamda(text)

    return data


# =========================
# 🚀 RUN PIPELINE
# =========================
def run():
    print("🚀 WAMDA PIPELINE START")

    articles = scrape_articles(URL)

    print(f"📦 Articles found: {len(articles)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = [
            executor.submit(process_article, a)
            for a in articles
        ]

        for i, f in enumerate(as_completed(futures)):
            data = f.result()

            if not data:
                continue

            print(f"\n💾 Saving article {i+1}")

            # 🔥 SAVE IMMÉDIATEMENT
            save_all(data)

    print("\n✅ DONE")


if __name__ == "__main__":
    run()
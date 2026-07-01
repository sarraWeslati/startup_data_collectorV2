import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from extractor import extract_from_shizune
from storage import save_data, load_existing


TARGET_URLS = [
    "https://shizune.co/investors/investors-tunisia",
    "https://shizune.co/investors/investors-africa"
]

MAX_WORKERS = 4

queue = deque(TARGET_URLS)
visited = set()
lock = threading.Lock()


def process(url):

    with lock:
        if url in visited:
            return None
        visited.add(url)

    print("🔍 scraping:", url)

    data = extract_from_shizune(url)

    return data


def run():

    existing = load_existing()

    print("🚀 START PIPELINE")
    print("📦 existing:", len(existing))

    batch = []

    while queue:

        chunk = []

        with lock:
            while queue and len(chunk) < MAX_WORKERS:
                chunk.append(queue.popleft())

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            results = ex.map(process, chunk)

            for res in results:
                if res:
                    batch.extend(res)

        if len(batch) > 0:

            print("\n💥 SAVING BATCH")

            added = save_data(batch)

            print(f"📊 added: {added}")

            batch = []

        time.sleep(1)

    print("✅ DONE")


if __name__ == "__main__":
    run()
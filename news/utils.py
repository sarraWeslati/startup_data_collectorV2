import json
import os
import threading

FILE = os.path.join(os.path.dirname(__file__), "news.json")
lock = threading.Lock()


def normalize_url(url):
    if not url:
        return ""
    return url.rstrip("/")


def load_data():
    if not os.path.exists(FILE):
        return []

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception:
        return []


def save_news(item):
    return save_news_batch([item])


def existing_sources():
    return {normalize_url(item.get("source")) for item in load_data() if item.get("source")}


def save_news_batch(items):
    if not items:
        return 0

    with lock:
        data = load_data()
        sources = {normalize_url(item.get("source")) for item in data if item.get("source")}
        new_items = []

        for item in items:
            source = normalize_url(item.get("source"))
            if source and source in sources:
                continue

            if source:
                sources.add(source)

            new_items.append(item)

        if not new_items:
            print("[SAVED OK] 0 new articles")
            return 0

        data.extend(new_items)

        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[SAVED OK] {len(new_items)} new articles")
    return len(new_items)

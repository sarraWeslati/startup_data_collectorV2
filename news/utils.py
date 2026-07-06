import json
import os
import threading

FILE = "news.json"
lock = threading.Lock()


def load_data():
    if not os.path.exists(FILE):
        return []

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except:
        return []


def save_news(item):
    with lock:
        data = load_data()
        data.append(item)

        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    print("[SAVED OK]")
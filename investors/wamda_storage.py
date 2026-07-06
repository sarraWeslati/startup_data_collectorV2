import json
from config import OUTPUT_NEWS, OUTPUT_STARTUPS, OUTPUT_INVESTORS

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_json(path, new_items):
    data = load_json(path)

    existing = set()
    for i in data:
        if isinstance(i, dict):
            existing.add(i.get("title") or i.get("name"))

    added = 0

    for item in new_items:
        key = item.get("title") or item.get("name")
        if not key or key in existing:
            continue
        data.append(item)
        existing.add(key)
        added += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return added


def save_all(data):
    news = data.get("news", [])

    investors = []
    startups = []

    for n in news:
        investors.extend(n.get("investors", []))
        startups.extend(n.get("startups", []))

    a1 = save_json(OUTPUT_NEWS, news)
    a2 = save_json(OUTPUT_INVESTORS, investors)
    a3 = save_json(OUTPUT_STARTUPS, startups)

    print(f"💾 news={a1} investors={a2} startups={a3}")
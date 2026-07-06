import json
from config import OUTPUT_NEWS, OUTPUT_STARTUPS, OUTPUT_INVESTORS


# =========================
# 📥 LOAD JSON SAFE
# =========================
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# =========================
# 💾 SAVE WITH DEDUP
# =========================
def save_json(path, new_items, key_field="name"):

    data = load_json(path)

    existing = set()

    # normalize existing
    for item in data:
        key = (item.get(key_field) or "").strip().lower()
        if key:
            existing.add(key)

    added = 0

    for item in new_items:

        key = (item.get(key_field) or "").strip().lower()

        if not key:
            continue

        if key in existing:
            continue

        data.append(item)
        existing.add(key)
        added += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return added


# =========================
# 🚀 MAIN SAVE LOGIC
# =========================
def save_all(data):

    if not data:
        print("❌ No data to save")
        return

    print("💾 saving...")

    news = data.get("news", [])
    startups = data.get("startups", [])
    investors = data.get("investors", [])

    # 🔥 SAVE INDEPENDENT FILES
    a1 = save_json(OUTPUT_NEWS, news, key_field="title")
    a2 = save_json(OUTPUT_STARTUPS, startups, key_field="name")
    a3 = save_json(OUTPUT_INVESTORS, investors, key_field="name")

    print(f"✅ saved -> news={a1} startups={a2} investors={a3}")
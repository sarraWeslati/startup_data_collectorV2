import json
from config import OUTPUT_FILE


def load_existing():
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {i["name"].lower() for i in data.get("investors", [])}
    except:
        return set()


def save_data(new_investors):

    try:
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {"investors": []}

        existing = {i["name"].lower() for i in data["investors"]}

        added = 0

        for inv in new_investors:
            name = inv["name"].lower()

            if name not in existing:
                data["investors"].append(inv)
                existing.add(name)
                added += 1

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved: {added}")

        return added

    except Exception as e:
        print("Storage error:", e)
        return 0
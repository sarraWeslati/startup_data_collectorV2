import json
from pathlib import Path

# -------------------------------------------------------
# Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

NEWS_FILE = BASE_DIR / "news.json"
OTHER_FILE = BASE_DIR.parent / "site_managers" / "storage" / "other_articles.json"
OUTPUT_FILE = BASE_DIR / "newsAll.json"


# -------------------------------------------------------
# Load JSON
# -------------------------------------------------------

def load_json(path):
    if not path.exists():
        print(f"[WARNING] File not found: {path}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        print(f"[WARNING] {path} is not a list.")
        return []

    except Exception as e:
        print(f"[ERROR] {path}: {e}")
        return []


# -------------------------------------------------------
# Normalize article
# -------------------------------------------------------

def normalize(article):

    source_article = article.get("source_article", {})
    entities = article.get("entities", {})

    return {

        # -----------------------------
        # General
        # -----------------------------
        "entity_type": article.get("entity_type", "other"),
        "category": article.get("category", "news"),

        # -----------------------------
        # Main article
        # -----------------------------
        "title":
            article.get("title")
            or source_article.get("title", ""),

        "summary":
            article.get("summary", ""),

        "content":
            article.get("content")
            or source_article.get("content", ""),

        "url":
            article.get("url")
            or source_article.get("url", ""),

        "country":
            article.get("country", ""),

        "date":
            article.get("date", ""),

        "source":
            article.get("source", ""),

        # -----------------------------
        # Analysis
        # -----------------------------
        "tags":
            article.get("tags", []),

        "relevance":
            article.get("relevance", ""),

        "amounts":
            article.get("amounts", []),

        # -----------------------------
        # Entities
        # -----------------------------
        "entities": {

            "startups":
                entities.get("startups", []),

            "investors":
                entities.get("investors", []),

            "funds":
                entities.get("funds", [])
        },

        # -----------------------------
        # Extra fields
        # -----------------------------
        "others":
            article.get("others", {})
    }


# -------------------------------------------------------
# Merge
# -------------------------------------------------------

def main():

    news_articles = load_json(NEWS_FILE)
    other_articles = load_json(OTHER_FILE)

    merged = []

    for article in news_articles:
        merged.append(normalize(article))

    for article in other_articles:
        merged.append(normalize(article))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=4)

    print("=" * 60)
    print(f"News articles  : {len(news_articles)}")
    print(f"Other articles : {len(other_articles)}")
    print(f"Total merged   : {len(merged)}")
    print(f"Saved          : {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
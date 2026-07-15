import json
import hashlib
import re
from pathlib import Path

# ==========================================================
# Configuration
# ==========================================================

# Racine du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILES = {
    "articles": PROJECT_ROOT / "site_managers" / "storage" / "articles.json",
    "news": PROJECT_ROOT / "news" / "news.json",
    "wamda": PROJECT_ROOT / "wamdaNews" / "storage" / "wamda_news.json",
}

OUTPUT_FILE = PROJECT_ROOT / "cleaningNews" / "merged_news.json"


# ==========================================================
# Utilitaires
# ==========================================================

def load_json(path: Path):
    """Charge un fichier JSON."""
    if not path.exists():
        print(f"[ERREUR] Fichier introuvable : {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        if "articles" in data:
            return data["articles"]
        return [data]

    return data


def normalize_title_key(title: str):
    if not title:
        return ""

    title = title.lower().strip()
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title)

    return title


def make_id(url: str, title: str):
    base = (url or title or "").lower().strip()
    return hashlib.md5(base.encode()).hexdigest()[:12]


# ==========================================================
# Adaptateurs
# ==========================================================

def adapt_articles(item):

    src = item.get("source_article", {})

    return {
        "title": item.get("title", ""),
        "summary": item.get("summary", ""),
        "content": src.get("content", ""),
        "date": item.get("date", ""),
        "country": "",
        "region": "",
        "category": item.get("entity_type", ""),
        "tags": item.get("tags", []),
        "amounts": item.get("amounts", []),
        "relevance": item.get("relevance", ""),
        "entities": {
            "startups": [],
            "investors": [],
            "funds": []
        },
        "funding": {},
        "source_url": src.get("url", ""),
        "origin_file": "articles.json",
    }


def adapt_news(item):

    entities = item.get("entities", {})

    return {
        "title": item.get("title", ""),
        "summary": item.get("summary", ""),
        "content": item.get("content", ""),
        "date": item.get("date", ""),
        "country": item.get("country", ""),
        "region": "",
        "category": item.get("category", ""),
        "tags": [],
        "amounts": [],
        "relevance": "",
        "entities": {
            "startups": entities.get("startups", []),
            "investors": entities.get("investors", []),
            "funds": entities.get("funds", [])
        },
        "funding": {},
        "source_url": item.get("source", ""),
        "origin_file": "news.json",
    }


def adapt_wamda(item):

    entities = item.get("entities", {})

    startups = []
    investors = []

    if isinstance(entities, dict):

        if entities.get("startup"):
            startups.append(entities["startup"])

        if entities.get("investor"):
            investors.append(entities["investor"])

    return {
        "title": item.get("title", ""),
        "summary": item.get("summary", ""),
        "content": item.get("content", ""),
        "date": item.get("date", ""),
        "country": item.get("country", ""),
        "region": item.get("region", ""),
        "category": item.get("category", ""),
        "tags": [],
        "amounts": [],
        "relevance": "high" if item.get("relevant") else "",
        "entities": {
            "startups": startups,
            "investors": investors,
            "funds": []
        },
        "funding": item.get("funding", {}),
        "source_url": item.get("source", ""),
        "origin_file": "wamda_news.json",
    }


ADAPTERS = {
    "articles": adapt_articles,
    "news": adapt_news,
    "wamda": adapt_wamda,
}


# ==========================================================
# Fusion
# ==========================================================

def merge_all():

    merged = []

    print("\n========== CHARGEMENT ==========\n")

    for key, path in INPUT_FILES.items():

        raw_items = load_json(path)

        print(f"{path.name:<20} -> {len(raw_items)} articles")

        adapter = ADAPTERS[key]

        for raw in raw_items:

            article = adapter(raw)

            article["id"] = make_id(
                article["source_url"],
                article["title"]
            )

            merged.append(article)

    print("\n===============================\n")

    return merged


# ==========================================================
# Déduplication
# ==========================================================

def deduplicate(articles):

    seen_urls = {}
    seen_titles = {}

    result = []

    duplicates = 0

    for article in articles:

        url = article["source_url"].strip().rstrip("/") if article["source_url"] else ""

        title_key = normalize_title_key(article["title"])

        idx = None

        if url:
            idx = seen_urls.get(url)

        if idx is None and title_key:
            idx = seen_titles.get(title_key)

        if idx is not None:

            duplicates += 1

            if len(article.get("content", "")) > len(result[idx].get("content", "")):
                result[idx] = article

            continue

        result.append(article)

        new_index = len(result) - 1

        if url:
            seen_urls[url] = new_index

        if title_key:
            seen_titles[title_key] = new_index

    print(f"Doublons supprimés : {duplicates}")

    return result


# ==========================================================
# Sauvegarde
# ==========================================================

def save_json(data, path):

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ==========================================================
# Main
# ==========================================================

def main():

    print("\nFusion des trois sources...\n")

    merged = merge_all()

    print(f"Total avant déduplication : {len(merged)}")

    merged = deduplicate(merged)

    print(f"Total final : {len(merged)}")

    save_json(merged, OUTPUT_FILE)

    print("\n====================================")
    print("Fusion terminée avec succès.")
    print(f"Fichier créé : {OUTPUT_FILE}")
    print("====================================")


if __name__ == "__main__":
    main()
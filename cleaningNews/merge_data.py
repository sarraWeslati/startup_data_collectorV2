import json
import hashlib
import re
from pathlib import Path


# ==========================================================
# Configuration
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILES = {
    "articles": PROJECT_ROOT / "site_managers" / "storage" / "articles.json",
    "news": PROJECT_ROOT / "news" / "newsAll.json",
    "wamda": PROJECT_ROOT / "wamdaNews" / "storage" / "wamda_news.json",
}

OUTPUT_FILE = PROJECT_ROOT / "cleaningNews" / "merged_news.json"


# ==========================================================
# Load JSON
# ==========================================================

def load_json(path):

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



# ==========================================================
# Utils
# ==========================================================

def normalize_title(title):

    if not title:
        return ""

    title = title.lower()
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title)

    return title.strip()



def make_id(url, title):

    value = url or title or ""

    return hashlib.md5(
        value.lower().encode()
    ).hexdigest()[:12]



# ==========================================================
# Normalisation Entities
# ==========================================================

def normalize_entities(entities):

    if not isinstance(entities, dict):
        return {
            "startups": [],
            "investors": [],
            "funds": [],
            "accelerators": [],
            "incubators": []
        }


    result = entities.copy()


    # startup -> startups

    if "startup" in result:

        if result["startup"]:
            result["startups"] = [result["startup"]]

        del result["startup"]


    # investor -> investors

    if "investor" in result:

        if result["investor"]:

            if isinstance(result["investor"], list):
                result["investors"] = result["investor"]

            else:
                result["investors"] = [
                    result["investor"]
                ]

        del result["investor"]


    result.setdefault("startups", [])
    result.setdefault("investors", [])
    result.setdefault("funds", [])
    result.setdefault("accelerators", [])
    result.setdefault("incubators", [])


    return result



# ==========================================================
# Adaptation générale
# ==========================================================

def normalize_article(item, origin):


    article = item.copy()


    # -----------------------
    # Content
    # -----------------------

    if not article.get("content"):

        source_article = article.get(
            "source_article",
            {}
        )

        if isinstance(source_article, dict):

            article["content"] = (
                source_article.get("content","")
            )


    # -----------------------
    # Source URL
    # -----------------------

    if "source_url" not in article:

        article["source_url"] = (
            article.get("source")
            or
            article.get("url")
            or ""
        )


    # -----------------------
    # Entities
    # -----------------------

    article["entities"] = normalize_entities(
        article.get("entities", {})
    )


    # -----------------------
    # Default fields
    # -----------------------

    article.setdefault(
        "summary",
        ""
    )

    article.setdefault(
        "country",
        ""
    )

    article.setdefault(
        "region",
        ""
    )

    article.setdefault(
        "category",
        ""
    )

    article.setdefault(
        "funding",
        {}
    )

    article.setdefault(
        "metrics",
        {}
    )

    article.setdefault(
        "tags",
        []
    )

    article.setdefault(
        "amounts",
        []
    )


    article["origin_file"] = origin


    article["id"] = make_id(
        article["source_url"],
        article.get("title","")
    )


    return article



# ==========================================================
# Fusion
# ==========================================================

def merge_all():


    merged = []


    print("\n========== CHARGEMENT ==========\n")


    for name, path in INPUT_FILES.items():


        data = load_json(path)


        print(
            f"{path.name:<25} -> {len(data)} articles"
        )


        for item in data:


            article = normalize_article(
                item,
                path.name
            )


            merged.append(article)



    print(
        "\nTotal chargé :",
        len(merged)
    )


    return merged




# ==========================================================
# Deduplication
# ==========================================================

def deduplicate(data):


    seen_urls = set()
    seen_titles = set()

    result = []

    duplicates = 0


    for article in data:


        url = (
            article.get("source_url","")
            .strip()
            .rstrip("/")
        )


        title = normalize_title(
            article.get("title","")
        )


        duplicate = False


        if url and url in seen_urls:

            duplicate = True


        if title and title in seen_titles:

            duplicate = True



        if duplicate:

            duplicates += 1

            continue



        result.append(article)


        if url:
            seen_urls.add(url)


        if title:
            seen_titles.add(title)



    print(
        "Doublons supprimés :",
        duplicates
    )


    return result



# ==========================================================
# Save
# ==========================================================

def save_json(data,path):


    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )



# ==========================================================
# Main
# ==========================================================

def main():


    print(
        "\nFusion des fichiers JSON..."
    )


    merged = merge_all()


    print(
        "\nAvant nettoyage :",
        len(merged)
    )


    merged = deduplicate(
        merged
    )


    print(
        "Après déduplication :",
        len(merged)
    )


    save_json(
        merged,
        OUTPUT_FILE
    )


    print(
        "\n================================"
    )

    print(
        "Fusion terminée avec succès"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "================================"
    )



if __name__ == "__main__":
    main()
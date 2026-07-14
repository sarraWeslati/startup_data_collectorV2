import json
import os
from datetime import datetime


# ===============================
# PATHS
# ===============================

NEWS_FILE = r"C:\Users\Dell\Downloads\startup_data_collectorV2-main\startup_data_collectorV2\news\news.json"

ARTICLES_FILE = r"C:\Users\Dell\Downloads\startup_data_collectorV2-main\startup_data_collectorV2\site_managers\storage\articles.json"


OUTPUT_FILE = r"C:\Users\Dell\Downloads\startup_data_collectorV2-main\startup_data_collectorV2\news\newsAll.json"



# ===============================
# LOAD JSON
# ===============================

def load_json(path):

    if not os.path.exists(path):
        print(f"❌ File not found : {path}")
        return []


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



# ===============================
# NORMALIZE articles.json
# ===============================

def normalize_article(article):

    source_article = article.get(
        "source_article",
        {}
    )


    return {

        "title":
            article.get(
                "title",
                source_article.get("title","")
            ),


        "summary":
            article.get(
                "summary",
                ""
            ),


        "content":
            source_article.get(
                "content",
                ""
            ),


        "country":
            "Tunisia",


        "category":
            "startup",


        "entities": {

            "startups": [],

            "investors": [],

            "funds": []

        },


        "tags":
            article.get(
                "tags",
                []
            ),


        "source":
            source_article.get(
                "url",
                ""
            ),


        "date":
             article.get(
                "date",
                ""
            ),



        "relevance":
            article.get(
                "relevance",
                ""
            )

    }



# ===============================
# REMOVE DUPLICATES
# ===============================

def deduplicate(news):

    seen = set()

    result = []


    for item in news:

        url = item.get(
            "source",
            ""
        )


        title = item.get(
            "title",
            ""
        )


        key = url if url else title.lower()


        if key not in seen:

            seen.add(key)

            result.append(item)



    return result




# ===============================
# MAIN
# ===============================

def main():

    print("\n🚀 NEWS MERGE START\n")


    news_data = load_json(
        NEWS_FILE
    )


    articles_data = load_json(
        ARTICLES_FILE
    )


    print(
        f"News articles     : {len(news_data)}"
    )

    print(
        f"Other articles    : {len(articles_data)}"
    )



    print("\n🔄 Normalizing articles...")


    normalized_articles = []


    for article in articles_data:

        normalized_articles.append(
            normalize_article(article)
        )



    print(
        f"Normalized others : {len(normalized_articles)}"
    )



    print("\n🔗 Merging...")


    merged = (
        news_data
        +
        normalized_articles
    )



    print(
        f"Before dedup      : {len(merged)}"
    )



    merged = deduplicate(
        merged
    )


    print(
        f"After dedup       : {len(merged)}"
    )



    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            merged,
            f,
            ensure_ascii=False,
            indent=4
        )



    print(
        "\n✅ DONE"
    )

    print(
        "Output :",
        OUTPUT_FILE
    )



if __name__ == "__main__":
    main()
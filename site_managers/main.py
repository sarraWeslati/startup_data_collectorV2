import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


from crawler import get_article_links
from llm import llm_extract
from scraper import scrape_article



# ==================================
# CONFIG
# ==================================

BASE_URL = "https://managers.tn/category/startup/"

MAX_WORKERS = 3


ROOT_DIR = Path(__file__).resolve().parent

STORAGE_DIR = ROOT_DIR / "storage"





# ==================================
# PROCESS ARTICLE
# ==================================

def process_article(url):

    try:

        print("\n[SCRAPE]", url)


        result = scrape_article(url)


        if not result:

            return None


        text, date = result


        if not text:

            return None



        title = text.split(".")[0][:250]


        print(
            "[LLM]",
            title
        )


        data = llm_extract(

            url=url,

            title=title,

            text=text,

            date=date

        )


        if not data.get(
            "relevant",
            False
        ):

            print(
                "❌ NOT RELEVANT"
            )

            return None



        data["source"] = url


        data["source_article"] = {

            "url": url,

            "title": title,

            "content": text

        }



        print(
            "✅ SAVED:",
            data.get("category")
        )


        return data



    except Exception as e:


        print(
            "[PROCESS ERROR]",
            url,
            e
        )


        return None






# ==================================
# SAVE JSON
# ==================================

def save_json(filename, data):


    STORAGE_DIR.mkdir(
        exist_ok=True
    )


    path = STORAGE_DIR / filename



    with open(

        path,

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            data,

            f,

            indent=4,

            ensure_ascii=False

        )


    print(
        "SAVED:",
        path
    )






# ==================================
# REMOVE DUPLICATES
# ==================================

def remove_duplicates(data, key):


    seen = set()

    result = []



    for item in data:


        value = item.get(key)



        if isinstance(value, dict):

            value = value.get(
                "name",
                ""
            )



        if isinstance(value, list):

            value = str(value)



        if value and value not in seen:


            seen.add(value)

            result.append(item)



    return result






# ==================================
# EXTRACT ENTITIES
# ==================================

def extract_entities(articles):


    startups = []

    investors = []



    for article in articles:


        entities = article.get(
            "entities",
            {}
        )



        # ==========================
        # STARTUPS
        # ==========================


        for startup in entities.get(
            "startups",
            []
        ):


            if isinstance(startup, dict):

                startup_name = startup.get(
                    "name",
                    ""
                )

            else:

                startup_name = startup



            if startup_name:


                startups.append({

                    "name": startup_name,


                    "country": article.get(
                        "country",
                        ""
                    ),


                    "summary": article.get(
                        "summary",
                        ""
                    ),


                    "category": article.get(
                        "category",
                        ""
                    ),


                    "funding": article.get(
                        "funding",
                        {}
                    ),


                    "metrics": article.get(
                        "metrics",
                        {}
                    ),


                    "source": article.get(
                        "source",
                        ""
                    ),


                    "article_title": article.get(
                        "title",
                        ""
                    )

                })






        # ==========================
        # INVESTORS
        # ==========================


        for investor in entities.get(
            "investors",
            []
        ):


            if isinstance(investor, dict):

                investor_name = investor.get(
                    "name",
                    ""
                )

            else:

                investor_name = investor



            if investor_name:


                investors.append({

                    "name": investor_name,


                    "country": article.get(
                        "country",
                        ""
                    ),


                    "summary": article.get(
                        "summary",
                        ""
                    ),


                    "category": article.get(
                        "category",
                        ""
                    ),


                    "investments": {


                        "startups": entities.get(
                            "startups",
                            []
                        ),


                        "funding": article.get(
                            "funding",
                            {}
                        )

                    },


                    "source": article.get(
                        "source",
                        ""
                    ),


                    "article_title": article.get(
                        "title",
                        ""
                    )

                })





    startups = remove_duplicates(
        startups,
        "name"
    )


    investors = remove_duplicates(
        investors,
        "name"
    )



    return startups, investors







# ==================================
# MAIN
# ==================================

# ==================================
# MAIN
# ==================================

def main():

    print(
        "🚀 AFRICA STARTUP NEWS PIPELINE"
    )


    # ==============================
    # MODE
    # ==============================

    if len(sys.argv) > 1:

        mode = sys.argv[1]

    else:

        mode = input(
            "Mode (20/full): "
        )



    # ==============================
    # GET URLS
    # ==============================

    links = get_article_links(
        BASE_URL
    )



    if mode == "20":

        links = links[:20]

        print(
            "TEST MODE"
        )

    else:

        print(
            "FULL MODE"
        )



    print(
        "TOTAL URLS:",
        len(links)
    )



    # ==============================
    # PROCESS ARTICLES
    # ==============================

    articles = []



    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:


        futures = {


            executor.submit(
                process_article,
                url
            ): url


            for url in links

        }



        for i, future in enumerate(
            as_completed(futures),
            start=1
        ):


            url = futures[future]


            print(
                f"[{i}/{len(links)}]"
            )


            try:

                data = future.result()


                if data:

                    # Tous les articles startup/funding/investor
                    articles.append(data)



            except Exception as e:

                print(
                    "[ERROR]",
                    e
                )



    # ==============================
    # SAVE ALL ARTICLES FIRST
    # ==============================

    print(
        "\nTOTAL ARTICLES:",
        len(articles)
    )


    save_json(
        "articles.json",
        articles
    )



    # ==============================
    # EXTRACT STARTUPS + INVESTORS
    # ==============================

    startups, investors = extract_entities(
        articles
    )



    # ==============================
    # SAVE STARTUPS
    # ==============================

    save_json(
        "startups.json",
        startups
    )



    # ==============================
    # SAVE INVESTORS
    # ==============================

    save_json(
        "investors.json",
        investors
    )



    # ==============================
    # STATISTICS
    # ==============================

    print("\n====================")


    print(
        "ARTICLES:",
        len(articles)
    )


    print(
        "STARTUPS:",
        len(startups)
    )


    print(
        "INVESTISSEURS:",
        len(investors)
    )


    print("====================")





if __name__ == "__main__":

    main()
import json
import os
import time
import random


from playwright.sync_api import sync_playwright


from scraper import scrape_page
from extractor import extract_news


from config import (
    VALID_CATEGORIES,
    AFRICA_KEYWORDS,
    MENA_KEYWORDS,
    STARTUP_KEYWORDS,
    OUTPUT_FILE
)




# ============================
# LOAD EXISTING
# ============================


def load_existing():


    if not os.path.exists(
        OUTPUT_FILE
    ):

        return []


    try:

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)


    except:

        return []




# ============================
# SAVE IMMEDIATE
# ============================


def save_news(news):


    existing = load_existing()


    urls = {

        x.get("source")

        for x in existing

    }


    if news.get("source") in urls:

        print(
            "DUPLICATE SKIP"
        )

        return



    existing.append(news)



    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            existing,

            f,

            indent=4,

            ensure_ascii=False

        )



    print(
        "💾 JSON UPDATED"
    )





# ============================
# AFRICA CHECK
# ============================


def is_africa_related(title, content):

    text = (
        title +
        " " +
        content
    ).lower()


    keywords = (
        AFRICA_KEYWORDS
        +
        MENA_KEYWORDS
    )


    for word in keywords:

        if word.lower() in text:

            return True


    return False


    text=(

        title
        +
        " "
        +
        content

    ).lower()



    for word in AFRICA_KEYWORDS:


        if word.lower() in text:

            return True



    return False





# ============================
# STARTUP CHECK
# ============================


def is_startup_news(
        title,
        content
):


    text=(

        title
        +
        " "
        +
        content

    ).lower()



    for word in STARTUP_KEYWORDS:


        if word.lower() in text:

            return True



    return False





# ============================
# PROCESS ARTICLE
# ============================


def process(
        page,
        url
):


    data = scrape_page(

        page,

        url

    )



    if not data:


        return None



    title=data.get(
        "title",
        ""
    )


    content=data.get(
        "content",
        ""
    )



    print(
        "[TITLE]",
        title
    )


    print(
        "[CONTENT]",
        len(content)
    )



    if len(content)<1000:


        print(
            "CONTENT TOO SHORT"
        )

        return None




    if not is_africa_related(

        title,

        content

    ):


        print(
            "❌ NOT AFRICA"
        )

        return None




    if not is_startup_news(

        title,

        content

    ):


        print(
            "❌ NOT STARTUP NEWS"
        )

        return None





    result = extract_news(

        content,

        url,

        title

    )



    return result





# ============================
# MAIN PIPELINE
# ============================


def run_pipeline(
        urls
):


    print(
        "TOTAL ARTICLES:",
        len(urls)
    )



    saved=0



    with sync_playwright() as p:



        browser=p.chromium.launch(

            headless=False,

            args=[

                "--disable-blink-features=AutomationControlled"

            ]

        )



        context=browser.new_context(

            user_agent=(

                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/120 Safari/537.36"

            ),

            viewport={

                "width":1366,

                "height":768

            }

        )



        page=context.new_page()



        page.add_init_script(

            """

            Object.defineProperty(
                navigator,
                'webdriver',
                {
                    get:()=>undefined
                }
            )

            """

        )





        for i,url in enumerate(urls):


            print("\n================")

            print(

                f"[{i+1}/{len(urls)}]"

            )


            print(

                "[SCRAPE]",

                url

            )



            try:


                time.sleep(

                    random.uniform(
                        2,
                        5
                    )

                )



                news=process(

                    page,

                    url

                )



                if news:



                    category=(

                        news.get(
                            "category",
                            ""
                        )
                        .lower()

                    )



                    if category in VALID_CATEGORIES:



                        save_news(

                            news

                        )


                        saved+=1



                        print(

                            "✅ SAVED",

                            news["title"]

                        )


                    else:


                        print(

                            "❌ INVALID CATEGORY",

                            category

                        )



                else:


                    print(

                        "❌ NO DATA"

                    )




            except Exception as e:


                print(

                    "ERROR",

                    e

                )




        browser.close()



        print(
    "TOTAL SAVED:",
    saved
)

    return load_existing()
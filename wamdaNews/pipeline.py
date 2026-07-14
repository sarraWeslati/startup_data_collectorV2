import json
import os
import time
import random


from playwright.sync_api import sync_playwright


from scraper import scrape_page
from extractor import extract_news


from config import (
    OUTPUT_FILE,
    VALID_CATEGORIES
)





# =========================
# LOAD EXISTING DATA
# =========================


def load_existing():


    if not os.path.exists(OUTPUT_FILE):

        return []



    try:

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data=json.load(f)


            if isinstance(data,list):

                return data


            return []



    except Exception as e:


        print(
            "LOAD ERROR:",
            e
        )

        return []







# =========================
# SAVE NEWS
# =========================


def save_news(news):


    data=load_existing()



    existing_urls={

        item.get("source")

        for item in data

    }



    if news.get("source") in existing_urls:


        print(
            "DUPLICATE:",
            news.get("title")
        )


        return False




    data.append(news)



    try:


        with open(

            OUTPUT_FILE,

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
            news.get("title")
        )


        return True



    except Exception as e:


        print(
            "SAVE ERROR:",
            e
        )


        return False







# =========================
# PROCESS ARTICLE
# =========================


def process(page,url):


    article=scrape_page(

        page,

        url

    )



    if not article:


        return None




    title=article.get(

        "title",

        ""

    )



    content=article.get(

        "content",

        ""

    )




    print(
        "\nTITLE:",
        title
    )


    print(
        "CONTENT SIZE:",
        len(content)
    )




    if len(content)<500:


        print(
            "CONTENT TOO SHORT"
        )


        return None






    news=extract_news(

        content,

        url,

        title

    )



    return news







# =========================
# CATEGORY NORMALIZATION
# =========================


def normalize_category(news):


    category=news.get(

        "category",

        ""

    )



    # LLM returned dict

    if isinstance(category,dict):


        print(
            "FIX CATEGORY DICT"
        )


        category=list(

            category.keys()

        )[0]



        news["category"]=category




    if not isinstance(
        category,
        str
    ):


        return ""




    return category.lower()








# =========================
# MAIN PIPELINE
# =========================


def run_pipeline(urls):


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
                "(Windows NT 10.0; Win64; x64)"

            )

        )



        page=context.new_page()





        for i,url in enumerate(urls):


            print(
                "\n===================="
            )


            print(
                f"[{i+1}/{len(urls)}]"
            )


            print(
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



                if not news:


                    print(
                        "NO DATA"
                    )

                    continue





                category=normalize_category(

                    news

                )



                print(
                    "CATEGORY:",
                    category
                )




                if category in VALID_CATEGORIES:



                    if save_news(news):


                        saved+=1




                else:


                    print(

                        "FILTERED CATEGORY:",

                        category

                    )





            except Exception as e:


                print(

                    "PIPELINE ERROR:",

                    e

                )





        browser.close()




    print(
        "\nTOTAL SAVED:",
        saved
    )



    return load_existing()
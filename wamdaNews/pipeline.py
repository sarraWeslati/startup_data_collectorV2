# pipeline.py


import asyncio
import json
import os
import time

from scraper import crawl_all_articles

from llm_extractor import extract_article



OUTPUT = "newsWamda.json"



def remove_duplicates(news):


    seen=set()

    result=[]


    for item in news:


        key = (

            item.get("title","")
            .lower()
            .strip()

        )


        if key and key not in seen:


            seen.add(key)

            result.append(item)


    return result





def save_news(news):


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            news,

            f,

            ensure_ascii=False,

            indent=2

        )





async def run_pipeline():


    print(
        "🚀 Starting crawl..."
    )


    articles = await crawl_all_articles(
        max_pages=10
    )



    print(
        f"📄 Articles crawled: {len(articles)}"
    )



    extracted=[]



    semaphore = asyncio.Semaphore(3)



    async def process(article):


        async with semaphore:


            print(
                "🧠 Extracting:",
                article["url"]
            )


            data = await asyncio.to_thread(

                extract_article,

                article

            )


            if data:

                extracted.append(
                    data
                )





    tasks=[

        process(a)

        for a in articles

    ]



    await asyncio.gather(
        *tasks
    )



    print(
        f"🌍 Africa news kept: {len(extracted)}"
    )



    extracted = remove_duplicates(
        extracted
    )


    print(
        f"✨ After deduplication: {len(extracted)}"
    )



    save_news(
        extracted
    )


    print(
        "✅ Saved:",
        OUTPUT
    )

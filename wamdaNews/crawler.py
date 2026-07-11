import requests
import time
import random

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from config import BASE_URL, MAX_PAGES


HEADERS = {

    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",

    "Accept":
    "text/html",

}


session = requests.Session()
session.headers.update(HEADERS)



IGNORE = [

    "/tag/",
    "/author/",
    "/events/",
    "/subscribe",
    "/podcast",
    "/category/",
    "/page/"

]



def valid_article(url):


    if not url.startswith(
        "https://www.wamda.com/"
    ):
        return False


    for x in IGNORE:

        if x in url:

            return False


    parts=url.split("/")


    # https://www.wamda.com/2026/07/article

    if len(parts) < 5:

        return False


    if not parts[3].isdigit():

        return False


    return True





def get_links(page):


    links=[]


    url=f"{BASE_URL}/news?page={page}"


    print(
        "FETCH:",
        url
    )


    try:


        r=session.get(

            url,

            timeout=30

        )


        print(
            "STATUS:",
            r.status_code
        )


        soup=BeautifulSoup(

            r.text,

            "lxml"

        )



        for a in soup.find_all(
            "a",
            href=True
        ):


            href=a["href"]


            full=urljoin(

                BASE_URL,

                href

            )



            if valid_article(full):


                links.append(full)




    except Exception as e:


        print(
            "CRAWLER ERROR",
            e
        )



    return list(set(links))






def get_article_links():


    results=[]


    for page in range(
        1,
        MAX_PAGES+1
    ):


        print(
            "\n[PAGE]",
            page
        )


        links=get_links(
            page
        )


        print(
            "FOUND:",
            len(links)
        )


        results.extend(
            links
        )



        time.sleep(
            random.uniform(1,2)
        )



    results=list(set(results))


    print(
        "\nTOTAL DISCOVERED:",
        len(results)
    )


    return results
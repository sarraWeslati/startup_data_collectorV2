import requests
import time
import random

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from config import (
    BASE_URL,
    MAX_PAGES
)



HEADERS = {

    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/138 Safari/537.36",

    "Accept":
    "text/html,application/xhtml+xml",

    "Accept-Language":
    "en-US,en;q=0.9"

}



IGNORE = [

    "/tag/",
    "/author/",
    "/contact/",
    "/events/",
    "/subscribe",
    "/country/",
    "/podcast"

]



KEYWORDS = [

    "startup",
    "funding",
    "investment",
    "investor",
    "venture",
    "capital",
    "fund",
    "raised",
    "million",
    "billion",
    "series",
    "seed",
    "vc"

]




session = requests.Session()

session.headers.update(
    HEADERS
)




def relevant(url, title):


    text = (
        url +
        " " +
        title
    ).lower()


    return any(
        k in text
        for k in KEYWORDS
    )




def get_links(page):


    links=[]


    url=f"{BASE_URL}?page={page}"


    try:


        time.sleep(
            random.uniform(1,2)
        )


        r=session.get(
            url,
            timeout=30
        )


        if r.status_code != 200:

            print(
                "PAGE ERROR",
                r.status_code
            )

            return []



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



            if not full.startswith(
                "https://www.wamda.com/"
            ):
                continue



            if any(
                x in full
                for x in IGNORE
            ):
                continue



            parts=full.split("/")


            # format:
            # /2025/07/title

            if len(parts)>=5:


                if parts[3].isdigit():


                    title=a.get_text(
                        " ",
                        strip=True
                    )


                    if relevant(
                        full,
                        title
                    ):


                        links.append(
                            full
                        )



    except Exception as e:

        print(
            "CRAWLER ERROR",
            e
        )


    return list(
        set(links)
    )






def get_article_links():


    results=[]



    for page in range(
        1,
        MAX_PAGES+1
    ):


        print(
            "[PAGE]",
            page
        )


        links=get_links(
            page
        )


        print(
            "FOUND",
            len(links)
        )


        results.extend(
            links
        )



    results=list(
        set(results)
    )


    return results
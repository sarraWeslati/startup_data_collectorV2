from bs4 import BeautifulSoup
from playwright.sync_api import Page
import re
import time
import random



def clean_text(text):


    text = " ".join(
        text.split()
    )


    noise = [

        "Sign up to receive our weekly digest",
        "Please check your email to confirm your subscription",
        "Subscribe",
        "Newsletter",
        "Follow us",
        "Wamda newsletter"

    ]


    for n in noise:

        text=text.replace(
            n,
            ""
        )



    # corriger mots collés

    text=re.sub(

        r'(?<=[a-z])(?=[A-Z])',

        ' ',

        text

    )



    text=re.sub(

        r'(?<=,)(?=[A-Za-z])',

        ', ',

        text

    )



    return text.strip()







def extract_title(soup):


    # OpenGraph

    og=soup.find(

        "meta",

        property="og:title"

    )


    if og:

        return og.get(
            "content",
            ""
        ).replace(
            "- Wamda",
            ""
        ).strip()



    if soup.title:


        return soup.title.text.replace(

            "- Wamda",

            ""

        ).strip()



    h1=soup.find(
        "h1"
    )


    if h1:

        return h1.get_text(

            " ",

            strip=True

        )


    return ""








def extract_content(soup):


    for tag in soup([

        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "form"

    ]):

        tag.decompose()



    paragraphs=[]



    for p in soup.find_all(
        "p"
    ):


        txt=p.get_text(

            " ",

            strip=True

        )


        if len(txt)>40:

            paragraphs.append(
                txt
            )



    if paragraphs:


        content=" ".join(
            paragraphs
        )


    else:


        content=soup.get_text(

            " ",

            strip=True

        )



    return clean_text(
        content
    )










def scrape_page(page:Page,url):


    print(
        "\n[SCRAPE]",
        url
    )



    for attempt in range(3):


        try:


            page.goto(

                url,

                wait_until="domcontentloaded",

                timeout=60000

            )



            page.wait_for_timeout(

                random.randint(
                    3000,
                    6000
                )

            )



            html=page.content()



            soup=BeautifulSoup(

                html,

                "lxml"

            )



            title=extract_title(
                soup
            )


            content=extract_content(
                soup
            )



            print(

                "[TITLE]",

                title

            )



            print(

                "[CONTENT]",

                len(content)

            )



            # détecter blocage

            if (

                "403 Forbidden" in title

                or

                len(content)<300

            ):


                print(

                    "BLOCKED RETRY",

                    attempt+1

                )


                time.sleep(5)

                continue





            return {


                "title":

                title,


                "content":

                content[:8000],


                "url":

                url


            }




        except Exception as e:


            print(

                "SCRAPER ERROR",

                e

            )


            time.sleep(5)




    print(

        "FAILED",

        url

    )


    return None
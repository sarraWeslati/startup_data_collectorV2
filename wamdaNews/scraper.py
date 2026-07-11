from bs4 import BeautifulSoup
from playwright.sync_api import Page

import re
import time
import random





# =========================
# TEXT CLEANING
# =========================


def clean_text(text):


    if not text:

        return ""



    text=" ".join(
        text.split()
    )



    noise=[

        "Sign up to receive our weekly digest",
        "Please check your email to confirm your subscription",
        "Subscribe",
        "Newsletter",
        "Follow us",
        "Wamda newsletter",
        "Related Articles",
        "You may also like",
        "Read more",
        "Advertisement"

    ]



    for n in noise:


        text=text.replace(
            n,
            ""
        )



    # words joined together

    text=re.sub(

        r'(?<=[a-z])(?=[A-Z])',

        ' ',

        text

    )



    # missing spaces after punctuation

    text=re.sub(

        r'(?<=[,.])(?=[A-Za-z])',

        ', ',

        text

    )



    return text.strip()







# =========================
# TITLE EXTRACTION
# =========================


def extract_title(soup):


    # OpenGraph

    meta=soup.find(

        "meta",

        property="og:title"

    )


    if meta and meta.get("content"):


        return clean_text(

            meta["content"]

        ).replace(

            "- Wamda",

            ""

        )





    h1=soup.find(
        "h1"
    )


    if h1:


        return clean_text(

            h1.get_text()

        )





    if soup.title:


        return clean_text(

            soup.title.text

        ).replace(

            "- Wamda",

            ""

        )



    return ""








# =========================
# DATE EXTRACTION
# =========================


def extract_date(soup):


    date=None



    meta_dates=[

        "article:published_time",

        "date",

        "publish_date"

    ]



    for d in meta_dates:


        tag=soup.find(

            "meta",

            property=d

        )


        if not tag:


            tag=soup.find(

                "meta",

                attrs={"name":d}

            )



        if tag and tag.get("content"):


            date=tag["content"]

            break




    if not date:


        text=soup.get_text(
            " ",
            strip=True
        )


        match=re.search(

            r'\b(20\d{2})[-/]\d{2}[-/]\d{2}\b',

            text

        )


        if match:

            date=match.group()



    return date







# =========================
# CONTENT EXTRACTION
# =========================


def extract_content(soup):


    remove=[

        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        "button",
        "svg"

    ]



    for tag in soup.find_all(remove):


        tag.decompose()





    # Wamda article body

    article=soup.find(

        "article"

    )



    if article:


        paragraphs=article.find_all(
            "p"
        )


    else:


        paragraphs=soup.find_all(
            "p"
        )






    content=[]



    for p in paragraphs:


        txt=p.get_text(

            " ",

            strip=True

        )



        txt=clean_text(txt)



        if len(txt)>50:


            content.append(txt)





    result=" ".join(content)





    if len(result)<300:


        result=clean_text(

            soup.get_text(

                " ",

                strip=True

            )

        )





    return result







# =========================
# KEYWORD CHECK
# =========================


def is_article(title,content):


    text=(

        title+" "+content

    ).lower()



    keywords=[


        "startup",

        "funding",

        "raised",

        "investment",

        "investor",

        "venture",

        "seed",

        "series a",

        "series b",

        "accelerator",

        "acquisition",

        "vc"

    ]



    return any(

        k in text

        for k in keywords

    )







# =========================
# MAIN SCRAPER
# =========================


def scrape_page(page:Page,url):


    print(

        "\n[SCRAPE]",

        url

    )



    for attempt in range(1,4):


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



            date=extract_date(
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





            # anti bot

            blocked=[

                "403",

                "access denied",

                "captcha",

                "cloudflare"

            ]



            if any(

                x in content.lower()

                for x in blocked

            ):


                print(

                    "BLOCKED"

                )


                time.sleep(5)

                continue






            if len(content)<500:


                print(

                    "CONTENT TOO SHORT"

                )


                time.sleep(3)

                continue





            if not is_article(

                title,

                content

            ):


                print(

                    "NOT STARTUP ARTICLE"

                )


                return None





            return {


                "title":

                title,



                "content":

                content[:8000],



                "date":

                date,



                "url":

                url


            }





        except Exception as e:


            print(

                "SCRAPER ERROR:",

                e

            )


            time.sleep(5)




    print(

        "FAILED:",

        url

    )


    return None
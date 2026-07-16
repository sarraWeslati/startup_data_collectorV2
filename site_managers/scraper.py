import requests
import trafilatura
from trafilatura.metadata import extract_metadata



# ==============================
# CONFIG
# ==============================


HEADERS = {

    "User-Agent":
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120 Safari/537.36"
    )

}



TIMEOUT = 15





# ==============================
# CLEAN TEXT
# ==============================


def clean_text(text):

    if not text:

        return ""


    return (
        " "
        .join(
            text.split()
        )
        .strip()
    )





# ==============================
# SCRAPE ARTICLE
# ==============================


def scrape_article(url):


    try:


        response = requests.get(

            url,

            headers=HEADERS,

            timeout=TIMEOUT

        )



        if response.status_code != 200:


            print(

                "[HTTP ERROR]",

                response.status_code,

                url

            )


            return None, None





        html = response.text





        # ==============================
        # EXTRACTION ARTICLE
        # ==============================


        text = trafilatura.extract(

            html,

            include_comments=False,

            include_tables=False,

            favor_precision=True

        )



        if not text:


            print(

                "[NO CONTENT]",

                url

            )


            return None, None





        text = clean_text(text)





        # ==============================
        # DATE EXTRACTION
        # ==============================


        date = ""



        try:


            metadata = extract_metadata(
                html
            )


            if metadata and metadata.date:

                date = metadata.date



        except Exception:


            pass






        return text, date





    except requests.exceptions.Timeout:


        print(

            "[TIMEOUT]",

            url

        )


        return None, None




    except requests.exceptions.RequestException as e:


        print(

            "[REQUEST ERROR]",

            e

        )


        return None, None




    except Exception as e:


        print(

            "[SCRAPER ERROR]",

            e

        )


        return None, None
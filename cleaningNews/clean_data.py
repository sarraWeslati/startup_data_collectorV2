"""
Script 2 : Nettoyage & normalisation des données
================================================

Input:
    merged_news.json

Output:
    clean_news.json

Pipeline:
    merged_news.json
          |
          v
    nettoyage
          |
          v
    normalisation
          |
          v
    clean_news.json
          |
          v
    RAG / Embeddings
"""

import json
import re
import html
import unicodedata

from pathlib import Path
from datetime import datetime
from dateutil import parser as date_parser



# ==========================================================
# CONFIG
# ==========================================================


BASE_DIR = Path(__file__).parent

INPUT_FILE = BASE_DIR / "merged_news.json"

OUTPUT_FILE = BASE_DIR / "clean_news.json"


MIN_CONTENT_LENGTH = 30



# ==========================================================
# TEXT CLEANING
# ==========================================================


HTML_TAG_RE = re.compile(r"<[^>]+>")

MULTI_SPACE_RE = re.compile(r"[ \t]+")

CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


CHAR_REPLACEMENTS = {

    "\u2018":"' ",
    "\u2019":"' ",
    "\u201c":'"',
    "\u201d":'"',
    "\u2013":"-",
    "\u2014":"-",
    "\u00a0":" ",
    "\u200b":"",
    "\ufeff":""

}



def clean_text(text):

    if text is None:
        return ""

    text = str(text)

    # Decode HTML
    text = html.unescape(text)

    # Remove HTML
    text = HTML_TAG_RE.sub(" ", text)

    # Fix unicode characters
    for old, new in CHAR_REPLACEMENTS.items():
        text = text.replace(old, new)


    # Normalize unicode
    text = unicodedata.normalize(
        "NFKC",
        text
    )


    # Remove control chars
    text = CONTROL_RE.sub("", text)


    # FIX apostrophes
    # l' agriculture -> l'agriculture
    text = re.sub(
        r"\s+'\s*",
        "'",
        text
    )


    # FIX quotes
    text = re.sub(
        r'\s+"\s*',
        '"',
        text
    )


    # Remove multiple spaces
    text = MULTI_SPACE_RE.sub(
        " ",
        text
    )


    return text.strip()


def clean_list(items):

    if not isinstance(items,list):
        return []


    result=[]

    seen=set()


    for item in items:


        value=clean_text(item)


        if value:


            key=value.lower()


            if key not in seen:

                result.append(value)

                seen.add(key)


    return result




# ==========================================================
# ENTITIES CLEANING
# ==========================================================



def clean_entities(items):

    """
    Conserve les objets LLM :

    {
      name,
      founders,
      country,
      sector
    }

    """

    if not isinstance(items,list):

        return []


    result=[]

    seen=set()


    for item in items:


        if isinstance(item,dict):


            obj={}


            for key,value in item.items():

                if value in ["", None, []]:
                 continue


                if isinstance(value,list):

                    obj[key]=clean_list(value)


                elif isinstance(value,dict):

                    obj[key]=value


                else:

                    obj[key]=clean_text(value)



            signature=json.dumps(
                obj,
                sort_keys=True,
                ensure_ascii=False
            )



            if signature not in seen:

                result.append(obj)

                seen.add(signature)



        else:


            value=clean_text(item)


            if value and value.lower() not in seen:

                result.append(value)

                seen.add(
                    value.lower()
                )


    return result




# ==========================================================
# DATE NORMALIZATION
# ==========================================================



UNKNOWN_DATE={
    "",
    "unknown",
    "n/a",
    "na",
    "-",
    "tbd"
}



MONTHS_FR={

"janvier":1,
"février":2,
"fevrier":2,
"mars":3,
"avril":4,
"mai":5,
"juin":6,
"juillet":7,
"août":8,
"aout":8,
"septembre":9,
"octobre":10,
"novembre":11,
"décembre":12,
"decembre":12

}




def normalize_date(raw):


    raw=clean_text(raw)



    if raw.lower() in UNKNOWN_DATE:

        return {
            "date":None,
            "precision":"unknown"
        }




    if re.match(
        r"^\d{4}$",
        raw
    ):

        return {

            "date":raw+"-01-01",

            "precision":"year"

        }




    if re.match(
        r"^\d{4}-\d{2}$",
        raw
    ):

        return {

            "date":raw+"-01",

            "precision":"month"

        }




    try:

        dt=date_parser.parse(
            raw,
            dayfirst=True
        )


        return {

            "date":dt.strftime(
                "%Y-%m-%d"
            ),

            "precision":"day"

        }


    except:


        return {

            "date":None,

            "precision":"unknown"

        }
    # ==========================================================
# COUNTRY / REGION NORMALIZATION
# ==========================================================


REGION_TERMS = {

    "africa",
    "mena",
    "north africa",
    "middle east"

}



COUNTRY_ALIASES = {


    "tunisia":"Tunisia",
    "tunisie":"Tunisia",

    "morocco":"Morocco",
    "maroc":"Morocco",

    "algeria":"Algeria",
    "algérie":"Algeria",

    "egypt":"Egypt",
    "egypte":"Egypt",

    "nigeria":"Nigeria",

    "kenya":"Kenya",

    "south africa":"South Africa",

    "uae":"United Arab Emirates",
    "dubai":"United Arab Emirates",

    "ksa":"Saudi Arabia",
    "saudi arabia":"Saudi Arabia",

    "ivory coast":"Côte d'Ivoire",
    "cote d'ivoire":"Côte d'Ivoire",

    "senegal":"Senegal",

    "ghana":"Ghana",

    "rwanda":"Rwanda",

    "ethiopia":"Ethiopia"

}




def normalize_country(raw):


    if not raw:

        return {
            "countries":[],
            "region":None
        }



    if isinstance(raw,list):

        raw=",".join(raw)



    raw=clean_text(raw)



    if not raw:

        return {
            "countries":[],
            "region":None
        }




    countries=[]

    region=None

    seen=set()



    tokens=re.split(
        r",|and|\||/",
        raw,
        flags=re.I
    )



    for token in tokens:


        token=token.strip()


        if not token:
            continue



        key=token.lower()



        if key in REGION_TERMS:

            region=token.title()

            continue




        country=COUNTRY_ALIASES.get(

            key,

            token.title()

        )



        if country.lower() not in seen:

            countries.append(country)

            seen.add(
                country.lower()
            )




    return {

        "countries":countries,

        "region":region

    }






# ==========================================================
# SECTORS / CATEGORY
# ==========================================================


SECTOR_ALIASES={


"ai":"AI",

"artificial intelligence":"AI",


"fintech":"Fintech",

"financial technology":"Fintech",


"ecommerce":"E-commerce",

"e-commerce":"E-commerce",


"healthtech":"HealthTech",

"health tech":"HealthTech",


"edtech":"EdTech",


"agritech":"AgriTech",

"agtech":"AgriTech",


"climate tech":"CleanTech",

"cleantech":"CleanTech",

"climatetech":"CleanTech",


"logistics":"Logistics",

"mobility":"Mobility",

"energy":"Energy",

"saas":"SaaS",

"software":"Software"

}




CATEGORY_ALIASES={


"funding":"funding",

"investment":"funding",

"fundraise":"funding",


"startup":"startup",

"startup ecosystem":"startup ecosystem",

"ecosystem":"startup ecosystem",


"acquisition":"acquisition",

"report":"report",

"event":"event",

"news":"news"


}




def normalize_sector(value):


    value=clean_text(value)


    if not value:

        return None



    return SECTOR_ALIASES.get(

        value.lower(),

        value.title()

    )




def normalize_category(value):


    value=clean_text(value)



    if not value:

        return "other"



    return CATEGORY_ALIASES.get(

        value.lower(),

        value.lower()

    )





# ==========================================================
# EXTRACTION SECTORS FROM ENTITIES
# ==========================================================


def extract_entity_sectors(entities):


    sectors=[]


    for startup in entities.get(
        "startups",
        []
    ):


        if isinstance(startup,dict):


            sector=startup.get(
                "sector"
            )


            if sector:

                sectors.append(
                    sector
                )


    return sectors





# ==========================================================
# FUNDING CLEAN
# ==========================================================



def clean_funding(data):


    if not isinstance(data,dict):

        return {}



    result={}



    for key,value in data.items():


        if isinstance(value,list):

            result[key]=clean_list(value)



        elif isinstance(value,dict):

            result[key]=clean_funding(value)



        else:

            result[key]=clean_text(value)



    return result





# ==========================================================
# ARTICLE CLEANING
# ==========================================================



def clean_article(article):


    title=clean_text(
        article.get("title")
    )


    summary=clean_text(
        article.get("summary")
    )


    content=clean_text(
        article.get("content")
    )



    if max(
        len(title),
        len(summary),
        len(content)

    ) < MIN_CONTENT_LENGTH:

        return None




    date_info=normalize_date(
        article.get("date")
    )



    country_info = normalize_country(
    article.get("countries")
    or article.get("country")
)


    entities=article.get(
        "entities",
        {}
    )



    tags=article.get(
        "tags",
        []
    )



    # Ajouter secteurs venant des startups LLM

    tags.extend(
        extract_entity_sectors(
            entities
        )
    )



    sectors=[]

    for tag in clean_list(tags):

        sector=normalize_sector(tag)

        if sector and sector not in sectors:

            sectors.append(
                sector
            )




    text_for_rag=f"""
Title:
{title}

Summary:
{summary}

Content:
{content}
""".strip()





    return {


        "id":article.get(
            "id"
        ),


        "title":title,


        "summary":summary,


        "content":content or summary,


        "text_for_rag":text_for_rag,



        "date":date_info["date"],


        "date_precision":
            date_info["precision"],




        "countries":
            country_info["countries"],



        "region":
            country_info["region"],




        "category":
            normalize_category(
                article.get("category")
            ),



        "sectors":sectors,



        "amounts":
            clean_list(
                article.get("amounts")
                or []
            ),




        "relevance":
            clean_text(
                article.get("relevance")
            )
            or None,




        "entities":{


            "startups":
                clean_entities(
                    entities.get(
                        "startups",
                        []
                    )
                ),


            "investors":
                clean_entities(
                    entities.get(
                        "investors",
                        []
                    )
                ),


            "funds":
                clean_entities(
                    entities.get(
                        "funds",
                        []
                    )
                )

        },



        "funding":
            clean_funding(
                article.get(
                    "funding"
                )
            ),




        "source_url":
            clean_text(
                article.get(
                    "source_url"
                )
            ),




        "origin_file":
            clean_text(
                article.get(
                    "origin_file"
                )
            )

    }


def extract_sectors(article):

    sectors=[]

    # tags
    for tag in article.get("tags", []):

        sector = normalize_sector(tag)

        if sector:
            sectors.append(sector)



    # startups sectors
    entities = article.get(
        "entities",
        {}
    )


    for startup in entities.get(
        "startups",
        []
    ):

        if isinstance(startup,dict):

            sector = normalize_sector(
                startup.get("sector","")
            )

            if sector:
                sectors.append(sector)



    # remove duplicates

    result=[]

    seen=set()

    for s in sectors:

        if s.lower() not in seen:

            result.append(s)

            seen.add(
                s.lower()
            )


    return result



# ==========================================================
# MAIN
# ==========================================================



def main():


    with open(
        INPUT_FILE,
        encoding="utf-8"
    ) as f:

        articles=json.load(f)



    print(
        f"Articles chargés : {len(articles)}"
    )



    cleaned=[]

    removed=0



    for article in articles:


        result=clean_article(
            article
        )


        if result:

            cleaned.append(
                result
            )

        else:

            removed+=1




    print(
        f"Supprimés : {removed}"
    )


    print(
        f"Conservés : {len(cleaned)}"
    )



    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            cleaned,
            f,
            ensure_ascii=False,
            indent=2
        )



    print(
        f"Fichier créé : {OUTPUT_FILE}"
    )



    print("\n===== STATISTIQUES =====")


    print(
        "Avec date :",
        sum(
            1 for x in cleaned
            if x["date"]
        )
    )


    print(
        "Avec pays :",
        sum(
            1 for x in cleaned
            if x["countries"]
        )
    )


    print(
        "Avec startups :",
        sum(
            1 for x in cleaned
            if x["entities"]["startups"]
        )
    )


    print(
        "Avec investisseurs :",
        sum(
            1 for x in cleaned
            if x["entities"]["investors"]
        )
    )





if __name__=="__main__":

    main()
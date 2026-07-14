import json
from pathlib import Path
from tqdm import tqdm
import hashlib
import re


# ==============================
# CONFIG
# ==============================

ROOT_DIR = Path(__file__).resolve().parent


NEWS_FILE = ROOT_DIR / "news.json"

OTHER_FILE = (
    ROOT_DIR.parent
    / "site_managers"
    / "storage"
    / "articles.json"
)


OUTPUT_FILE = ROOT_DIR / "newNews.json"


# taille chunk
CHUNK_SIZE = 1200

OVERLAP = 200



# ==============================
# LOAD JSON
# ==============================

def load_json(path):

    if not path.exists():

        print(
            f"❌ File not found : {path}"
        )

        return []


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



# ==============================
# CLEAN TEXT
# ==============================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()



# ==============================
# FILTER ARTICLES
# ==============================


VALID_CATEGORIES = [

    "startup",
    "funding",
    "investment",
    "investor",
    "venture",
    "vc"

]


def is_relevant(article):


    category = (
        article
        .get("category","")
        .lower()
    )


    title = (
        article
        .get("title","")
        .lower()
    )


    keywords = [

        "startup",
        "funding",
        "investment",
        "investor",
        "venture",
        "capital",
        "vc",
        "fintech",
        "accelerator",
        "incubator"

    ]


    if category in VALID_CATEGORIES:

        return True



    for k in keywords:

        if k in title:

            return True



    entities = article.get(
        "entities",
        {}
    )


    if (
        entities.get("startups")
        or
        entities.get("investors")
        or
        entities.get("funds")
    ):

        return True



    return False



# ==============================
# DUPLICATE
# ==============================

def make_hash(article):

    text = (
        article.get("title","")
        +
        article.get("source","")
    )


    return hashlib.md5(
        text.encode()
    ).hexdigest()



# ==============================
# COUNTRY NORMALIZATION
# ==============================

def normalize_country(article):


    country = article.get(
        "country",
        ""
    )


    if not country:

        return []



    if country.lower()=="africa":

        return [
            "Africa"
        ]


    return [
        country
    ]



# ==============================
# DOCUMENT FOR EMBEDDING
# ==============================

def create_document(article):


    startups = ", ".join(

        article
        .get("entities",{})
        .get("startups",[])

    )


    investors = ", ".join(

        article
        .get("entities",{})
        .get("investors",[])

    )


    funds = ", ".join(

        article
        .get("entities",{})
        .get("funds",[])

    )



    document = f"""

Titre:
{article.get("title","")}


Résumé:
{article.get("summary","")}


Contenu:
{article.get("content","")}


Startups:
{startups}


Investisseurs:
{investors}


Fonds:
{funds}


Pays:
{', '.join(article.get("countries",[]))}


Catégorie:
{article.get("category","")}

"""


    return clean_text(document)




# ==============================
# CHUNKING
# ==============================

def split_chunks(text):


    chunks=[]


    start=0


    length=len(text)


    while start < length:


        end = start + CHUNK_SIZE


        chunk=text[start:end]


        chunks.append(
            chunk
        )


        start += (
            CHUNK_SIZE
            -
            OVERLAP
        )


    return chunks



# ==============================
# PROCESS
# ==============================

def process():


    print("\n🚀 Preparing RAG dataset\n")



    news = load_json(
        NEWS_FILE
    )


    other = load_json(
        OTHER_FILE
    )



    print(
        "News:",
        len(news)
    )


    print(
        "Other:",
        len(other)
    )



    articles = news + other



    print(
        "Total:",
        len(articles)
    )



    final=[]

    seen=set()


    counter=1



    for article in tqdm(
        articles
    ):



        if not is_relevant(article):

            continue



        h = make_hash(
            article
        )



        if h in seen:

            continue



        seen.add(h)



        article["id"] = (
            f"news_{counter:06d}"
        )


        counter+=1



        article["title"] = clean_text(
            article.get("title","")
        )


        article["summary"] = clean_text(
            article.get("summary","")
        )


        article["content"] = clean_text(
            article.get("content","")
        )



        article["countries"] = normalize_country(
            article
        )


        article["document"] = create_document(
            article
        )



        chunks = split_chunks(
            article["document"]
        )



        article["chunks"] = []


        for i,chunk in enumerate(
            chunks
        ):

            article["chunks"].append({

                "chunk_id":
                f"{article['id']}_{i}",

                "text":
                chunk

            })



        final.append(
            article
        )



    print(
        "\nFinal documents:",
        len(final)
    )



    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            final,

            f,

            indent=4,

            ensure_ascii=False

        )



    print(
        "\n✅ Saved:"
    )


    print(
        OUTPUT_FILE
    )



# ==============================
# MAIN
# ==============================

if __name__=="__main__":

    process()
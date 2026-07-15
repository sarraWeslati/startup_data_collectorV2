import json
from pathlib import Path


INPUT = Path("../../cleaningNews/clean_news.json")
OUTPUT = Path("../data/documents.json")


def build_document(news):

    entities = news.get("entities", {})

    startups = ", ".join(
        entities.get("startups", [])
    )

    investors = ", ".join(
        entities.get("investors", [])
    )

    funds = ", ".join(
        entities.get("funds", [])
    )


    sectors = ", ".join(
        news.get("sectors", [])
    )


    countries = ", ".join(
        news.get("countries", [])
    )


    text = f"""
Titre:
{news.get('title','')}


Résumé:
{news.get('summary','')}


Date:
{news.get('date','')}


Catégorie:
{news.get('category','')}


Secteurs:
{sectors}


Pays:
{countries}


Startups mentionnées:
{startups}


Investisseurs:
{investors}


Fonds:
{funds}


Article:
{news.get('content','')}
"""


    return {
        "id": news.get("id"),
        "text": text.strip(),
        "metadata": {
            "title": news.get("title"),
            "date": news.get("date"),
            "category": news.get("category"),
            "sectors": news.get("sectors"),
            "source_url": news.get("source_url")
        }
    }



def main():

    with open(INPUT,encoding="utf-8") as f:
        news=json.load(f)


    documents=[]


    for article in news:

        doc=build_document(article)

        documents.append(doc)


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            documents,
            f,
            ensure_ascii=False,
            indent=2
        )


    print(
        len(documents),
        "documents created"
    )



if __name__=="__main__":
    main()
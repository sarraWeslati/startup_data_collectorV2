import json
from pathlib import Path


INPUT = Path("../../cleaningNews/clean_news.json")
OUTPUT = Path("../data/documents.json")


def extract_entity_names(items):
    """
    Transforme une liste d'entités JSON en liste de noms.
    
    Exemple:
    [
        {"name": "EcoFeed", "founder": "Malek"},
        {"name": "Bako Motors"}
    ]

    devient:
    [
        "EcoFeed",
        "Bako Motors"
    ]
    """

    names = []

    for item in items:

        if isinstance(item, dict):
            name = item.get("name")

            if name:
                names.append(name)

        else:
            value = str(item).strip()

            if value:
                names.append(value)

    return names



def build_document(news):

    entities = news.get("entities", {})


    # -------------------------
    # Extraction entités
    # -------------------------

    startups = extract_entity_names(
        entities.get("startups", [])
    )

    investors = extract_entity_names(
        entities.get("investors", [])
    )

    funds = extract_entity_names(
        entities.get("funds", [])
    )


    sectors = news.get("sectors", [])

    countries = news.get("countries", [])



    # -------------------------
    # Texte utilisé pour embedding
    # -------------------------

    text = f"""
Titre:
{news.get("title", "")}


Résumé:
{news.get("summary", "")}


Date:
{news.get("date", "")}


Catégorie:
{news.get("category", "")}


Secteurs:
{", ".join(sectors)}


Pays:
{", ".join(countries)}


Startups mentionnées:
{", ".join(startups)}


Investisseurs:
{", ".join(investors)}


Fonds:
{", ".join(funds)}


Article:
{news.get("content", "")}
""".strip()



    return {

        "id": news.get("id"),


        # Texte pour embeddings
        "text": text,


        # Données structurées
        "title": news.get("title"),

        "summary": news.get("summary"),

        "content": news.get("content"),

        "date": news.get("date"),

        "category": news.get("category"),


        "countries": countries,

        "sectors": sectors,


        # On garde les objets JSON originaux
        "startups": entities.get(
            "startups",
            []
        ),

        "investors": entities.get(
            "investors",
            []
        ),

        "funds": entities.get(
            "funds",
            []
        ),



        "metadata": {

            "title": news.get("title"),

            "date": news.get("date"),

            "category": news.get("category"),

            "countries": countries,

            "sectors": sectors,

            "source_url": news.get("source_url")

        }
    }



def main():

    with open(
        INPUT,
        "r",
        encoding="utf-8"
    ) as f:

        news = json.load(f)



    documents = []

    for article in news:

        doc = build_document(article)

        documents.append(doc)



    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )


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
        f"{len(documents)} documents created"
    )



if __name__ == "__main__":
    main()
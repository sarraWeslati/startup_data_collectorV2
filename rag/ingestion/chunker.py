import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


# ==============================
# CONFIG
# ==============================

INPUT = Path("../data/documents.json")
OUTPUT = Path("../data/chunks.json")


# ==============================
# FORMAT ENTITIES
# ==============================

def format_entities(items):

    if not items:
        return "Aucune"

    result = []

    for item in items:

        if isinstance(item, dict):

            name = item.get("name", "")

            details = []

            for key, value in item.items():

                if key != "name" and value:

                    if isinstance(value, list):
                        value = ", ".join(value)

                    details.append(
                        f"{key}: {value}"
                    )

            if name:

                if details:
                    result.append(
                        f"{name} ({', '.join(details)})"
                    )
                else:
                    result.append(name)

        else:
            result.append(str(item))


    return "\n".join(result) if result else "Aucune"



# ==============================
# GET FIELD
# ==============================

def get_field(doc, metadata, field):

    return (
        doc.get(field)
        or metadata.get(field)
        or []
    )



# ==============================
# MAIN
# ==============================

def main():


    with open(INPUT, "r", encoding="utf-8") as f:

        documents = json.load(f)



    splitter = RecursiveCharacterTextSplitter(

       chunk_size=700,
       chunk_overlap=100,

        separators=[
            "\n\n",
            "\n",
            ". ",
            " "
        ]

    )


    chunks = []


    for doc in documents:


        metadata_original = doc.get(
            "metadata",
            {}
        )


        document_id = (
            doc.get("id")
            or metadata_original.get("document_id")
            or "unknown"
        )


        title = (
            doc.get("title")
            or metadata_original.get("title")
            or ""
        )


        summary = (
            doc.get("summary")
            or ""
        )


        content = (
            doc.get("content")
            or doc.get("text")
            or ""
        )


        if not content:
            continue



        # ==========================
        # ENTITIES
        # ==========================

        startups = get_field(
            doc,
            metadata_original,
            "startups"
        )


        investors = get_field(
            doc,
            metadata_original,
            "investors"
        )


        funds = get_field(
            doc,
            metadata_original,
            "funds"
        )


        countries = (
            doc.get("countries")
            or metadata_original.get("countries")
            or []
        )


        sectors = (
            doc.get("sectors")
            or metadata_original.get("sectors")
            or []
        )



        # ==========================
        # TEXT SPLITTING
        # ==========================

        text_chunks = splitter.split_text(
            content
        )



        for index, chunk in enumerate(text_chunks):


            enriched_text = f"""
Titre:
{title}


Résumé:
{summary}


Startups mentionnées:
{format_entities(startups)}


Investisseurs mentionnés:
{format_entities(investors)}


Fonds mentionnés:
{format_entities(funds)}


Pays:
{", ".join(countries) if countries else "Aucun"}


Secteurs:
{", ".join(sectors) if sectors else "Aucun"}


Article:
{chunk}
""".strip()



            chunk_metadata = {


                "document_id":
                document_id,


                "chunk_number":
                index,


                "title":
                title,


                "date":
                (
                    doc.get("date")
                    or metadata_original.get("date")
                    or ""
                ),


                "category":
                (
                    doc.get("category")
                    or metadata_original.get("category")
                    or ""
                ),


                "countries":
                countries,


                "sectors":
                sectors,


                "source_url":
                (
                    metadata_original.get(
                        "source_url",
                        ""
                    )
                ),


                "startups":
                startups,


                "investors":
                investors,


                "funds":
                funds

            }



            chunks.append(

                {

                    "chunk_id":
                    f"{document_id}_{index}",


                    "text":
                    enriched_text,


                    "metadata":
                    chunk_metadata

                }

            )



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

            chunks,

            f,

            ensure_ascii=False,

            indent=2

        )


    print(
        f"✅ {len(chunks)} chunks created"
    )



if __name__ == "__main__":
    main()
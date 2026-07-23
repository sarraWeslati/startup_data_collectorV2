# document_builder.py

import json
from pathlib import Path
from datetime import datetime
import hashlib


# =====================================================
# CONFIGURATION
# =====================================================

ROOT_DIR = Path(
    r"C:\Users\Dell\Downloads\startup_data_collectorV2-main\startup_data_collectorV2"
)


# Articles
ARTICLES_FILE = (
    ROOT_DIR
    / "cleaningNews"
    / "clean_news.json"
)


# Startups : plusieurs fichiers JSON
STARTUPS_DIR = (
    ROOT_DIR
    / "etl"
    / "deduplicated"
    / "startups"
)


# Investors : plusieurs fichiers JSON
INVESTORS_DIR = (
    ROOT_DIR
    / "etl"
    / "deduplicated"
    / "investors"
)


# Output RAG
OUTPUT_FILE = (
    ROOT_DIR
    / "rag"
    / "data"
    / "documents.json"
)



# =====================================================
# CHAMPS A EXCLURE DU TEXTE RAG
# =====================================================

IGNORED_FIELDS = {

    "text_for_rag",

    "_source_file",

    "etl",

    "quality",

    "stats",

    "validation",

    "confidence",

    "enrichment",

    "tavily",

}



# =====================================================
# LOAD JSON FILE OR DIRECTORY
# =====================================================

def load_json(path):

    results = []


    # -----------------------------
    # JSON FILE
    # -----------------------------

    if path.is_file():

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)


                if isinstance(data, list):

                    results.extend(data)

                else:

                    results.append(data)


        except Exception as e:

            print(
                f"[ERROR] {path} : {e}"
            )


    # -----------------------------
    # DIRECTORY
    # -----------------------------

    elif path.is_dir():


        files = list(
            path.glob("*.json")
        )


        print(
            f"[INFO] {path.name}: {len(files)} JSON files"
        )


        for file in files:


            try:

                with open(
                    file,
                    "r",
                    encoding="utf-8"
                ) as f:


                    data = json.load(f)


                    if isinstance(data,list):

                        results.extend(data)

                    else:

                        results.append(data)


            except Exception as e:

                print(
                    f"[ERROR] {file}: {e}"
                )


    else:

        print(
            f"[WARNING] Missing : {path}"
        )


    return results



# =====================================================
# CLEAN JSON BEFORE RAG
# =====================================================

def clean_for_rag(data):

    """
    Supprime les champs inutiles
    mais garde raw_data complet
    """

    if isinstance(data, dict):

        cleaned = {}


        for key,value in data.items():


            if key in IGNORED_FIELDS:

                continue


            cleaned[key] = clean_for_rag(value)


        return cleaned



    elif isinstance(data,list):

        return [
            clean_for_rag(x)
            for x in data
        ]



    else:

        return data



# =====================================================
# FLATTEN JSON
# =====================================================

def flatten_json(data, prefix=""):


    lines = []


    if isinstance(data, dict):


        for key,value in data.items():


            current_key = (
                f"{prefix}.{key}"
                if prefix
                else key
            )


            if isinstance(value,(dict,list)):


                lines.extend(
                    flatten_json(
                        value,
                        current_key
                    )
                )


            else:


                if value not in [
                    "",
                    None
                ]:


                    lines.append(
                        f"{current_key}: {value}"
                    )



    elif isinstance(data,list):


        for index,item in enumerate(data):


            lines.extend(
                flatten_json(
                    item,
                    f"{prefix}[{index}]"
                )
            )


    return lines




# =====================================================
# UNIQUE ID
# =====================================================

def generate_id(item):


    base = (

        item.get("name")

        or

        item.get("title")

        or

        str(item)

    )


    return hashlib.md5(
        base.encode("utf-8")
    ).hexdigest()[:12]



# =====================================================
# CREATE DOCUMENT
# =====================================================

def create_document(
        item,
        entity_type,
        source
):


    cleaned = clean_for_rag(item)


    text = "\n".join(
        flatten_json(cleaned)
    )


    return {


        "id":
            generate_id(item),



        "entity_type":
            entity_type,



        "text":
            text,



        "metadata": {


            "source":
                source,


            "entity_type":
                entity_type,


            "name":
                item.get(
                    "name",
                    item.get(
                        "title",
                        ""
                    )
                ),


            "country":
                item.get(
                    "country",
                    ""
                ),


            "city":
                item.get(
                    "city",
                    ""
                ),


            "industry":
                item.get(
                    "industry",
                    item.get(
                        "sector",
                        ""
                    )
                ),


            "date":
                item.get(
                    "date",
                    ""
                ),


            "created_at":
                datetime.now().isoformat()

        },



        # ORIGINAL COMPLET
        "raw_data":
            item

    }





# =====================================================
# BUILD DOCUMENTS
# =====================================================

def build_documents():


    documents = []



    # -------------------------
    # STARTUPS
    # -------------------------

    startups = load_json(
        STARTUPS_DIR
    )


    print(
        f"[STARTUPS] {len(startups)}"
    )


    for startup in startups:


        documents.append(

            create_document(
                startup,
                "startup",
                "deduplicated/startups"
            )

        )




    # -------------------------
    # INVESTORS
    # -------------------------

    investors = load_json(
        INVESTORS_DIR
    )


    print(
        f"[INVESTORS] {len(investors)}"
    )


    for investor in investors:


        documents.append(

            create_document(
                investor,
                "investor",
                "deduplicated/investors"
            )

        )




    # -------------------------
    # ARTICLES
    # -------------------------

    articles = load_json(
        ARTICLES_FILE
    )


    print(
        f"[ARTICLES] {len(articles)}"
    )


    for article in articles:


        documents.append(

            create_document(
                article,
                "article",
                "clean_news.json"
            )

        )



    return documents




# =====================================================
# SAVE
# =====================================================

def save_documents(documents):


    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            documents,
            f,
            ensure_ascii=False,
            indent=2
        )




# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":


    print(
        "\n========== BUILD RAG DOCUMENTS ==========\n"
    )


    docs = build_documents()



    save_documents(
        docs
    )



    print(
        "\n========================================="
    )


    print(
        f"TOTAL DOCUMENTS : {len(docs)}"
    )


    print(
        f"OUTPUT : {OUTPUT_FILE}"
    )


    print(
        "=========================================\n"
    )
import json
import re
from pathlib import Path


INPUT_FILE = Path("../data/documents.json")
OUTPUT_FILE = Path("../data/clean_documents.json")


# =====================================
# Regex
# =====================================

URL_REGEX = re.compile(
    r'https?://\S+',
    re.IGNORECASE
)

EMAIL_REGEX = re.compile(
    r'\S+@\S+\.\S+'
)

MARKDOWN_IMAGE_REGEX = re.compile(
    r'!\[.*?\]\(.*?\)'
)

MARKDOWN_LINK_REGEX = re.compile(
    r'\[([^\]]+)\]\([^\)]+\)'
)


# Mots inutiles venant des pages web

NOISE_WORDS = [
    "cookie",
    "accept all",
    "reject all",
    "privacy",
    "consent",
    "necessary cookies",
    "search",
    "subscribe",
    "newsletter",
    "follow us",
    "recent posts",
    "trending",
    "read also"
]


# =====================================
# Nettoyage texte
# =====================================

def clean_text(text):

    if not isinstance(text, str):
        return ""


    # supprimer images markdown

    text = MARKDOWN_IMAGE_REGEX.sub(
        "",
        text
    )


    # garder seulement le texte des liens markdown

    text = MARKDOWN_LINK_REGEX.sub(
        r"\1",
        text
    )


    # supprimer URLs

    text = URL_REGEX.sub(
        "",
        text
    )


    # supprimer emails

    text = EMAIL_REGEX.sub(
        "",
        text
    )



    clean_lines=[]


    for line in text.splitlines():

        line=line.strip()


        if not line:
            continue


        lower=line.lower()


        # supprimer bruit web

        if any(
            word in lower
            for word in NOISE_WORDS
        ):
            continue


        clean_lines.append(line)



    text=" ".join(clean_lines)



    # espaces multiples

    text=re.sub(
        r"\s+",
        " ",
        text
    )


    return text.strip()



# =====================================
# Pipeline nettoyage documents
# =====================================

def process():


    print("Loading documents...")


    with open(
        INPUT_FILE,
        encoding="utf-8"
    ) as f:

        documents=json.load(f)



    print(
        "Documents found:",
        len(documents)
    )



    cleaned=[]



    for i,doc in enumerate(documents):


        if i % 100 == 0:

            print(
                "Cleaning:",
                i,
                "/",
                len(documents)
            )



        # nettoyer le champ text

        if "text" in doc:

            doc["text"] = clean_text(
                doc["text"]
            )



        # nettoyer website_content si existe

        if "raw_data" in doc:

            if "website_content" in doc["raw_data"]:

                doc["raw_data"]["website_content"] = clean_text(
                    doc["raw_data"]["website_content"]
                )



        cleaned.append(doc)




    print("Saving clean file...")



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
        "Clean documents:",
        len(cleaned)
    )



if __name__ == "__main__":

    process()
import json
import hashlib
from pathlib import Path
from datetime import datetime


# ==============================
# CONFIG
# ==============================

ROOT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT_DIR / "data" / "rag_documents.json"

OUTPUT_FILE = ROOT_DIR / "data" / "chunks.json"


# taille chunk
CHUNK_SIZE = 350

# chevauchement entre chunks
CHUNK_OVERLAP = 50



# ==============================
# UTILS
# ==============================


def generate_id(text):
    """
    Génère un ID unique pour chaque chunk
    """
    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()[:12]



def clean_text(text):

    if not text:
        return ""

    text = text.replace("\n\n\n", "\n")
    text = text.replace("\r", " ")

    return " ".join(text.split())



# ==============================
# CHUNKING
# ==============================


def create_chunks(text):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + CHUNK_SIZE

        chunk_words = words[start:end]

        chunk = " ".join(chunk_words)

        chunks.append(chunk)


        start += CHUNK_SIZE - CHUNK_OVERLAP


    return chunks



# ==============================
# PROCESS
# ==============================


def process():


    print("Loading documents...")


    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        documents = json.load(f)



    print(
        f"Documents found : {len(documents)}"
    )



    all_chunks = []


    for doc in documents:


        text = clean_text(
            doc.get("text", "")
        )


        if not text:
            continue



        chunks = create_chunks(text)



        for index, chunk_text in enumerate(chunks):


            chunk = {

                "id": generate_id(
                    chunk_text
                ),


                "text": chunk_text,


                "metadata": {

                    **doc.get(
                        "metadata",
                        {}
                    ),


                    "chunk_index": index,


                    "total_chunks": len(chunks),


                    "original_document_id": doc.get(
                        "id"
                    ),


                    "created_at": datetime.now()
                    .isoformat()

                }

            }


            all_chunks.append(chunk)



    print(
        f"Chunks created : {len(all_chunks)}"
    )



    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_chunks,
            f,
            ensure_ascii=False,
            indent=2
        )



    print(
        "Saved:",
        OUTPUT_FILE
    )



# ==============================
# MAIN
# ==============================


if __name__ == "__main__":

    process()
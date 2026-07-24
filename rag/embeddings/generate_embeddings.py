import os
import json
import requests
import time
import numpy as np
import faiss

from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv



# =====================================
# CONFIG
# =====================================


load_dotenv()


API_KEY = os.getenv(
    "NVIDIA_API_KEY"
)


if not API_KEY:
    raise Exception(
        "NVIDIA_API_KEY missing"
    )



MODEL = "nvidia/nv-embed-v1"


URL = (
    "https://integrate.api.nvidia.com/v1/embeddings"
)



ROOT = Path(__file__).resolve().parent.parent



INPUT_FILE = (
    ROOT
    /
    "data"
    /
    "chunks.json"
)



VECTORSTORE_DIR = (
    ROOT
    /
    "vectorstore"
)



VECTORSTORE_DIR.mkdir(
    exist_ok=True
)



INDEX_FILE = (
    VECTORSTORE_DIR
    /
    "index.faiss"
)



METADATA_FILE = (
    VECTORSTORE_DIR
    /
    "metadata.json"
)



BATCH_SIZE = 8





# =====================================
# EMBEDDING API
# =====================================


def get_embeddings(texts):


    headers = {

        "Authorization":
        f"Bearer {API_KEY}",

        "Accept":
        "application/json",

        "Content-Type":
        "application/json"

    }



    payload = {


        "model":
        MODEL,


        "input":
        texts

    }




    response = requests.post(

        URL,

        headers=headers,

        json=payload,

        timeout=120

    )



    if response.status_code != 200:


        print(
            response.text
        )


        raise Exception(
            "NVIDIA embedding error"
        )




    data=response.json()



    return [

        item["embedding"]

        for item in data["data"]

    ]





# =====================================
# LOAD CHUNKS
# =====================================


def load_chunks():


    with open(

        INPUT_FILE,

        encoding="utf-8"

    ) as f:


        return json.load(f)





# =====================================
# BUILD FAISS
# =====================================


def main():


    print(
        "\nLoading chunks..."
    )


    chunks = load_chunks()



    print(

        "Chunks:",

        len(chunks)

    )




    vectors=[]


    metadata=[]




    for i in tqdm(

        range(

            0,

            len(chunks),

            BATCH_SIZE

        )

    ):


        batch = chunks[
            i:i+BATCH_SIZE
        ]



        texts=[

            x["text"]

            for x in batch

        ]



        embeddings = get_embeddings(
            texts
        )



        for chunk,vector in zip(

            batch,

            embeddings

        ):



            vectors.append(
                vector
            )



            metadata.append({

                "id":
                chunk["id"],


                "text":
                chunk["text"],


                "metadata":
                chunk["metadata"]

            })



        time.sleep(1)




    # ===============================
    # numpy vectors
    # ===============================


    vectors=np.array(

        vectors,

        dtype="float32"

    )



    print(

        "Vector shape:",

        vectors.shape

    )



    # cosine similarity

    faiss.normalize_L2(
        vectors
    )



    dimension = vectors.shape[1]



    # Index FAISS

    index = faiss.IndexFlatIP(
        dimension
    )



    index.add(
        vectors
    )



    print(

        "FAISS size:",

        index.ntotal

    )




    # save index


    faiss.write_index(

        index,

        str(INDEX_FILE)

    )




    # save metadata


    with open(

        METADATA_FILE,

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            metadata,

            f,

            ensure_ascii=False,

            indent=2

        )




    print("\n================")
    print("DONE ✅")
    print("================")


    print(

        "Index:",

        INDEX_FILE

    )


    print(

        "Metadata:",

        METADATA_FILE

    )





if __name__=="__main__":

    main()
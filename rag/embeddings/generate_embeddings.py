import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm


# =========================
# CONFIG
# =========================

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY")

if not API_KEY:
    raise Exception("NVIDIA_API_KEY missing")


MODEL = "nvidia/nv-embed-v1"

URL = "https://integrate.api.nvidia.com/v1/embeddings"


ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "chunks.json"

OUTPUT_FILE = ROOT / "data" / "embeddings.json"


BATCH_SIZE = 8



# =========================
# EMBEDDING FUNCTION
# =========================

def get_embeddings(texts):

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


    payload = {
        "model": "nvidia/nv-embed-v1",
        "input": texts
    }


    r = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=120
    )


    if r.status_code != 200:
        print("STATUS :", r.status_code)
        print(r.text)
        raise Exception("NVIDIA embedding failed")


    data = r.json()


    return [
        item["embedding"]
        for item in data["data"]
    ]

# =========================
# LOAD
# =========================

def load_chunks():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)



# =========================
# MAIN
# =========================

def main():

    print("Loading chunks...")

    chunks = load_chunks()

    print(
        "Chunks found :",
        len(chunks)
    )


    embeddings = []


    for i in tqdm(
        range(0, len(chunks), BATCH_SIZE)
    ):

        batch = chunks[i:i+BATCH_SIZE]


        texts = [
            x["text"]
            for x in batch
        ]


        vectors = get_embeddings(texts)


        for chunk, vector in zip(
            batch,
            vectors
        ):

            embeddings.append({

                "id": chunk["id"],

                "text": chunk["text"],

                "metadata": chunk["metadata"],

                "embedding": vector

            })


        time.sleep(1)



    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            embeddings,
            f,
            ensure_ascii=False,
            indent=2
        )


    print("\nDONE")
    print(
        "Embeddings:",
        len(embeddings)
    )

    print(
        "Saved:",
        OUTPUT_FILE
    )



if __name__ == "__main__":
    main()
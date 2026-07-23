import json
import os
import numpy as np
import faiss
from pathlib import Path
from tqdm import tqdm
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "embeddings.json"

VECTORSTORE_DIR = BASE_DIR / "vectorstore"

INDEX_FILE = VECTORSTORE_DIR / "index.faiss"

METADATA_FILE = VECTORSTORE_DIR / "metadata.json"

# ==============================
# LOAD EMBEDDINGS
# ==============================

def load_chunks():

    print("Loading embedded chunks...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)


    print(f"Chunks loaded : {len(chunks)}")

    return chunks



# ==============================
# BUILD FAISS INDEX
# ==============================

def build_index(chunks):

    print("Preparing vectors...")


    vectors = []

    for chunk in tqdm(chunks):

        embedding = chunk.get("embedding")

        if not embedding:
            continue

        vectors.append(
            embedding
        )


    vectors = np.array(
        vectors,
        dtype="float32"
    )


    print(
        f"Vectors shape : {vectors.shape}"
    )


    # --------------------------
    # Normalize vectors
    # cosine similarity
    # --------------------------

    faiss.normalize_L2(vectors)


    dimension = vectors.shape[1]


    print(
        f"Embedding dimension : {dimension}"
    )


    # --------------------------
    # FAISS index
    # --------------------------

    index = faiss.IndexFlatIP(
        dimension
    )


    index.add(vectors)


    print(
        f"FAISS index size : {index.ntotal}"
    )


    return index



# ==============================
# SAVE METADATA
# ==============================

def save_metadata(chunks):

    metadata = []


    for i, chunk in enumerate(chunks):

        item = {

            "index": i,

            "id": chunk.get("id"),

            "text": chunk.get("text"),

            "metadata": chunk.get("metadata")

        }

        metadata.append(item)



    VECTORSTORE_DIR.mkdir(
        exist_ok=True
    )


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


    print(
        f"Metadata saved : {METADATA_FILE}"
    )



# ==============================
# MAIN
# ==============================

def main():

    chunks = load_chunks()


    index = build_index(
        chunks
    )


    VECTORSTORE_DIR.mkdir(
        exist_ok=True
    )


    faiss.write_index(
        index,
        str(INDEX_FILE)
    )


    print(
        f"FAISS index saved : {INDEX_FILE}"
    )


    save_metadata(
        chunks
    )


    print("\nDONE ✅")



if __name__ == "__main__":
    main()
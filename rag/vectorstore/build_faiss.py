import json
import numpy as np
import faiss

from pathlib import Path



# =====================================
# PATHS
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent


EMBEDDINGS_FILE = (
    BASE_DIR /
    "embeddings" /
    "embeddings.npy"
)


CHUNKS_FILE = (
    BASE_DIR /
    "data" /
    "chunks.json"
)


OUTPUT_DIR = (
    BASE_DIR /
    "vectorstore"
)


INDEX_FILE = (
    OUTPUT_DIR /
    "index.faiss"
)


METADATA_FILE = (
    OUTPUT_DIR /
    "metadata.json"
)



# =====================================
# MAIN
# =====================================


def main():


    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    print("Loading embeddings...")


    embeddings = np.load(
        EMBEDDINGS_FILE
    )


    embeddings = embeddings.astype(
        "float32"
    )


    print(
        "Embedding shape:",
        embeddings.shape
    )


    dimension = embeddings.shape[1]



    print(
        "Creating FAISS index..."
    )


    index = faiss.IndexFlatIP(
        dimension
    )


    index.add(
        embeddings
    )


    print(
        "Vectors indexed:",
        index.ntotal
    )



    faiss.write_index(
        index,
        str(INDEX_FILE)
    )


    print(
        "FAISS saved:",
        INDEX_FILE
    )



    # -----------------------------
    # Metadata
    # -----------------------------


    print(
        "Loading chunks..."
    )


    with open(
        CHUNKS_FILE,
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)



    metadata = []


    for i, chunk in enumerate(chunks):


        metadata.append(

            {

                "index": i,


                "chunk_id":
                chunk.get(
                    "chunk_id"
                ),


                # IMPORTANT
                # garder le texte

                "text":
                chunk.get(
                    "text",
                    ""
                ),


                "metadata":
                chunk.get(
                    "metadata",
                    {}
                )

            }

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
        "Metadata saved:",
        len(metadata)
    )


    print(
        "\nVECTOR DATABASE READY ✅"
    )




if __name__ == "__main__":

    main()
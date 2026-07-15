import json
import numpy as np
import faiss

from pathlib import Path



EMBEDDINGS_FILE = Path("../data/embeddings.npy")

CHUNKS_FILE = Path("../data/chunks.json")


INDEX_FILE = Path("./index.faiss")

METADATA_FILE = Path("./metadata.json")



def main():


    print("Loading embeddings...")


    embeddings = np.load(
        EMBEDDINGS_FILE
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



    faiss.write_index(
        index,
        str(INDEX_FILE)
    )


    print(
        "FAISS saved"
    )



    with open(
        CHUNKS_FILE,
        encoding="utf-8"
    ) as f:

        chunks=json.load(f)



    metadata=[]



    for chunk in chunks:


        meta = chunk.get(
            "metadata",
            {}
        )


        metadata.append(

            {

                "chunk_id":
                chunk["chunk_id"],


                "text":
                chunk["text"],


                "metadata":

                {

                    "title":
                    meta.get("title"),


                    "date":
                    meta.get("date"),


                    "category":
                    meta.get("category"),


                    "sectors":
                    meta.get("sectors"),


                    "source_url":
                    meta.get("source_url"),


                    "chunk_number":
                    meta.get("chunk_number")

                }

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
        "Metadata saved"
    )



if __name__=="__main__":
    main()
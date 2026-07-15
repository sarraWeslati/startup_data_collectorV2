import json
import numpy as np
from pathlib import Path

from sentence_transformers import SentenceTransformer


INPUT_FILE = Path("../data/chunks.json")
OUTPUT_FILE = Path("../data/embeddings.npy")


MODEL_NAME = "BAAI/bge-m3"



def main():

    print("Loading chunks...")


    with open(
        INPUT_FILE,
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)



    print(
        "Chunks:",
        len(chunks)
    )


    print("Loading embedding model...")


    model = SentenceTransformer(
        MODEL_NAME
    )


    texts = [
        chunk["text"]
        for chunk in chunks
    ]



    print("Generating embeddings...")


    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True
    )



    embeddings = np.array(
        embeddings
    )



    np.save(
        OUTPUT_FILE,
        embeddings
    )


    print(
        "Embeddings saved:",
        OUTPUT_FILE
    )


    print(
        "Shape:",
        embeddings.shape
    )



if __name__ == "__main__":
    main()
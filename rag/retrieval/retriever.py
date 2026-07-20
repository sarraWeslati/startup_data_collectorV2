import json
import faiss
import numpy as np
import os

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI



# =====================================
# LOAD ENV
# =====================================

load_dotenv()


NVIDIA_API_KEY = os.getenv(
    "NVIDIA_API_KEY"
)


if not NVIDIA_API_KEY:
    raise ValueError(
        "NVIDIA_API_KEY missing"
    )



# =====================================
# PATHS
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent


INDEX_FILE = (
    BASE_DIR /
    "vectorstore" /
    "index.faiss"
)


METADATA_FILE = (
    BASE_DIR /
    "vectorstore" /
    "metadata.json"
)



# =====================================
# NVIDIA CONFIG
# =====================================


MODEL_NAME = (
    "nvidia/nv-embedqa-e5-v5"
)



client = OpenAI(

    base_url=
    "https://integrate.api.nvidia.com/v1",

    api_key=NVIDIA_API_KEY

)



# =====================================
# RETRIEVER
# =====================================


class Retriever:



    def __init__(self):


        print(
            "Loading FAISS index..."
        )


        self.index = faiss.read_index(

            str(INDEX_FILE)

        )



        print(
            "Loading metadata..."
        )


        with open(

            METADATA_FILE,

            encoding="utf-8"

        ) as f:

            self.metadata = json.load(f)



        print(
            "Retriever ready ✅"
        )




    # ---------------------------------

    # Generate query embedding

    # ---------------------------------

    def create_embedding(self, text):


        response = client.embeddings.create(

            model=MODEL_NAME,

            input=[text],

            extra_body={

                "input_type":
                "query"

            }

        )


        embedding = np.array(

            response.data[0].embedding,

            dtype="float32"

        )


        # normalisation

        embedding = embedding / np.linalg.norm(
            embedding
        )


        return embedding.reshape(
            1,
            -1
        )





    # ---------------------------------

    # Search

    # ---------------------------------

    def search(

        self,

        query,

        top_k=5,

        category=None,

        min_score=0.55

    ):



        print(
            "Embedding query..."
        )


        query_embedding = self.create_embedding(
            query
        )



        scores, indexes = self.index.search(

            query_embedding,

            top_k

        )



        results=[]



        for score, idx in zip(

            scores[0],

            indexes[0]

        ):



            if idx == -1:

                continue



            if score < min_score:

                continue



            item = self.metadata[idx]


            meta = item.get(
                "metadata",
                {}
            )



            if category:


                if meta.get(
                    "category"
                ) != category:

                    continue




            results.append(

                {

                    "score":
                    float(score),


                    "text":
                    item["text"],


                    "metadata":
                    meta

                }

            )



        return results





# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    retriever = Retriever()



    question = """

    Quelles startups tunisiennes ont levé des fonds en intelligence artificielle ?

    """



    results = retriever.search(

        question,

        top_k=10

    )



    for r in results:


        print(
            "\n===================="
        )


        print(
            "Score:",
            r["score"]
        )


        print(
            "Metadata:"
        )

        print(
            r["metadata"]
        )


        print(
            "\nTEXT:"
        )


        print(
            r["text"][:800]
        )
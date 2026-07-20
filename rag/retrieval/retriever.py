import json
import faiss
import numpy as np
import os

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI



load_dotenv()


API_KEY = os.getenv("NVIDIA_API_KEY")


if not API_KEY:
    raise ValueError("NVIDIA_API_KEY missing")



client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=API_KEY
)



MODEL_NAME = "nvidia/nv-embedqa-e5-v5"



BASE_DIR = Path(__file__).resolve().parent.parent


INDEX_FILE = BASE_DIR / "vectorstore/index.faiss"

METADATA_FILE = BASE_DIR / "vectorstore/metadata.json"





class Retriever:


    def __init__(self):


        print("Loading FAISS index...")


        self.index = faiss.read_index(
            str(INDEX_FILE)
        )



        print("Loading metadata...")


        with open(
            METADATA_FILE,
            encoding="utf-8"
        ) as f:

            self.metadata = json.load(f)



        print(
            f"Loaded documents : {len(self.metadata)}"
        )


        print("Retriever ready ✅")





    def embed_query(self, query):


        response = client.embeddings.create(

            model=MODEL_NAME,

            input=[query],

            extra_body={
                "input_type":"query"
            }

        )


        vector=np.array(
            response.data[0].embedding,
            dtype="float32"
        )


        vector /= np.linalg.norm(vector)


        return vector.reshape(1,-1)





    def search(
        self,
        query,
        top_k=5,
        min_score=0.50
    ):


        print("Embedding query...")


        vector=self.embed_query(query)



        scores, ids = self.index.search(

            vector,

            top_k

        )



        results=[]


        seen=set()



        for score,idx in zip(
            scores[0],
            ids[0]
        ):



            if idx == -1:
                continue



            if score < min_score:
                continue



            item=self.metadata[idx]


            meta=item.get(
                "metadata",
                {}
            )


            title=meta.get(
                "title",
                ""
            )


            if title.lower() in seen:
                continue


            seen.add(
                title.lower()
            )



            results.append({

                "score":float(score),

                "title":title,

                "date":meta.get(
                    "date",
                    ""
                ),

                "metadata":meta,

                "text":item.get(
                    "text",
                    ""
                )

            })



        return results
import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer



INDEX_FILE="../vectorstore/index.faiss"

METADATA_FILE="../vectorstore/metadata.json"


MODEL_NAME="BAAI/bge-m3"



class Retriever:


    def __init__(self):


        print(
            "Loading FAISS..."
        )


        self.index = faiss.read_index(
            INDEX_FILE
        )


        with open(
            METADATA_FILE,
            encoding="utf-8"
        ) as f:


            self.metadata=json.load(f)



        self.model = SentenceTransformer(
            MODEL_NAME
        )




    def search(

        self,

        query,

        top_k=20,

        category=None,

        min_score=0.55

    ):


        query_embedding = self.model.encode(

            [query],

            normalize_embeddings=True

        )


        query_embedding=np.array(
            query_embedding
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



            item=self.metadata[idx]



            meta=item["metadata"]



            if category:


                if meta.get("category") != category:

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





if __name__=="__main__":



    retriever=Retriever()



    question="""

    Quelles startups tunisiennes ont levé des fonds en intelligence artificielle ?

    """



    results=retriever.search(

        question,

        top_k=20,

        category="funding"

    )



    for r in results:


        print("\n================")


        print(
            "Score:",
            r["score"]
        )


        print(
            r["metadata"]
        )


        print(
            r["text"][:700]
        )
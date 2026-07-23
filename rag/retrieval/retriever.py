import os
import json
import requests
import numpy as np
import faiss

from dotenv import load_dotenv



# =====================================================
# PATHS
# =====================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BASE_DIR = os.path.dirname(
    CURRENT_DIR
)


VECTORSTORE_DIR = os.path.join(
    BASE_DIR,
    "vectorstore"
)


INDEX_FILE = os.path.join(
    VECTORSTORE_DIR,
    "index.faiss"
)


METADATA_FILE = os.path.join(
    VECTORSTORE_DIR,
    "metadata.json"
)



# =====================================================
# NVIDIA
# =====================================================

URL = "https://integrate.api.nvidia.com/v1/embeddings"

MODEL = "nvidia/nv-embed-v1"


load_dotenv()

API_KEY = os.getenv(
    "NVIDIA_API_KEY"
)


if not API_KEY:
    raise Exception(
        "Missing NVIDIA_API_KEY"
    )



# =====================================================
# LOAD VECTORSTORE
# =====================================================

print("\nLoading FAISS index...")


index = faiss.read_index(
    INDEX_FILE
)


print(
    "FAISS vectors:",
    index.ntotal
)


print(
    "Dimension:",
    index.d
)



with open(
    METADATA_FILE,
    encoding="utf-8"
) as f:

    metadata=json.load(f)



print(
    "Metadata:",
    len(metadata)
)




# =====================================================
# EMBEDDING
# =====================================================

def get_embedding(text):


    headers={

        "Authorization":
        f"Bearer {API_KEY}",

        "Content-Type":
        "application/json"

    }



    payload={

        "model":
        MODEL,

        "input":[text]

    }



    r=requests.post(

        URL,

        headers=headers,

        json=payload,

        timeout=120

    )



    print(
        "Embedding status:",
        r.status_code
    )



    if r.status_code != 200:

        print(r.text)

        raise Exception(
            "Embedding failed"
        )



    return np.array(

        r.json()["data"][0]["embedding"],

        dtype="float32"

    )




# =====================================================
# INTENT
# =====================================================

def detect_intent(query):


    q=query.lower()


    entity=None

    country=None



    if any(x in q for x in [

        "startup",
        "startups",
        "scaleup",
        "entreprise innovante",
        "entreprises innovantes"

    ]):

        entity="startup"



    elif any(x in q for x in [

        "investor",
        "investors",
        "investisseur",
        "investisseurs",
        "vc",
        "venture",
        "fonds",
        "capital"

    ]):

        entity="investor"



    elif any(x in q for x in [

        "news",
        "article",
        "actualité",
        "levée",
        "funding",
        "financement"

    ]):

        entity="article"



    if any(x in q for x in [

        "tunisie",
        "tunisia",
        "tunisian"

    ]):

        country="tunisia"



    return entity,country




# =====================================================
# INVESTOR FILTER
# =====================================================

def is_real_investor(meta):


    text=(

        str(meta.get("description",""))

        +

        str(meta.get("investment_focus",""))

        +

        str(meta.get("industry",""))

        +

        str(meta.get("investment_stages",""))

    ).lower()



    bad=[

        "law firm",
        "legal services"

    ]



    if any(
        b in text
        for b in bad
    ):

        return False



    good=[

        "venture",
        "capital",
        "investment",
        "fund",
        "invest",
        "portfolio",
        "startup",
        "equity",
        "seed",
        "angel"

    ]



    return any(
        g in text
        for g in good
    )




# =====================================================
# BUSINESS QUALITY
# =====================================================

def business_score(meta):


    entity=meta.get(
        "entity_type",
        ""
    ).lower()



    score=0



    if entity=="startup":


        fields=[

            "description",
            "industry",
            "founders",
            "products",
            "website"

        ]


        for f in fields:

            if meta.get(f):

                score+=0.2



    elif entity=="investor":


        fields=[

            "description",
            "investment_focus",
            "investment_stages",
            "portfolio_startups"

        ]


        for f in fields:

            if meta.get(f):

                score+=0.25



    elif entity=="article":


        fields=[

            "title",
            "summary",
            "content"

        ]


        for f in fields:

            if meta.get(f):

                score+=0.33



    return min(score,1)




# =====================================================
# HYBRID SEARCH
# =====================================================

def search(query,top_k=10):


    entity,country=detect_intent(query)



    print("\nFILTERS")
    print(
        "Entity:",
        entity
    )

    print(
        "Country:",
        country
    )



    vector=get_embedding(query)



    vector=np.array(
        [vector],
        dtype="float32"
    )


    faiss.normalize_L2(vector)



    scores,ids=index.search(

        vector,

        1000

    )



    results=[]



    for sim,idx in zip(

        scores[0],

        ids[0]

    ):


        if idx==-1:

            continue



        item=metadata[idx]

        meta=item.get(
            "metadata",
            {}
        )


        etype=str(

            meta.get(
                "entity_type",
                ""

            )

        ).lower()



        if entity and etype!=entity:

            continue



        if country:


            if country not in str(

                meta.get(
                    "country",
                    ""

                )

            ).lower():

                continue




        if entity=="investor":


            if not is_real_investor(meta):

                continue



        sim=float(sim)


        bscore=business_score(meta)



        final=(

            0.65*sim

            +

            0.35*bscore

        )



        results.append({

            "score":final,

            "similarity":sim,

            "metadata":meta,

            "text":item.get(
                "text",
                ""
            )

        })



    results.sort(

        key=lambda x:x["score"],

        reverse=True

    )



    # remove duplicate names

    output=[]

    seen=set()



    for r in results:


        name=str(

            r["metadata"].get(
                "name",
                ""
            )

        ).lower().strip()



        if not name:

            continue



        if name not in seen:

            seen.add(name)

            output.append(r)



    return output[:top_k]





# =====================================================
# TEST
# =====================================================

if __name__=="__main__":


    print(
        "\nHybrid RAG Retriever Ready ✅"
    )


    while True:


        q=input(
            "\nAsk > "
        )


        if q.lower() in [

            "exit",
            "quit"

        ]:

            break



        results=search(

            q,

            10

        )



        print(
            "\n====================="
        )

        print(
            "RESULTS:",
            len(results)
        )

        print(
            "====================="
        )



        for i,r in enumerate(

            results,

            1

        ):


            m=r["metadata"]


            print(
                f"\n--- Result {i} ---"
            )


            print(
                "Score:",
                round(
                    r["score"],
                    4
                )
            )


            print(
                "Type:",
                m.get("entity_type")
            )


            print(
                "Name:",
                m.get("name")
            )


            print(
                "Country:",
                m.get("country")
            )


            print(
                r["text"][:500]
            )
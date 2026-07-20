import os
import sys

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI



# =====================================
# IMPORT RETRIEVER
# =====================================


BASE_DIR = Path(__file__).resolve().parent.parent


sys.path.append(
    str(BASE_DIR / "retrieval")
)


from retriever import Retriever




# =====================================
# ENV
# =====================================


load_dotenv()


NVIDIA_API_KEY = os.getenv(
    "NVIDIA_API_KEY"
)


if not NVIDIA_API_KEY:

    raise ValueError(
        "NVIDIA_API_KEY missing in .env"
    )




# =====================================
# NVIDIA LLM CONFIG
# =====================================


client = OpenAI(

    base_url=
    "https://integrate.api.nvidia.com/v1",

    api_key=NVIDIA_API_KEY

)



MODEL_NAME = (
    "meta/llama-3.1-8b-instruct"
)





# =====================================
# QUERY ANALYZER
# =====================================


def detect_category(question):

    q = question.lower()



    funding_words = [

        "levée",

        "levé",

        "fonds",

        "financement",

        "funding",

        "investment",

        "investi",

        "série a",

        "series a",

        "series b",

        "capital"

    ]



    investor_words = [

        "investisseur",

        "fonds",

        "venture",

        "vc",

        "business angel"

    ]



    startup_words = [

        "startup",

        "entreprise",

        "société"

    ]



    for word in funding_words:

        if word in q:

            return "funding"



    for word in investor_words:

        if word in q:

            return "investor"



    for word in startup_words:

        if word in q:

            return "startup"



    return None






# =====================================
# GENERATE ANSWER
# =====================================


def generate_answer(question):


    print(
        "\nLoading retriever..."
    )


    retriever = Retriever()



    category = detect_category(
        question
    )



    print(
        "Detected category:",
        category
    )



    print(
        "\nSearching documents..."
    )



    results = retriever.search(

    question,

    top_k=15

      )




    if not results:


        return (
            "Je n'ai trouvé aucune information "
            "correspondante dans la base."
        )




    # -----------------------------
    # Construction contexte
    # -----------------------------


    context = ""



    sources = []



    for i, result in enumerate(results):


        meta = result["metadata"]



        context += f"""

========================

DOCUMENT {i+1}


Titre:
{meta.get('title')}


Date:
{meta.get('date')}


Catégorie:
{meta.get('category')}


Startups:
{meta.get('startups')}


Investisseurs:
{meta.get('investors')}


Fonds:
{meta.get('funds')}


Contenu:

{result['text']}


"""



        sources.append(

            meta.get(
                "source_url"
            )

        )






    # -----------------------------
    # Prompt LLM
    # -----------------------------


    prompt = f"""

Tu es un assistant expert du startup ecosystem africain.

Tu réponds uniquement avec les informations présentes
dans les documents fournis.


Règles importantes:

- Ne jamais inventer une information.
- Ne considère une startup comme financée que si le document
  indique clairement une levée de fonds.
- Différencie:
    * levée de fonds
    * admission accélérateur
    * programme startup
    * partenariat
    * événement
- Si l'information n'existe pas dans les documents,
  indique-le clairement.


Documents:


{context}



Question utilisateur:

{question}



Réponse:


"""




    print(
        "\nGenerating answer..."
    )



    response = client.chat.completions.create(


        model=MODEL_NAME,


        messages=[

            {

                "role":"system",

                "content":
                "You are a precise startup ecosystem analyst."

            },


            {

                "role":"user",

                "content":prompt

            }

        ],


        temperature=0.2,


        max_tokens=1000

    )



    answer = (
        response
        .choices[0]
        .message
        .content
    )




    # -----------------------------
    # Ajouter sources
    # -----------------------------


    final_answer = f"""


{answer}



Sources:

"""


    for url in set(sources):

        if url:

            final_answer += f"- {url}\n"



    return final_answer






# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    question = """

    Quelles startups tunisiennes ont levé
    des fonds récemment ?

    """



    answer = generate_answer(
        question
    )


    print(
        "\n=========================="
    )

    print(
        answer
    )
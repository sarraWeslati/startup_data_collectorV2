import os

from dotenv import load_dotenv
from openai import OpenAI



load_dotenv()


API_KEY=os.getenv(
    "NVIDIA_API_KEY"
)



client=OpenAI(

    base_url="https://integrate.api.nvidia.com/v1",

    api_key=API_KEY

)



MODEL_NAME="meta/llama-3.1-8b-instruct"





SYSTEM_PROMPT="""

Tu es un assistant RAG.

Tu réponds uniquement avec les informations
présentes dans le CONTEXTE.

Règles :

- Ne jamais inventer.
- Ne jamais utiliser tes connaissances externes.
- Si une information manque, dire :
  "Information non disponible dans les sources."

- Analyse toute la question avant de répondre.

- Pour les listes :
  extraire les éléments présents dans le contexte.

- Pour les startups :
  afficher si disponible :
  Nom
  Pays
  Secteur
  Fondateur
  Financement

- Pour les investisseurs :
  afficher :
  Nom
  Pays
  Type

- Pour les questions générales :
  faire une synthèse claire.

Toujours terminer par :

Sources utilisées :
- titre des articles utilisés


"""





def generate_answer(question, context):


    prompt=f"""

CONTEXTE :

{context}



QUESTION :

{question}



Réponds uniquement avec le contexte.

"""



    response=client.chat.completions.create(


        model=MODEL_NAME,


        messages=[

            {
                "role":"system",
                "content":SYSTEM_PROMPT
            },

            {
                "role":"user",
                "content":prompt
            }

        ],


        temperature=0.1,


        max_tokens=1200

    )



    return response.choices[0].message.content
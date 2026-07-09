# llm_extractor.py

import os
import json
import re
import time
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


LLM_TIMEOUT = int(
    os.getenv(
        "LLM_TIMEOUT",
        "60"
    )
)


MODEL = os.getenv(
    "NVIDIA_MODEL",
    "nvidia/nemotron-3-nano-30b-a3b"
)


client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=LLM_TIMEOUT,
    max_retries=1
)



AFRICAN_COUNTRIES = [
    "Africa",
    "Tunisia",
    "Egypt",
    "Morocco",
    "Algeria",
    "Nigeria",
    "Kenya",
    "South Africa",
    "Ghana",
    "Senegal",
    "Rwanda",
    "Ivory Coast",
    "Côte d'Ivoire",
    "Uganda",
    "Tanzania",
    "Ethiopia",
    "Cameroon",
    "Zambia",
    "Zimbabwe",
    "Botswana",
    "Namibia",
    "Libya",
    "Sudan",
    "Mali",
    "Mauritius"
]



def extract_json(text):

    """
    récupère JSON même si le LLM ajoute du texte
    """

    try:

        return json.loads(text)


    except:


        match = re.search(
            r"\{.*\}",
            text,
            re.S
        )


        if match:

            try:

                return json.loads(
                    match.group()
                )

            except:
                pass


    return None




def call_llm(content, source):

    started = time.time()

    print(
        "[LLM START]",
        source,
        flush=True
    )


    prompt = f"""
You are an expert African startup ecosystem analyst.

Analyze this article.

Your task:

1. Keep ONLY articles related to AFRICA.

Accepted:
- African countries
- African startups
- African investors
- African venture capital funds
- African entrepreneurship
- African technology ecosystem

Rejected:
- USA only
- Europe only
- Asia only
- crypto spam
- generic advertising


Return ONLY valid JSON.

Schema:

{{
"title":"",
"summary":"",
"content":"",
"country":"",
"category":"",
"entities":{{
    "startups":[],
    "investors":[],
    "funds":[]
}},
"source":"",
"date":"",
"keep":true
}}


Rules:

- date must be the publication date if available.
- country must contain African country.
- category:
  startup
  investment
  funding
  acquisition
  event
  report
  other

Article:

{content[:12000]}


Source:

{source}

"""


    try:

        response = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],

            temperature=0.1,

            max_tokens=2000
        )


        result = response.choices[0].message.content


        data = extract_json(
            result
        )

        print(
            "[LLM DONE]",
            source,
            f"{time.time() - started:.1f}s",
            flush=True
        )


        return data



    except Exception as e:

        print(
            "LLM ERROR:",
            source,
            f"{time.time() - started:.1f}s",
            e
        )

        return None





def extract_article(article):


    result = call_llm(

        article["markdown"],

        article["url"]

    )


    if not result:

        return None



    if result.get(
        "keep"
    ) != True:

        return None



    result.pop(
        "keep",
        None
    )


    return result

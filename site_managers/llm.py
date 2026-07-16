import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()


# ==============================
# CONFIG NVIDIA
# ==============================

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")


if not NVIDIA_API_KEY:
    raise Exception("❌ NVIDIA_API_KEY introuvable")


NVIDIA_URL = (
    "https://integrate.api.nvidia.com/v1/chat/completions"
)


NVIDIA_MODEL = (
    "meta/llama-3.1-8b-instruct"
)



# ==============================
# SYSTEM PROMPT
# ==============================

SYSTEM_PROMPT = """

You are a high precision African Startup Ecosystem Data Extractor.

Your job is to analyze startup ecosystem articles.

ONLY KEEP ARTICLES RELATED TO AFRICA.


=================================================
RELEVANCE FILTER
=================================================

The article is relevant ONLY if it talks about:

- startups
- startup companies
- founders
- fundraising
- funding rounds
- seed
- pre-seed
- Series A/B/C
- venture capital
- investors
- investment funds
- business angels
- accelerators
- incubators
- startup acquisitions
- startup ecosystem reports
- startup statistics
- startup revenue
- startup valuation


Reject:

- general technology news
- politics
- unrelated companies
- events without startup information
- generic economy news


If NOT relevant return ONLY:


{
    "relevant": false
}



=================================================
OUTPUT FORMAT
=================================================


If relevant return ONLY valid JSON:


{
"title":"",
"summary":"",
"content":"",

"country":"",
"region":"Africa",

"category":"",


"entities":{

    "startups":[],

    "investors":[],

    "accelerators":[],

    "incubators":[]

},



"funding":{

    "amount":"",
    "currency":"",
    "round":"",
    "investors":[]

},



"metrics":{

    "valuation":"",
    "revenue":"",
    "employees":"",
    "users":"",
    "growth":""

},


"date":"",

"relevant":true

}



=================================================
CATEGORY VALUES
=================================================

Choose ONE:

- funding
- startup
- investor
- acquisition
- accelerator
- incubator
- partnership
- ecosystem
- report
- statistics
- other



=================================================
EXTRACTION RULES
=================================================

Rules:

- Extract ALL startups mentioned.
- Extract ALL investors mentioned.
- Extract ALL funding amounts.
- Extract ALL funding rounds.
- Extract business numbers.
- Never invent information.
- Unknown values must be empty.
- If multiple investors exist, put them in an array.
- If multiple startups exist, put them in an array.
- Country must be an African country if relevant.
- Return ONLY JSON.
"""



# ==============================
# CLEAN JSON RESPONSE
# ==============================

def safe_json(raw):

    try:

        raw = raw.strip()


        if raw.startswith("```json"):

            raw = (
                raw
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )


        elif raw.startswith("```"):

            raw = raw.replace("```", "").strip()


        return json.loads(raw)


    except Exception as e:

        print(
            "JSON ERROR:",
            e
        )

        return {
            "relevant": False
        }



# ==============================
# LLM EXTRACTION
# ==============================

def llm_extract(
        url,
        title,
        text,
        date=""
):


    # limite tokens
    text = text[:5000]


    prompt = f"""

ARTICLE URL:
{url}


TITLE:
{title}


DATE:
{date}



CONTENT:

{text}



Analyze this article and extract startup ecosystem information.

"""


    headers = {

        "Authorization":
        f"Bearer {NVIDIA_API_KEY}",

        "Content-Type":
        "application/json"

    }



    payload = {


        "model":
        NVIDIA_MODEL,


        "messages":[

            {
                "role":"system",
                "content":SYSTEM_PROMPT
            },


            {
                "role":"user",
                "content":prompt
            }

        ],


        "temperature":0,


        "max_tokens":1500

    }



    try:


        response = requests.post(

            NVIDIA_URL,

            headers=headers,

            json=payload,

            timeout=60

        )


        response.raise_for_status()



        result = response.json()



        content = (
            result["choices"][0]
            ["message"]
            ["content"]
        )



        data = safe_json(content)



        # ajout source

        if data.get("relevant"):

            data["source"] = url


        return data



    except Exception as e:


        print(
            "[LLM ERROR]",
            e
        )


        return {

            "relevant":False

        }
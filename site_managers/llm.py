import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()


# ==================================================
# CONFIG NVIDIA
# ==================================================

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")


if not NVIDIA_API_KEY:
    raise Exception("❌ NVIDIA_API_KEY introuvable")


NVIDIA_URL = (
    "https://integrate.api.nvidia.com/v1/chat/completions"
)


NVIDIA_MODEL = (
    "meta/llama-3.1-8b-instruct"
)



# ==================================================
# SYSTEM PROMPT
# ==================================================

SYSTEM_PROMPT = """
You are a High Precision African Startup Ecosystem Data Extractor.

Your task is to analyze news articles and extract structured information about:
- African startups
- founders
- investors
- venture capital funds
- accelerators
- incubators
- fundraising events
- startup ecosystem events
- startup metrics

You MUST return ONLY valid JSON.
Do not add explanations.
Do not use markdown.
Do not create information that is not explicitly present in the article.

====================================================
1. RELEVANCE FILTER
====================================================

Set "relevant": true ONLY if the article is related to:

- Startup creation
- Startup launches
- Startup growth
- Startup acquisitions
- Startup awards
- Startup ecosystem
- Fundraising rounds
- Venture capital investment
- Angel investors
- Investment funds
- Accelerators
- Incubators
- Entrepreneurship programs
- Startup competitions
- Innovation hubs
- Technology companies with startup characteristics
- African technology ecosystem

Set "relevant": false for:

- General companies without startup context
- Government announcements without startup ecosystem relation
- Generic technology news
- General economic news
- Product advertisements
- Job announcements
- Training announcements without startup ecosystem relevance

====================================================
2. GEOGRAPHIC RULE
====================================================

KEEP ONLY articles related to Africa.

Accepted:
- Tunisia
- Morocco
- Algeria
- Egypt
- Kenya
- Nigeria
- South Africa
- Ghana
- Rwanda
- Senegal
- Ivory Coast
- Ethiopia
- Other African countries

If Africa relation is unclear:
relevant = false

====================================================
3. STARTUP EXTRACTION RULES
====================================================

Extract startups only when they are explicitly mentioned.

For each startup:

{
"name": "",
"founders": [],
"country": "",
"city": "",
"sector": ""
}


Rules:

- Do not confuse investors with startups.
- Do not extract organizations as startups unless they are companies.
- Do not extract examples mentioned only as references unless they are real startups.
- If founder is unknown use [].
- If city is unknown use "".
- If sector is unknown use "".


====================================================
4. INVESTOR EXTRACTION RULES
====================================================

Extract:

- Venture capital funds
- Private equity funds
- Business angels
- Institutional investors
- Investment organizations


Format:

"investors": [
{
"name": "",
"type": "",
"country": ""
}
]


Do not extract:
- Government ministries
- Banks unless they invest in startups
- Partners without investment role


====================================================
5. FUNDING EXTRACTION RULES
====================================================


Extract fundraising information:

{
"amount": "",
"currency": "",
"round": "",
"investors": []
}


Examples:

"$5 million Series A"

becomes:

{
"amount":"5000000",
"currency":"USD",
"round":"Series A"
}


Rules:

- Convert million/billion numbers into full numbers.
- If unknown keep empty string.
- Do not guess funding rounds.


====================================================
6. METRICS EXTRACTION
====================================================

Extract only explicit numbers:

{
"valuation":"",
"revenue":"",
"employees":"",
"users":"",
"growth":""
}


Examples:

"500,000 users"

=> users:"500000"


====================================================
7. CATEGORY CLASSIFICATION
====================================================

Choose one category:

- Startup
- Funding
- Venture Capital
- Investor
- Accelerator
- Incubator
- Startup Ecosystem
- Startup Award
- Acquisition
- Innovation
- Technology


====================================================
8. OUTPUT FORMAT
====================================================


Return exactly:

{
"title":"",
"summary":"",
"content":"",

"country":"",
"region":"Africa",

"category":"",

"entities":{

"startups":[
{
"name":"",
"founders":[],
"country":"",
"city":"",
"sector":""
}
],

"investors":[
{
"name":"",
"type":"",
"country":""
}
],

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

"relevant":true,

"source":""

}


====================================================
9. IMPORTANT QUALITY RULES
====================================================

- Precision is more important than recall.
- Never hallucinate.
- Never invent founders.
- Never invent funding amounts.
- Never infer investors.
- Preserve original article meaning.
- Extract only facts contained in the article.
- Return valid JSON only.

"""

# ==================================================
# SAFE JSON PARSER
# ==================================================

def safe_json(raw):

    try:

        raw = raw.strip()


        if raw.startswith("```"):

            raw = (
                raw
                .replace("```json","")
                .replace("```","")
                .strip()
            )


        return json.loads(raw)



    except Exception as e:

        print(
            "[JSON ERROR]",
            e
        )

        return {
            "relevant":False
        }



# ==================================================
# ENTITY CLEANING
# ==================================================

def clean_entities(data):


    if not data.get("relevant"):

        return data



    entities = data.get(
        "entities",
        {}
    )



    # ----------------------------
    # CLEAN STARTUPS
    # ----------------------------


    clean_startups=[]


    for startup in entities.get(
        "startups",
        []
    ):


        if isinstance(startup,str):

            clean_startups.append({

                "name":startup,
                "founders":[],
                "country":"",
                "city":"",
                "sector":""

            })


        elif isinstance(startup,dict):

            if startup.get("name"):

                clean_startups.append(startup)



    entities["startups"] = clean_startups



    # ----------------------------
    # CLEAN INVESTORS
    # ----------------------------


    bad_words={

        "investisseur",
        "investisseurs",
        "financement",
        "fonds",
        "partenaire",
        "partenaires",
        "jury",
        "experts",
        "glovo"

    }



    investors=[]


    for inv in entities.get(
        "investors",
        []
    ):


        if isinstance(inv,str):

            if inv.lower() not in bad_words:

                investors.append(inv)



    entities["investors"]=investors



    data["entities"]=entities


    return data



# ==================================================
# LLM EXTRACTION FUNCTION
# ==================================================

def llm_extract(
        url,
        title,
        text,
        date=""
):


    text=text[:8000]



    prompt=f"""

ARTICLE URL:

{url}



TITLE:

{title}



DATE:

{date}



CONTENT:

{text}



Analyze this article.

Return JSON only.

"""



    headers={

        "Authorization":
        f"Bearer {NVIDIA_API_KEY}",

        "Content-Type":
        "application/json"

    }



    payload={


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


        "max_tokens":2000

    }



    try:


        response=requests.post(

            NVIDIA_URL,

            headers=headers,

            json=payload,

            timeout=60

        )



        response.raise_for_status()



        result=response.json()



        content=(

            result
            ["choices"]
            [0]
            ["message"]
            ["content"]

        )



        data=safe_json(content)



        data=clean_entities(data)



        if data.get("relevant"):

            data["source"]=url



        return data




    except Exception as e:


        print(
            "[LLM ERROR]",
            e
        )


        return {

            "relevant":False

        }
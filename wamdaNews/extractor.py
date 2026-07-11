import json
import re
import requests


from config import (
    NVIDIA_API_KEY,
    NVIDIA_MODEL,
    NVIDIA_URL,
    LLM_TIMEOUT,
    MAX_TOKENS,
    VALID_CATEGORIES
)



HEADERS = {

    "Authorization":
    f"Bearer {NVIDIA_API_KEY}",

    "Content-Type":
    "application/json",

    "Accept":
    "application/json"

}



SYSTEM_PROMPT = """

You are a startup ecosystem intelligence analyst.

Your task:
Extract ONLY African startup ecosystem news.

Return ONLY valid JSON.

The article is relevant ONLY if it contains:

- startup funding
- fundraising
- seed round
- pre-seed
- Series A/B/C
- venture capital investment
- investor investing in startup
- startup acquisition
- accelerator/incubator investing in startups


Reject:

- UAE news
- Saudi Arabia news
- Qatar news
- Bahrain news
- GCC news
- Europe
- USA
- Asia

Keep only Africa:

Tunisia
Egypt
Morocco
Algeria
Nigeria
Kenya
Ghana
Senegal
South Africa
Rwanda
Ivory Coast
Uganda
Tanzania
African countries


Return this exact structure:


{
"title":"",
"summary":"",
"content":"",
"country":"",
"region":"Africa",
"category":"",
"entities":{
    "startup":"",
    "investor":"",
    "fund":"",
    "accelerator":""
},
"funding":{
    "amount":"",
    "round":"",
    "investors":""
},
"date":"",
"relevant":true
}



category MUST be ONLY one string:

funding
investment
acquisition
accelerator
startup


Never return an object for category.

Never invent information.

If not relevant return:

{
"relevant":false
}


"""

def clean_json(text):


    if not text:

        return None



    text=text.replace(
        "```json",
        ""
    )


    text=text.replace(
        "```",
        ""
    )



    match=re.search(
        r"\{.*\}",
        text,
        re.S
    )



    if not match:

        print(
            "NO JSON FOUND"
        )

        return None



    try:

        return json.loads(
            match.group()
        )


    except Exception as e:


        print(
            "JSON ERROR",
            e
        )


        return None






def call_llm(prompt):


    payload={


        "model":
        NVIDIA_MODEL,


        "messages":[


            {

                "role":
                "system",

                "content":
                SYSTEM_PROMPT

            },


            {

                "role":
                "user",

                "content":
                prompt

            }


        ],



        "temperature":
        0,


        "max_tokens":
        MAX_TOKENS

    }




    try:


        print(
            "CALL NVIDIA..."
        )


        r=requests.post(

            NVIDIA_URL,

            headers=HEADERS,

            json=payload,

            timeout=LLM_TIMEOUT

        )



        print(
            "LLM STATUS:",
            r.status_code
        )



        if r.status_code != 200:


            print(
                r.text[:500]
            )


            return None




        result=r.json()



        return (

            result
            ["choices"]
            [0]
            ["message"]
            ["content"]

        )



    except Exception as e:


        print(
            "LLM ERROR:",
            e
        )


        return None







def validate_news(data):


    if not data:
        return False


    if data.get("relevant") is False:
        return False



    category=data.get(
        "category",
        ""
    )


    if isinstance(category,dict):

        print(
            "CATEGORY DICT FIX"
        )


        category=list(category.keys())[0]

        data["category"]=category



    category=category.lower()



    allowed=[
        "funding",
        "investment",
        "acquisition",
        "accelerator",
        "startup"
    ]


    if category not in allowed:

        print(
            "BAD CATEGORY",
            category
        )

        return False



    entities=data.get(
        "entities",
        {}
    )


    if not isinstance(
        entities,
        dict
    ):

        return False



    if not any(entities.values()):

        return False



    return True




def extract_news(
        content,
        url,
        title=""
):



    prompt=f"""

ARTICLE URL:

{url}


ARTICLE TITLE:

{title}


ARTICLE CONTENT:

{content}



Extract startup ecosystem information.

Return JSON only.

"""



    response=call_llm(
        prompt
    )



    if not response:


        return None




    print(
        "LLM RESPONSE:"
    )


    print(
        response[:1000]
    )



    data=clean_json(
        response
    )



    if not data:

        return None



    data["source"]=url




    if validate_news(data):


        print(
            "VALID NEWS"
        )


        return data



    print(
        "FILTERED:",
        title
    )


    return None
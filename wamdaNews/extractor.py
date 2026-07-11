import json
import re
import requests


from config import (

    NVIDIA_API_KEY,
    NVIDIA_MODEL,
    NVIDIA_URL,

    LLM_TIMEOUT,
    MAX_TOKENS,

    AFRICA_KEYWORDS,
    MENA_KEYWORDS,

    VALID_CATEGORIES

)

print("\n========== NVIDIA CONFIG ==========")

print(
    "MODEL:",
    NVIDIA_MODEL
)

print(
    "URL:",
    NVIDIA_URL
)

print(
    "KEY EXISTS:",
    bool(NVIDIA_API_KEY)
)

print(
    "KEY START:",
    NVIDIA_API_KEY[:10]
    if NVIDIA_API_KEY
    else "EMPTY"
)

print(
    "KEY LENGTH:",
    len(NVIDIA_API_KEY)
    if NVIDIA_API_KEY
    else 0
)

print(
    "==================================\n"
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

You extract startup ecosystem news.

Return ONLY JSON.


Fields:

title
summary
content
country
region
category
entities
funding
date
relevant



Categories:

funding:
startup raised money, seed, series A/B/C, funding round


investment:
investor invested in startup


investor:
VC or investment fund article


startup:
startup profile


report:
startup ecosystem analysis



Only keep MENA or Africa startup ecosystem news.

Never invent information.

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
            "❌ NO JSON FOUND"
        )

        return None



    try:

        return json.loads(
            match.group()
        )


    except Exception as e:

        print(
            "JSON ERROR:",
            e
        )

        return None





def call_llm(prompt):


    print("\n========== LLM REQUEST ==========")


    print(
        "MODEL:",
        NVIDIA_MODEL
    )


    print(
        "URL:",
        NVIDIA_URL
    )


    print(
        "PROMPT LENGTH:",
        len(prompt)
    )


    print(
        "PROMPT PREVIEW:"
    )

    print(
        prompt[:500]
    )


    print(
        "================================"
    )



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



    print(
        "\nSENDING REQUEST..."
    )


    try:


        r=requests.post(


            NVIDIA_URL,


            headers=HEADERS,


            json=payload,


            timeout=LLM_TIMEOUT


        )


        print(
            "\n========== NVIDIA RESPONSE =========="
        )


        print(
            "STATUS:",
            r.status_code
        )


        print(
            "HEADERS:"
        )


        print(
            dict(r.headers)
        )


        print(
            "BODY:"
        )


        print(
            r.text[:1000]
        )


        print(
            "====================================\n"
        )



        if r.status_code != 200:

            return None



        result=r.json()


        print(
            "JSON KEYS:",
            result.keys()
        )


        content=(

            result
            ["choices"]
            [0]
            ["message"]
            ["content"]

        )


        print(
            "CONTENT LENGTH:",
            len(content)
        )


        return content



    except Exception as e:


        print(
            "REQUEST EXCEPTION:"
        )

        print(
            type(e),
            e
        )


        return None


def validate_news(data):


    if not data:

        return False



    # =========================
    # REGION CHECK
    # =========================

    text = json.dumps(
        data,
        ensure_ascii=False
    ).lower()



    region_words = (
        AFRICA_KEYWORDS
        +
        MENA_KEYWORDS
    )



    if not any(

        word.lower() in text

        for word in region_words

    ):

        print(
            "❌ NOT AFRICA/MENA"
        )

        return False




    # =========================
    # CATEGORY CHECK
    # =========================


    category = data.get(
        "category",
        ""
    ).lower()



    title = data.get(
        "title",
        ""
    ).lower()



    # correction funding automatique

    if any(

        x in title

        for x in [

            "raise",
            "raised",
            "raises",
            "funding",
            "series",
            "investment",
            "million"

        ]

    ):

        data["category"] = "funding"

        category = "funding"



    if category not in VALID_CATEGORIES:


        print(
            "❌ INVALID CATEGORY:",
            category
        )


        return False





    # =========================
    # ENTITY CHECK
    # =========================


    entities = data.get(
        "entities",
        {}
    )



    if isinstance(
        entities,
        dict
    ):



        count = len(
            entities.keys()
        )



    else:

        count = 0




    if count == 0:


        print(
            "❌ NO ENTITIES"
        )


        return False




    print(
        "✅ ENTITIES:",
        count
    )



    return True



def extract_news(

        content,

        url,

        title=""

):


    prompt=f"""

URL:

{url}


TITLE:

{title}


ARTICLE:

{content}



Extract information as JSON.

"""



    response=call_llm(prompt)



    print(
        "\n===== RESPONSE ====="
    )

    print(response)

    print(
        "===================="
    )



    data=clean_json(response)



    if not data:

        return None




    data["source"]=url



    if validate_news(data):


        print(
            "VALID NEWS"
        )


        return data



    print(
        "FILTERED",
        title
    )


    return None
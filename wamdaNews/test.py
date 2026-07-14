import requests


API_KEY="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"


url="https://integrate.api.nvidia.com/v1/chat/completions"



headers={

    "Authorization": f"Bearer {API_KEY}",

    "Content-Type":"application/json",

    "Accept":"application/json"

}



data={

    "model":"meta/llama-3.1-8b-instruct",

    "messages":[

        {

            "role":"user",

            "content":"Hello"

        }

    ],

    "max_tokens":20

}



response=requests.post(

    url,

    headers=headers,

    json=data

)



print(response.status_code)

print(response.text)
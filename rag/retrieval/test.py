import os
import requests
import numpy as np

from dotenv import load_dotenv


# ==================================
# LOAD ENV
# ==================================

load_dotenv()


NVIDIA_API_KEY = os.getenv(
    "NVIDIA_API_KEY"
)


if not NVIDIA_API_KEY:
    raise Exception(
        "NVIDIA_API_KEY missing in .env"
    )


# ==================================
# CONFIG NVIDIA
# ==================================

NVIDIA_API_URL = (
    "https://integrate.api.nvidia.com/v1/embeddings"
)


MODEL = "baai/bge-m3"



# ==================================
# TEST EMBEDDING
# ==================================

def get_embedding(text):


    headers = {

        "Authorization":
            f"Bearer {NVIDIA_API_KEY}",

        "Content-Type":
            "application/json"

    }


    payload = {

        "model":
            MODEL,

        "input":
            [
                text
            ],

        "input_type":
            "query",

        "encoding_format":
            "float"

    }


    print("\nSending request...")
    print("Model :", MODEL)
    print("Text :", text)



    response = requests.post(

        NVIDIA_API_URL,

        headers=headers,

        json=payload,

        timeout=60

    )



    print("\n====================")
    print("STATUS CODE :", response.status_code)
    print("====================")



    print("\nResponse:")
    print(response.text[:1000])



    if response.status_code != 200:

        raise Exception(
            "NVIDIA embedding request failed"
        )



    data = response.json()



    embedding = data["data"][0]["embedding"]



    return np.array(
        embedding,
        dtype="float32"
    )





# ==================================
# MAIN TEST
# ==================================

if __name__ == "__main__":


    print(
        "\n===== NVIDIA EMBEDDING TEST ====="
    )


    text = (
        "les startups tunisiennes "
        "dans le domaine de la technologie"
    )


    vector = get_embedding(
        text
    )


    print(
        "\n===== SUCCESS ====="
    )


    print(
        "Embedding dimension :",
        len(vector)
    )


    print(
        "First 10 values :"
    )


    print(
        vector[:10]
    )
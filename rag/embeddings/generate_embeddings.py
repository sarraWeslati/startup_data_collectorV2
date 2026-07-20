import os
import json
import numpy as np

from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

from openai import OpenAI



# =====================================
# LOAD ENV
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
# PATHS
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent


INPUT_FILE = (
    BASE_DIR /
    "data" /
    "chunks.json"
)


OUTPUT_DIR = (
    BASE_DIR /
    "embeddings"
)


OUTPUT_EMBEDDINGS = (
    OUTPUT_DIR /
    "embeddings.npy"
)


OUTPUT_METADATA = (
    OUTPUT_DIR /
    "metadata.json"
)



# =====================================
# NVIDIA CONFIG
# =====================================


MODEL_NAME = (
    "nvidia/nv-embedqa-e5-v5"
)



client = OpenAI(

    base_url=
    "https://integrate.api.nvidia.com/v1",

    api_key=NVIDIA_API_KEY

)



# =====================================
# TEXT LIMIT
# =====================================

def truncate_text(
        text,
        max_chars=1500
):
    """
    NVIDIA nv-embedqa-e5-v5
    Maximum: 512 tokens

    1500 caractères ≈ 400-500 tokens
    """

    if len(text) > max_chars:

        return text[:max_chars]

    return text



# =====================================
# MAIN
# =====================================


def main():


    OUTPUT_DIR.mkdir(
        exist_ok=True,
        parents=True
    )



    # -----------------------------
    # LOAD CHUNKS
    # -----------------------------


    print(
        "Loading chunks..."
    )


    with open(

        INPUT_FILE,

        "r",

        encoding="utf-8"

    ) as f:

        chunks = json.load(f)



    print(
        f"Chunks loaded: {len(chunks)}"
    )



    texts = []

    metadata = []



    # -----------------------------
    # PREPARE TEXTS
    # -----------------------------


    for index, chunk in enumerate(chunks):


        text = chunk.get(
            "text",
            ""
        )


        if not text.strip():

            continue



        # Protection NVIDIA

        text = truncate_text(
            text
        )



        texts.append(
            text
        )



        metadata.append(

            {

                "index": index,


                "chunk_id":
                chunk.get(
                    "chunk_id"
                ),


                "metadata":
                chunk.get(
                    "metadata",
                    {}
                )

            }

        )



    print(
        f"Texts ready: {len(texts)}"
    )



    # -----------------------------
    # GENERATE EMBEDDINGS
    # -----------------------------


    embeddings = []


    batch_size = 32



    print(
        "Generating NVIDIA embeddings..."
    )



    for i in tqdm(

        range(
            0,
            len(texts),
            batch_size
        )

    ):


        batch = texts[
            i:i + batch_size
        ]



        try:


            response = client.embeddings.create(

                model=MODEL_NAME,


                input=batch,


                extra_body={

                    "input_type":
                    "passage"

                }

            )



            batch_embeddings = [

                item.embedding

                for item in response.data

            ]



            embeddings.extend(

                batch_embeddings

            )



        except Exception as e:


            print(
                "\nEmbedding error:",
                e
            )


            print(
                "Skipping batch:",
                i
            )



    # -----------------------------
    # CHECK RESULTS
    # -----------------------------


    embeddings = np.asarray(

        embeddings,

        dtype="float32"

    )



    print(

        "Embedding shape:",

        embeddings.shape

    )



    if len(embeddings) == 0:

        raise Exception(
            "No embeddings generated"
        )



    # -----------------------------
    # SAVE EMBEDDINGS
    # -----------------------------


    np.save(

        OUTPUT_EMBEDDINGS,

        embeddings

    )



    print(
        "Embeddings saved:"
    )

    print(
        OUTPUT_EMBEDDINGS
    )



    # -----------------------------
    # SAVE METADATA
    # -----------------------------


    # garder uniquement les metadata
    # correspondant aux embeddings créés


    metadata = metadata[
        :len(embeddings)
    ]



    with open(

        OUTPUT_METADATA,

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            metadata,

            f,

            ensure_ascii=False,

            indent=2

        )



    print(
        "Metadata saved:"
    )

    print(
        OUTPUT_METADATA
    )



    print(
        "\nDONE ✅"
    )




if __name__ == "__main__":

    main()
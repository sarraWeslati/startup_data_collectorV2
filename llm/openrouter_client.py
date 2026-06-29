# llm/openrouter_client.py

import os
from dotenv import load_dotenv
from openai import OpenAI
import time

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY introuvable dans le fichier .env"
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


DEFAULT_MODEL = (
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
)
DEFAULT_TEMPERATURE = 0.1

DEFAULT_MAX_TOKENS = 2000

DEFAULT_TIMEOUT = 120

MAX_RETRIES = 3

RETRY_DELAY = 2

HTTP_REFERER = "https://github.com/sarraWeslati/startup_data_collectorV2.git"

APP_TITLE = "Startup Data Collection"

def call_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """
    Envoie un prompt à OpenRouter avec
    plusieurs tentatives automatiques.
    """

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            response = client.chat.completions.create(

                model=model,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=temperature,

                max_tokens=max_tokens,

                timeout=DEFAULT_TIMEOUT,

                extra_headers={

                    "HTTP-Referer":
                    HTTP_REFERER,

                    "X-Title":
                    APP_TITLE
                }

            )

            if (
                not response.choices
                or
                not response.choices[0].message.content
            ):

                raise ValueError(
                    "Empty response from model."
                )

            return (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

        except Exception as e:

            print(
                f"[OPENROUTER ERROR] Attempt "
                f"{attempt}/{MAX_RETRIES}: {e}"
            )

            if attempt < MAX_RETRIES:

                time.sleep(
                    RETRY_DELAY
                )

    return ""

def call_llm_json(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """
    Appelle le LLM en demandant
    explicitement une réponse JSON.
    """

    prompt = (
        "You must answer ONLY with valid JSON.\n\n"
        + prompt
    )

    return call_llm(
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature
    )
# llm/openrouter_client.py

import os
from dotenv import load_dotenv
from openai import OpenAI

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
    "openai/gpt-oss-120b:free"
)


def call_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 2000,
    temperature: float = 0.1,
) -> str:
    """
    Envoie un prompt à OpenRouter
    et retourne la réponse texte.
    """

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
            f"[OPENROUTER ERROR] {e}"
        )

        return ""
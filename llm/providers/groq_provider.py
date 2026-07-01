import os
import time
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class GroqProvider:

    NAME = "Groq"

    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(self):

        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not api_key:

            raise RuntimeError(
                "GROQ_API_KEY not found."
            )

        self.client = OpenAI(

            api_key=api_key,

            base_url="https://api.groq.com/openai/v1"

        )

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 3500,
        temperature: float = 0.0,
        retries: int = 3
    ) -> Optional[str]:

        if model is None:

            model = self.DEFAULT_MODEL

        for attempt in range(retries):

            try:

                response = self.client.chat.completions.create(

                    model=model,

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    max_tokens=max_tokens,

                    temperature=temperature

                )

                return response.choices[0].message.content

            except Exception as e:

                print(
                    f"[GROQ ERROR] Attempt {attempt + 1}/{retries}: {e}"
                )

                # On remonte les erreurs critiques au routeur
                if (
                    "429" in str(e)
                    or "Rate limit" in str(e)
                ):
                    raise

                time.sleep(2)

        return None
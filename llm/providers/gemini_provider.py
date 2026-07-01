import os
import time
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class GeminiProvider:

    NAME = "Gemini"

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:

            raise RuntimeError(
                "GEMINI_API_KEY not found."
            )

        self.client = OpenAI(

            api_key=api_key,

            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"

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
                    f"[GEMINI ERROR] Attempt {attempt + 1}/{retries}: {e}"
                )

                # On laisse le routeur gérer les erreurs importantes
                if (
                    "429" in str(e)
                    or "Rate limit" in str(e)
                ):
                    raise

                time.sleep(2)

        return None
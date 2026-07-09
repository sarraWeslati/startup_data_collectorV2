import os
import time
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class NvidiaProvider:

    NAME = "NVIDIA"

    DEFAULT_MODEL = (
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
    )

    def __init__(self):

        api_key = os.getenv(
            "NVIDIA_API_KEY"
        )

        if not api_key:

            raise RuntimeError(
                "NVIDIA_API_KEY not found."
            )

        self.client = OpenAI(

            api_key=api_key,

            base_url="https://integrate.api.nvidia.com/v1"

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

                    temperature=temperature,

                    top_p=0.95,

                    max_tokens=max_tokens,

                    extra_body={

                        "chat_template_kwargs": {
                            "enable_thinking": True
                        },

                        "reasoning_budget": 16384

                    },

                    stream=False

                )

                message = response.choices[0].message

                reasoning = getattr(
                    message,
                    "reasoning_content",
                    None
                )

                if reasoning:

                    print(
                        "[NVIDIA REASONING]"
                    )

                    print(reasoning)

                return message.content

            except Exception as e:

                print(
                    f"[NVIDIA ERROR] Attempt {attempt + 1}/{retries}: {e}"
                )

                # On laisse le routeur choisir
                # un autre provider en cas de quota
                if (
                    "429" in str(e)
                    or "Rate limit" in str(e)
                ):
                    raise

                time.sleep(2)

        return None
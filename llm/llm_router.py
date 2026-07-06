# llm/llm_router.py

from typing import Optional

from llm.providers.openrouter_provider import OpenRouterProvider
from llm.providers.groq_provider import GroqProvider
from llm.providers.gemini_provider import GeminiProvider
from llm.providers.nvidia_provider import NvidiaProvider

# =====================================================
# INITIALISATION DES PROVIDERS
# =====================================================

PROVIDERS = []


def register_provider(provider_class):

    try:

        provider = provider_class()

        PROVIDERS.append(provider)

        print(
            f"[LLM] {provider.NAME} initialized."
        )

    except Exception as e:

        print(
            f"[LLM] {provider_class.__name__} disabled : {e}"
        )

register_provider(OpenRouterProvider)

register_provider(NvidiaProvider)

register_provider(GroqProvider)

register_provider(GeminiProvider)


# =====================================================
# APPEL PRINCIPAL
# =====================================================

def call_llm(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 3500,
    temperature: float = 0.0
) -> str:

    if not PROVIDERS:

        raise RuntimeError(
            "No LLM provider available."
        )

    last_exception = None

    for provider in PROVIDERS:

        try:

            print(
                f"\n[LLM] Trying {provider.NAME}..."
            )

            response = provider.generate(

                prompt=prompt,

                model=model,

                max_tokens=max_tokens,

                temperature=temperature

            )

            if response:

                print(
                    f"[LLM] Success with {provider.NAME}"
                )

                return response

        except Exception as e:

            last_exception = e

            print(
                f"[LLM] {provider.NAME} failed."
            )

            print(e)

    raise RuntimeError(

        f"All LLM providers failed.\n\nLast error:\n{last_exception}"

    )


# =====================================================
# JSON
# =====================================================

def call_llm_json(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 3500,
    temperature: float = 0.0
) -> str:

    return call_llm(

        prompt=prompt,

        model=model,

        max_tokens=max_tokens,

        temperature=temperature

    )
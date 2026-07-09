from typing import Dict

from search.providers.tavily_provider import (
    TavilyProvider
)
from search.providers.exa_provider import (
    ExaProvider
)

# Les prochains providers
# from search.providers.exa_provider import ExaProvider
# from search.providers.serper_provider import SerperProvider


# =====================================================
# PROVIDERS
# =====================================================

PROVIDERS = []


def register_provider(
    provider_class
):

    try:

        provider = provider_class()

        PROVIDERS.append(
            provider
        )

        print(
            f"[SEARCH] {provider.NAME} initialized."
        )

    except Exception as e:

        print(

            f"[SEARCH] {provider_class.__name__} disabled : {e}"

        )


# =====================================================
# REGISTER
# =====================================================

register_provider(
    TavilyProvider
)

register_provider(ExaProvider)

# register_provider(SerperProvider)


# =====================================================
# MAIN SEARCH
# =====================================================

def search(

    query: str,

    max_results: int = 10,

    search_depth: str = "advanced",

    topic: str = "general"

) -> Dict:

    if not PROVIDERS:

        raise RuntimeError(

            "No Search provider available."

        )

    last_exception = None

    for provider in PROVIDERS:

        try:

            print(

                f"\n[SEARCH] Trying {provider.NAME}..."

            )

            response = provider.search(

                query=query,

                max_results=max_results,

                search_depth=search_depth,

                topic=topic

            )

            if (response 
                and
                 response.get("results", [])
             ):

                print(

                    f"[SEARCH] Success with {provider.NAME}"

                )

                return response

        except Exception as e:

            last_exception = e

            print(

                f"[SEARCH] {provider.NAME} failed."

            )

            print(e)

    raise RuntimeError(

        f"All Search providers failed.\n\nLast error:\n{last_exception}"

    )
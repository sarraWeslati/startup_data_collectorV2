import os
from typing import Dict, List

from dotenv import load_dotenv
from exa_py import Exa

from search.providers.base_provider import (
    BaseSearchProvider
)

load_dotenv()


class ExaProvider(BaseSearchProvider):

    NAME = "Exa"

    def __init__(self):

        api_key = os.getenv(
            "EXA_API_KEY"
        )

        if not api_key:

            raise RuntimeError(
                "EXA_API_KEY not found."
            )

        self.client = Exa(
            api_key=api_key
        )

    def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced",
        topic: str = "general"
    ) -> Dict:
        """
        Execute a search using Exa AI.

        Returns a Tavily-compatible structure so that
        the rest of the enrichment pipeline does not
        need to know which provider answered.
        """

        try:

            response = self.client.search_and_contents(

                query,

                num_results=max_results,

                text=True

            )

            results: List[Dict] = []

            for item in getattr(
                response,
                "results",
                []
            ):

                results.append(

                    {

                        "title": getattr(
                            item,
                            "title",
                            ""
                        ),

                        "url": getattr(
                            item,
                            "url",
                            ""
                        ),

                        "content": getattr(
                            item,
                            "text",
                            ""
                        ),

                        "raw_content": getattr(
                            item,
                            "text",
                            ""
                        )

                    }

                )

            return {

                "query": query,

                "answer": "",

                "results": results

            }

        except Exception as e:

            print(
                f"[EXA ERROR] {e}"
            )

            raise
import os
from typing import Dict

import requests
from dotenv import load_dotenv

from search.providers.base_provider import (
    BaseSearchProvider
)

load_dotenv()


class TavilyProvider(
    BaseSearchProvider
):

    NAME = "Tavily"

    BASE_URL = (
        "https://api.tavily.com/search"
    )

    def __init__(self):

        self.api_key = os.getenv(
            "TAVILY_API_KEY"
        )

        if not self.api_key:

            raise RuntimeError(
                "TAVILY_API_KEY not found."
            )

    def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced",
        topic: str = "general"
    ) -> Dict:

        payload = {

            "api_key": self.api_key,

            "query": query,

            "topic": topic,

            "search_depth": search_depth,

            "max_results": max_results,

            "include_answer": True,

            "include_raw_content": True,

            "include_images": False

        }

        try:

            response = requests.post(

                self.BASE_URL,

                json=payload,

                timeout=60

            )

            response.raise_for_status()

            data = response.json()

            data.setdefault(
                "results",
                []
            )

            data.setdefault(
                "answer",
                ""
            )

            return data

        except requests.exceptions.HTTPError as e:

            print(
                f"[TAVILY ERROR] {e}"
            )

            if e.response is not None:

                print(
                    e.response.text
                )

            raise

        except Exception as e:

            print(
                f"[TAVILY ERROR] {e}"
            )

            raise
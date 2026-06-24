# enrichment/tavily_client.py

import os
import requests
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY"
)

if not TAVILY_API_KEY:

    raise ValueError(
        "TAVILY_API_KEY introuvable dans le fichier .env"
    )


BASE_URL = "https://api.tavily.com/search"


# =====================================================
# Core Search
# =====================================================

def tavily_search(
    query: str,
    max_results: int = 10,
    search_depth: str = "advanced"
) -> Dict:

    try:

        payload = {

            "api_key":
            TAVILY_API_KEY,

            "query":
            query,

            "search_depth":
            search_depth,

            "max_results":
            max_results,

            "include_answer":
            True,

            "include_raw_content":
            True
        }

        response = requests.post(
            BASE_URL,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        print(
            f"[TAVILY ERROR] {e}"
        )

        return {

            "query":
            query,

            "results":
            [],

            "answer":
            "",

            "error":
            str(e)
        }


# =====================================================
# Startup Search
# =====================================================

def search_startup(
    startup_name: str
) -> Dict:

    query = f"""
    {startup_name}

    startup company

    founders

    linkedin

    website

    funding

    investors

    products

    services

    technologies
    """

    return tavily_search(
        query=query,
        max_results=15
    )


# =====================================================
# Investor Search
# =====================================================

def search_investor(
    investor_name: str
) -> Dict:

    query = f"""
    {investor_name}

    venture capital

    investment fund

    portfolio startups

    investment stages

    investment focus

    partners
    """

    return tavily_search(
        query=query,
        max_results=15
    )


# =====================================================
# URL Extraction
# =====================================================

def extract_urls(
    tavily_result: Dict
) -> List[str]:

    urls = []

    for result in tavily_result.get(
        "results",
        []
    ):

        url = result.get(
            "url",
            ""
        )

        if (
            url
            and url not in urls
        ):

            urls.append(url)

    return urls


# =====================================================
# LinkedIn Extraction
# =====================================================

def extract_linkedin_url(
    tavily_result: Dict
) -> Optional[str]:

    for result in tavily_result.get(
        "results",
        []
    ):

        url = result.get(
            "url",
            ""
        )

        if (
            "linkedin.com"
            in url.lower()
        ):

            return url

    return None


# =====================================================
# Crunchbase Extraction
# =====================================================

def extract_crunchbase_url(
    tavily_result: Dict
) -> Optional[str]:

    for result in tavily_result.get(
        "results",
        []
    ):

        url = result.get(
            "url",
            ""
        )

        if (
            "crunchbase.com"
            in url.lower()
        ):

            return url

    return None


# =====================================================
# Wellfound Extraction
# =====================================================

def extract_wellfound_url(
    tavily_result: Dict
) -> Optional[str]:

    for result in tavily_result.get(
        "results",
        []
    ):

        url = result.get(
            "url",
            ""
        )

        if (
            "wellfound.com"
            in url.lower()
            or
            "angel.co"
            in url.lower()
        ):

            return url

    return None


# =====================================================
# Social Links
# =====================================================

def extract_social_links(
    tavily_result: Dict
) -> Dict:

    socials = {

        "linkedin": "",
        "facebook": "",
        "twitter": "",
        "instagram": "",
        "youtube": ""
    }

    for result in tavily_result.get(
        "results",
        []
    ):

        url = result.get(
            "url",
            ""
        ).lower()

        if (
            "linkedin.com"
            in url
        ):
            socials["linkedin"] = url

        elif (
            "facebook.com"
            in url
        ):
            socials["facebook"] = url

        elif (
            "twitter.com"
            in url
            or
            "x.com"
            in url
        ):
            socials["twitter"] = url

        elif (
            "instagram.com"
            in url
        ):
            socials["instagram"] = url

        elif (
            "youtube.com"
            in url
        ):
            socials["youtube"] = url

    return socials


# =====================================================
# Test
# =====================================================

if __name__ == "__main__":

    result = search_startup(
        "Kumulus"
    )

    print(
        "\nANSWER:\n"
    )

    print(
        result.get(
            "answer",
            ""
        )
    )

    print(
        "\nLINKEDIN:"
    )

    print(
        extract_linkedin_url(
            result
        )
    )

    print(
        "\nCRUNCHBASE:"
    )

    print(
        extract_crunchbase_url(
            result
        )
    )

    print(
        "\nWELLFOUND:"
    )

    print(
        extract_wellfound_url(
            result
        )
    )

    print(
        "\nSOCIALS:"
    )

    print(
        extract_social_links(
            result
        )
    )
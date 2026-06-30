import os
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

from utils.entity_matcher import (is_matching_company)

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError(
        "TAVILY_API_KEY introuvable dans le fichier .env"
    )

BASE_URL = "https://api.tavily.com/search"


# =====================================================
# CORE SEARCH
# =====================================================

def tavily_search(
    query: str,
    max_results: int = 15,
    search_depth: str = "advanced",
    topic: str = "general"
) -> Dict:

    payload = {

        "api_key": TAVILY_API_KEY,

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
            BASE_URL,
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

        print("\n======================")

        print("[TAVILY ERROR]")

        print(e)

        if e.response is not None:

            print(e.response.text)

        print("======================\n")

        return {
            "results": []
        }

    except Exception as e:

        print(e)

        return {
            "results": []
        }

        return {

            "query": query,

            "results": [],

            "answer": "",

            "error": str(e)
        }


# =====================================================
# GENERIC HELPERS
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
        ).strip()

        if url and url not in urls:

            urls.append(url)

    return urls


def find_first_domain(
    tavily_result: Dict,
    domains: List[str]
) -> Optional[str]:

    for result in tavily_result.get(
        "results",
        []
    ):

        url = result.get(
            "url",
            ""
        )

        lower = url.lower()

        for domain in domains:

            if domain in lower:

                return url

    return None


def filter_official_websites(
    tavily_result: Dict
) -> List[str]:

    excluded = {

        "linkedin.com",
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "x.com",
        "youtube.com",
        "github.com",
        "crunchbase.com",
        "wellfound.com",
        "angel.co",
        "pitchbook.com",
        "dealroom.co",
        "startupblink.com",
        "medium.com",
        "wikipedia.org",
        "reddit.com"
    }

    websites = []

    for result in tavily_result.get(
        "results",
        []
    ):

        url = result.get(
            "url",
            ""
        )

        if not url:
            continue

        lower = url.lower()

        if any(
            domain in lower
            for domain in excluded
        ):
            continue

        if url not in websites:

            websites.append(url)

    return websites


def extract_official_website(
    tavily_result: Dict
) -> Optional[str]:

    websites = filter_official_websites(
        tavily_result
    )

    if websites:

        return websites[0]

    return None
# =====================================================
# STARTUP SEARCH
# =====================================================

def search_startup(
    startup_name: str
) -> Dict:

    query = (
    f"{startup_name} startup "
    "official website "
    "LinkedIn "
    "Crunchbase "
    "Wellfound "
    "founders "
    "CEO "
    "headquarters "
    "country "
    "city "
    "industry "
    "products "
    "services "
    "technologies "
    "funding "
    "investors "
    "partners "
    "awards"
)

    return tavily_search(
        query=query,
        max_results=20,
        search_depth="advanced"
    )


# =====================================================
# INVESTOR SEARCH
# =====================================================

def search_investor(
    investor_name: str
) -> Dict:

    query = (
    f"{investor_name} investor "
    "official website "
    "LinkedIn "
    "Crunchbase "
    "PitchBook "
    "Dealroom "
    "investment focus "
    "portfolio "
    "partners "
    "ticket size "
    "assets under management "
    "headquarters "
    "country "
    "city"
)

    return tavily_search(
        query=query,
        max_results=20,
        search_depth="advanced"
    )
# =====================================================
# PLATFORM EXTRACTION
# =====================================================

def extract_linkedin_url(
    tavily_result: Dict
) -> Optional[str]:

    return find_first_domain(
        tavily_result,
        ["linkedin.com"]
    )


def extract_crunchbase_url(
    tavily_result: Dict
) -> Optional[str]:

    return find_first_domain(
        tavily_result,
        ["crunchbase.com"]
    )


def extract_wellfound_url(
    tavily_result: Dict
) -> Optional[str]:

    return find_first_domain(
        tavily_result,
        [
            "wellfound.com",
            "angel.co"
        ]
    )


def extract_github_url(
    tavily_result: Dict
) -> Optional[str]:

    return find_first_domain(
        tavily_result,
        ["github.com"]
    )


def extract_dealroom_url(
    tavily_result: Dict
) -> Optional[str]:

    return find_first_domain(
        tavily_result,
        ["dealroom.co"]
    )


def extract_pitchbook_url(
    tavily_result: Dict
) -> Optional[str]:

    return find_first_domain(
        tavily_result,
        ["pitchbook.com"]
    )


def extract_startupblink_url(
    tavily_result: Dict
) -> Optional[str]:

    return find_first_domain(
        tavily_result,
        ["startupblink.com"]
    )


# =====================================================
# SOCIAL MEDIA
# =====================================================

def extract_social_links(
    tavily_result: Dict
) -> Dict:

    return {

        "linkedin":
        extract_linkedin_url(
            tavily_result
        ) or "",

        "facebook":
        find_first_domain(
            tavily_result,
            ["facebook.com"]
        ) or "",

        "instagram":
        find_first_domain(
            tavily_result,
            ["instagram.com"]
        ) or "",

        "youtube":
        find_first_domain(
            tavily_result,
            ["youtube.com"]
        ) or "",

        "github":
        extract_github_url(
            tavily_result
        ) or ""
    }


# =====================================================
# EXTERNAL PROFILES
# =====================================================

def extract_external_profiles(
    tavily_result: Dict
) -> Dict:

    return {

        "website":
        extract_official_website(
            tavily_result
        ),

        "linkedin":
        extract_linkedin_url(
            tavily_result
        ),

        "crunchbase":
        extract_crunchbase_url(
            tavily_result
        ),

        "wellfound":
        extract_wellfound_url(
            tavily_result
        ),

        "github":
        extract_github_url(
            tavily_result
        ),

        "dealroom":
        extract_dealroom_url(
            tavily_result
        ),

        "pitchbook":
        extract_pitchbook_url(
            tavily_result
        ),

        "startupblink":
        extract_startupblink_url(
            tavily_result
        )
    }
# =====================================================
# ENRICHMENT PACKAGE
# =====================================================

def build_enrichment_package(
    company_name: str,
    tavily_result: Dict
) -> Dict:
    """
    Construit un package complet d'informations
    à partir de la réponse Tavily.
    """

    filtered_results = []

    for result in tavily_result.get(
        "results",
        []
    ):

        url = result.get(
            "url",
            ""
        )

        if is_matching_company(
            company_name,
            url
        ):

            filtered_results.append(
                result
            )
    filtered_tavily = {
        **tavily_result,
        "results": filtered_results
    }

    return {

        "website":
        extract_official_website(
            filtered_tavily
        ),

        "linkedin":
        extract_linkedin_url(
            filtered_tavily
        ),

        "crunchbase":
        extract_crunchbase_url(
            filtered_tavily
        ),

        "wellfound":
        extract_wellfound_url(
            filtered_tavily
        ),

        "github":
        extract_github_url(
            filtered_tavily
        ),

        "dealroom":
        extract_dealroom_url(
            filtered_tavily
        ),

        "pitchbook":
        extract_pitchbook_url(
            filtered_tavily
        ),

        "startupblink":
        extract_startupblink_url(
            filtered_tavily
        ),

        "social_media":
        extract_social_links(
            filtered_tavily
        ),

        "urls":
        extract_urls(
            filtered_tavily
        ),

        "answer":
        filtered_tavily.get(
            "answer",
            ""
        ),

        "results":
        filtered_tavily.get(
            "results",
            []
        ),

        "results_count":
        len(
            filtered_tavily.get(
                "results",
                []
            )
        )
    }


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    company_name = "Kumulus"

    tavily_result = search_startup(
        company_name
    )

    package = build_enrichment_package(
        company_name,
        tavily_result
    )

    print("\n==============================")
    print("OFFICIAL WEBSITE")
    print("==============================")
    print(package["website"])

    print("\n==============================")
    print("LINKEDIN")
    print("==============================")
    print(package["linkedin"])

    print("\n==============================")
    print("CRUNCHBASE")
    print("==============================")
    print(package["crunchbase"])

    print("\n==============================")
    print("WELLFOUND")
    print("==============================")
    print(package["wellfound"])

    print("\n==============================")
    print("DEALROOM")
    print("==============================")
    print(package["dealroom"])

    print("\n==============================")
    print("PITCHBOOK")
    print("==============================")
    print(package["pitchbook"])

    print("\n==============================")
    print("STARTUPBLINK")
    print("==============================")
    print(package["startupblink"])

    print("\n==============================")
    print("SOCIAL MEDIA")
    print("==============================")
    print(package["social_media"])

    print("\n==============================")
    print("RESULTS")
    print("==============================")
    print(package["results_count"])
    
import os
from typing import Dict, List, Optional

import re
from dotenv import load_dotenv
from utils.website_resolver import (resolve_official_website)
from utils.entity_matcher import (is_matching_company)
from search.search_client import (search_web)

#load_dotenv()

#TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

#if not TAVILY_API_KEY:
    #raise ValueError(
        #"TAVILY_API_KEY introuvable dans le fichier .env"
    #)

#BASE_URL = "https://api.tavily.com/search"


# =====================================================
# CORE SEARCH
# =====================================================

def tavily_search(
    query: str,
    max_results: int = 15,
    search_depth: str = "advanced",
    topic: str = "general"
) -> Dict:
    """
    Wrapper autour du Search Router.

    Le moteur de recherche (Tavily, Exa, Serper...)
    est choisi automatiquement par le Search Router.
    """

    return search_web(

        query=query,

        max_results=max_results,

        search_depth=search_depth,

        topic=topic

    )

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
    """
    Sélectionne le meilleur site officiel parmi
    les résultats Tavily.
    """

    websites = filter_official_websites(
        tavily_result
    )

    if not websites:
        return None

    return resolve_official_website(
        *websites
    )

def normalize_company_name(
    name: str
) -> str:
    """
    Normalise un nom d'entreprise
    pour faciliter les comparaisons.
    """

    if not name:
        return ""

    name = name.lower()

    # Supprime toute ponctuation
    name = re.sub(
        r"[^a-z0-9]",
        "",
        name
    )

    return name

# =====================================================
# STARTUP SEARCH
# =====================================================

def search_startup(
    startup_name: str
) -> Dict:

    return search_company(
        startup_name
    )


def search_official_website(
    company_name: str
) -> Dict:
    """
    Recherche uniquement le site officiel.
    """

    query = (
        f'"{company_name}" official website'
    )

    return tavily_search(
        query=query,
        max_results=5,
        search_depth="advanced"
    )


def search_linkedin(
    company_name: str
) -> Dict:
    """
    Recherche uniquement LinkedIn.
    """

    query = (
        f'"{company_name}" LinkedIn'
    )

    return tavily_search(
        query=query,
        max_results=5,
        search_depth="advanced"
    )


def search_crunchbase(
    company_name: str
) -> Dict:
    """
    Recherche Crunchbase.
    """

    query = (
        f'"{company_name}" Crunchbase'
    )

    return tavily_search(
        query=query,
        max_results=5,
        search_depth="advanced"
    )


def search_wellfound(
    company_name: str
) -> Dict:
    """
    Recherche Wellfound.
    """

    query = (
        f'"{company_name}" Wellfound'
    )

    return tavily_search(
        query=query,
        max_results=5,
        search_depth="advanced"
    )

def search_dealroom(
    company_name: str
) -> Dict:
    """
    Recherche Dealroom.
    """

    query = (
        f'"{company_name}" Dealroom'
    )

    return tavily_search(
        query=query,
        max_results=5,
        search_depth="advanced"
    )



def search_startup_investors(
    startup_name: str
):
    """
    Recherche les investisseurs d'une startup via Tavily.
    """

    query = (
        f'"{startup_name}" investors '
        f'funding OR seed OR series A OR venture capital'
    )

    return tavily_search(
        query=query,
        max_results=10
    )


# =====================================================
# INVESTOR SEARCH
# =====================================================

def search_investor(
    investor_name: str
) -> Dict:

    return search_company(
        investor_name
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



def is_relevant_result(
    company_name: str,
    result: Dict
) -> bool:
    """
    Vérifie si un résultat Tavily parle réellement
    de l'entreprise recherchée.
    """

    company = company_name.lower().strip()

    title = result.get(
        "title",
        ""
    ).lower()

    content = result.get(
        "content",
        ""
    ).lower()

    raw = result.get(
        "raw_content",
        ""
    ).lower()

    url = result.get(
        "url",
        ""
    ).lower()

    # Nettoyage du nom
    words = [
        w
        for w in re.split(r"[\s\-_]+", company)
        if len(w) > 2
    ]

    score = 0

    for word in words:

        if word in title:
            score += 4

        if word in content:
            score += 2

        if word in raw:
            score += 1

        if word in url:
            score += 3

    # Le nom complet apparaît
    if company in title:
        score += 8

    if company in content:
        score += 5

    if company in url:
        score += 6

    return score >= 8

def merge_tavily_results(
    *responses: Dict
) -> Dict:
    """
    Fusionne plusieurs réponses Tavily.
    """

    merged = {

        "results": [],

        "answer": ""
    }

    seen = set()

    answers = []

    for response in responses:

        if not response:
            continue

        answer = response.get(
            "answer",
            ""
        )

        if answer:

            answers.append(
                answer
            )

        for result in response.get(
            "results",
            []
        ):

            url = result.get(
                "url",
                ""
            )

            if not url:

                continue

            if url in seen:

                continue

            seen.add(url)

            merged["results"].append(
                result
            )

    merged["answer"] = "\n".join(
        answers
    )

    return merged

def search_company(
    company_name: str
) -> Dict:
    """
    Effectue plusieurs recherches spécialisées
    puis fusionne les résultats.
    """

    website = search_official_website(
        company_name
    )

    linkedin = search_linkedin(
        company_name
    )

    crunchbase = search_crunchbase(
        company_name
    )

    wellfound = search_wellfound(
        company_name
    )

    dealroom = search_dealroom(
        company_name
    )

    return merge_tavily_results(

        website,

        linkedin,

        crunchbase,

        wellfound,

        dealroom

    )

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

        matching = is_matching_company(
            company_name,
            url
        )

        relevant = is_relevant_result(
            company_name,
            result
        )

        if matching or relevant:

            filtered_results.append(result)

            print(f"[KEEP] {url}")
        else:

            print(f"[SKIP] {url}")


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
    
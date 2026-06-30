import os
import requests
from typing import Dict, Optional

from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY manquante dans .env")


BASE_URL = "https://api.tavily.com/search"


# =====================================
# CORE SEARCH
# =====================================

def tavily_search(query: str, max_results: int = 10) -> Dict:

    try:

        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results,
            "include_answer": True,
            "include_raw_content": False
        }

        r = requests.post(BASE_URL, json=payload, timeout=60)
        r.raise_for_status()

        return r.json()

    except Exception as e:

        print("[TAVILY ERROR]", e)

        return {
            "query": query,
            "results": [],
            "answer": ""
        }


# =====================================
# STARTUP SEARCH
# =====================================

def search_startup(name: str) -> Dict:

    query = f"""
Find information about the startup: {name}

Return:
- website
- linkedin
- founders
- industry
- headquarters
- funding
- products
"""

    return tavily_search(query, max_results=15)


# =====================================
# INVESTOR SEARCH
# =====================================

def search_investor(name: str) -> Dict:

    query = f"""
Find information about the investor: {name}

Return:
- website
- linkedin
- investment focus
- portfolio companies
- funds
- partners
"""

    return tavily_search(query, max_results=15)


# =====================================
# EXTRACTORS
# =====================================

def extract_company_website(data: Dict) -> Optional[str]:

    blacklist = [
        "linkedin.com",
        "crunchbase.com",
        "twitter.com",
        "facebook.com",
        "instagram.com",
        "youtube.com"
    ]

    for r in data.get("results", []):

        url = r.get("url", "")

        if not url:
            continue

        if any(b in url for b in blacklist):
            continue

        return url

    return None


def extract_linkedin_url(data: Dict) -> Optional[str]:

    for r in data.get("results", []):

        url = r.get("url", "")

        if "linkedin.com" in url:
            return url

    return None


def extract_social_links(data: Dict) -> Dict:

    socials = {
        "linkedin": "",
        "twitter": "",
        "facebook": "",
        "instagram": ""
    }

    for r in data.get("results", []):

        url = r.get("url", "")

        if "linkedin.com" in url:
            socials["linkedin"] = url

        elif "twitter.com" in url or "x.com" in url:
            socials["twitter"] = url

        elif "facebook.com" in url:
            socials["facebook"] = url

        elif "instagram.com" in url:
            socials["instagram"] = url

    return socials
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
BASE_URL = "https://google.serper.dev/search"

_last_call = 0
MIN_DELAY = 1.5


def serper_search(query: str, max_results: int = 5, retry: int = 2):

    global _last_call

    if not query:
        return {"organic": []}

    query = query.strip()[:200]

    for _ in range(retry + 1):

        try:
            now = time.time()

            if now - _last_call < MIN_DELAY:
                time.sleep(MIN_DELAY)

            _last_call = time.time()

            r = requests.post(
                BASE_URL,
                headers={
                    "X-API-KEY": SERPER_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "q": query,
                    "num": max_results
                },
                timeout=20
            )

            if r.status_code == 429:
                time.sleep(3)
                continue

            if r.status_code == 400:
                print("[SERPER BAD QUERY]", query)
                return {"organic": []}

            r.raise_for_status()
            return r.json()

        except Exception as e:
            print("[SERPER ERROR]", e)
            time.sleep(2)

    return {"organic": []}


# =========================
# WEBSITE EXTRACTOR
# =========================
def extract_company_website(data: dict):

    blacklist = [
        "linkedin.com",
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "youtube.com",
        "crunchbase.com",
        "wikipedia.org"
    ]

    for r in data.get("organic", []):
        url = r.get("link", "")
        if url and not any(b in url for b in blacklist):
            return url

    return None


# =========================
# LINKEDIN COMPANY ONLY
# =========================
def extract_linkedin_url(data: dict):

    for r in data.get("organic", []):
        url = r.get("link", "")
        if "linkedin.com/company" in url:
            return url

    return None


# =========================
# SOCIAL LINKS
# =========================
def extract_social_links(data: dict):

    socials = {
        "linkedin": "",
        "twitter": "",
        "facebook": "",
        "instagram": "",
        "youtube": ""
    }

    for r in data.get("organic", []):

        url = r.get("link", "")

        if "linkedin.com/company" in url:
            socials["linkedin"] = url
        elif "twitter.com" in url or "x.com" in url:
            socials["twitter"] = url
        elif "facebook.com" in url:
            socials["facebook"] = url
        elif "instagram.com" in url:
            socials["instagram"] = url
        elif "youtube.com" in url:
            socials["youtube"] = url

    return socials
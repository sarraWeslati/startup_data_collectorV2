import re
from llm import llm_extract


INVALID_NAMES = {
    "balance", "dans", "avec", "une", "le", "la",
    "entrepreneurs", "startup", "program", "report"
}

def normalize_funding(funding_list):
    normalized = []

    for f in funding_list:
        try:
            amount = float(f.get("amount", 0))

            normalized.append({
                "amount": amount,
                "currency": f.get("currency", "USD"),
                "type": f.get("type", "unknown"),
                "meaning": f.get("meaning", "")
            })

        except:
            continue

    return normalized

def safe_llm_output(llm_data):
    if isinstance(llm_data, list):
        return llm_data[0] if llm_data else None
    return llm_data

def clean_startup_name(name):
    if not name:
        return None
    if name.lower() in INVALID_NAMES:
        return None
    if len(name) < 3:
        return None
    return name

def extract_year(text):
    years = re.findall(r"20\d{2}", text)
    return years[0] if years else None


def extract_startup_name(title):
    words = title.split()
    blacklist = {"Après", "C’est", "Dans", "Avec", "Une", "Le", "La", "Les"}

    for w in words:
        if w not in blacklist and len(w) > 2:
            return w
    return None


def extract_money(text):
    matches = re.findall(r"(\d+(?:\.\d+)?)\s?(million|milliard|M|K)?\s?(USD|EUR|TND)?", text, re.I)

    results = []
    for amount, scale, currency in matches:
        results.append({
            "amount": amount,
            "scale": scale,
            "currency": currency
        })

    return results


def extract_structured_data(url, title, text):

    if not text:
        return None

    basic = {
        "url": url,
        "startup_name": extract_startup_name(title),
        "year": extract_year(text),
        "funding": extract_money(text),
        "content": text[:1500]
    }

    llm_data = llm_extract(url, title, text)

    if isinstance(llm_data, dict):
        return {
            "url": url,
            "startup_name": llm_data.get("startup_name") or basic["startup_name"],
            "year": llm_data.get("year") or basic["year"],
            "funding": normalize_funding(llm_data.get("funding", [])),            "entities": llm_data.get("entities", []),
            "summary": llm_data.get("summary"),
            "content": text[:1500]
        }
    if not isinstance(llm_data, dict):
     llm_data = {}

    return basic
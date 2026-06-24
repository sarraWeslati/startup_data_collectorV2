import re
from llm import llm_extract


# =========================
# BASIC REGEX FALLBACK
# =========================

def extract_money(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\s?millions?\s?dollars?",
        r"(\d+(?:\.\d+)?)\s?milliards?\s?dollars?",
        r"(\d+(?:\.\d+)?)\s?M\$",
        r"(\d+(?:\.\d+)?)\s?million"
    ]

    results = []
    for p in patterns:
        results.extend(re.findall(p, text, re.IGNORECASE))

    return results


def extract_year(text):
    match = re.findall(r"20\d{2}", text)
    return match[0] if match else None


def extract_startup_name(title):
    words = title.split()

    if not words:
        return None

    bad = {"Après", "C’est", "Leur", "Dans", "Avec", "Une", "Le", "La", "Les"}

    for w in words:
        if w not in bad and len(w) > 2:
            return w

    return None


def clean_entities(text):
    words = re.findall(r"\b[A-Z][a-zA-Z]{3,}\b", text)

    blacklist = {
        "Tunisie", "France", "Europe", "Afrique", "Moyen", "Orient"
    }

    return list(set([w for w in words if w not in blacklist]))


# =========================
# MAIN FUNCTION (HYBRID)
# =========================

def extract_structured_data(url, title, text):

    if not text:
        return None

    # fallback local
    basic = {
        "url": url,
        "startup_name": extract_startup_name(title),
        "year": extract_year(text),
        "funding_mentions": extract_money(text),
        "entities": clean_entities(text),
        "content": text[:1500]
    }

    # LLM enrichment
    llm_data = llm_extract(url, title, text)

    if llm_data:
        return {
            "url": url,
            "startup_name": llm_data.get("startup_name") or basic["startup_name"],
            "year": llm_data.get("year") or basic["year"],
            "funding": llm_data.get("funding", []),
            "entities": llm_data.get("entities", []),
            "summary": llm_data.get("summary"),
            "content": text[:1500]
        }

    return basic
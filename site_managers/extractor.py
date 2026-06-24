import re


# =========================
# 💰 MONEY EXTRACTION
# =========================
def extract_money(text):
    patterns = [
        r"(\d+(?:[.,]\d+)?\s?(?:million|millions|milliard|milliards))\s?(?:dollars|euros|€|\$)?",
        r"(\d+(?:[.,]\d+)?\s?[M|MDT|MUSD|€|\$]+)"
    ]

    results = []

    for p in patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        results.extend(matches)

    return list(set(results))


# =========================
# 📅 YEAR EXTRACTION
# =========================
def extract_year(text):
    match = re.search(r"20\d{2}", text)
    return match.group(0) if match else None


# =========================
# 🏢 COMPANY EXTRACTION (FIX IMPORTANT)
# =========================
def extract_startup_name(title, text):

    # 1. priorité titre nettoyé
    title_words = title.split()

    if title_words:
        first = title_words[0]

        # filtre stopwords
        if first.lower() not in ["le", "la", "les", "un", "une", "dans"]:
            return first

    # 2. fallback : capitalized words
    candidates = re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", text)

    stop = {"Le", "La", "Les", "Dans", "Selon", "Pour"}

    filtered = [c for c in candidates if c not in stop]

    return filtered[0] if filtered else None


# =========================
# 🔢 NUMBERS EXTRACTION
# =========================
def extract_numbers(text):
    return re.findall(r"\+?\d[\d\s,.]*", text)


# =========================
# 🧹 ENTITIES CLEANING
# =========================
def clean_proper_entities(text):

    stop_words = {
        "Elle", "Pour", "Dans", "Selon", "Les", "Des", "Une",
        "Afrique", "Europe", "Tunisie", "France", "Chaque"
    }

    words = re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", text)

    cleaned = []

    for w in words:
        if w not in stop_words and len(w) > 2:
            cleaned.append(w)

    return list(set(cleaned))


# =========================
# 🧾 FINAL STRUCTURE
# =========================
def extract_structured_data(url, title, text):

    if not text:
        return None

    return {
        "url": url,
        "startup_name": extract_startup_name(title, text),
        "year": extract_year(text),
        "funding_mentions": extract_money(text),
        "entities": clean_proper_entities(text),
        "numbers": extract_numbers(text),
        "content": text[:2000]  # limite propre
    }
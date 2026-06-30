import re
import requests
import trafilatura


EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

PHONE_REGEX = r"\+?\d[\d\s().-]{7,}\d"


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text)


def extract_emails(text: str):
    if not text:
        return []
    return list(set(re.findall(EMAIL_REGEX, text)))


def extract_phones(text: str):
    if not text:
        return []

    phones = re.findall(PHONE_REGEX, text)

    cleaned = []
    for p in phones:
        p = p.strip()

        # 🔥 remove broken patterns like "135-103"
        if len(p) < 10:
            continue

        if any(c.isalpha() for c in p):
            continue

        cleaned.append(p)

    return list(set(cleaned))


def enrich_from_website(entity: dict):

    url = entity.get("website")
    if not url:
        return entity

    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        text = trafilatura.extract(r.text)

        if not text:
            return entity

        text = clean_text(text)

        entity["website_content"] = text[:12000]

        # ✅ FIXED EXTRACTION
        entity["emails"] = extract_emails(text)
        entity["phones"] = extract_phones(text)

    except Exception as e:
        print("[WEBSITE ERROR]", e)

    return entity
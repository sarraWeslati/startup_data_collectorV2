from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any

import fitz
import config

from models import StartupBase, Contact, Socials, FundingRound

SOURCE_NAME = "tunisie_pdf"

# =========================
# REGEX (AMÉLIORÉ)
# =========================

NAME_YEAR_RE = re.compile(r"^(.+?)\s*\(((?:19|20)\d{2})\)$")
SECTOR_RE = re.compile(r"Secteur d.?activit[eé]\s*/\s*Sector\s*:\s*(.+)", re.IGNORECASE)

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-]{7,}\d)")
URL_RE = re.compile(r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")


# =========================
# CLEANING
# =========================

def clean(text: str | None) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def clean_inline(text: str | None) -> str:
    return re.sub(r"\s+", " ", clean(text)).strip(" -")


# =========================
# EXTRACTION GLOBALE (TOUT)
# =========================

def extract_all(text: str) -> Dict[str, Any]:
    text = clean(text)

    emails = list(set(EMAIL_RE.findall(text)))
    phones = list(set(PHONE_RE.findall(text)))
    urls = list(set(URL_RE.findall(text)))

    return {
        "emails": emails,
        "phones": phones,
        "urls": urls
    }


# =========================
# NAME + YEAR
# =========================

def parse_name_year(text: str):
    line = clean_inline(text.splitlines()[0])
    match = NAME_YEAR_RE.match(line)
    if match:
        return clean_inline(match.group(1)), match.group(2)
    return line, None


# =========================
# SECTOR
# =========================

def extract_sector(text: str) -> str:
    for line in clean(text).splitlines():
        m = SECTOR_RE.search(line)
        if m:
            return clean_inline(m.group(1))
    return ""


# =========================
# WEBSITE
# =========================

def extract_website(urls: list[str]) -> str:
    for u in urls:
        if any(x in u for x in ["http", "www."]):
            return u
    return ""


# =========================
# CONTACT EXTRACTION (ROBUSTE)
# =========================

def extract_contact(text: str):
    lines = [clean_inline(l) for l in text.splitlines() if clean_inline(l)]

    email = ""
    idx = -1

    for i, l in enumerate(lines):
        m = EMAIL_RE.search(l)
        if m:
            email = m.group(0)
            idx = i
            break

    if idx == -1:
        return [], "", ""

    founders = [l for l in lines[:idx] if "fondateur" not in l.lower()]
    address = " ".join(lines[idx + 1:]).strip()

    return founders, email, address


# =========================
# PAGE BLOCKS
# =========================

def page_blocks(page):
    blocks = []
    for x0, y0, x1, y1, text, *_ in page.get_text("blocks"):
        t = clean(text)
        if t:
            blocks.append({"x0": x0, "y0": y0, "text": t})
    return blocks


def is_name_line(text: str) -> bool:
    if not text:
        return False
    line = clean_inline(text.splitlines()[0])
    return bool(NAME_YEAR_RE.match(line)) and len(line) < 120


# =========================
# BUILD STARTUP (🔥 AMÉLIORÉ)
# =========================

def build_startup(row_text: str, name_block: str) -> StartupBase:

    name, year = parse_name_year(name_block)
    sector = extract_sector(row_text)

    extracted = extract_all(row_text)
    website = extract_website(extracted["urls"])

    founders, email, address = extract_contact(row_text)

    # 🔥 IMPORTANT : garder TOUT dans description + extra raw-like
    full_description = row_text.strip()

    return StartupBase(
        nom=name,
        secteur=sector or None,
        description=full_description,

        site_web=website or None,
        ville=None,
        pays="Tunisia",

        source=SOURCE_NAME,
        source_url="pdf",

        contact=Contact(
            email=email or None,
            phone=extracted["phones"][0] if extracted["phones"] else None,
            address=address or None
        ),

        socials=Socials(
            website=website or None
        ),

        funding=FundingRound()
    )


# =========================
# PAGE EXTRACTION
# =========================

def extract_page_startups(page):
    blocks = page_blocks(page)

    name_blocks = [b for b in blocks if is_name_line(b["text"])]
    name_blocks = sorted(name_blocks, key=lambda b: b["y0"])

    startups = []

    for i, nb in enumerate(name_blocks):
        start = nb["y0"]
        end = name_blocks[i + 1]["y0"] if i + 1 < len(name_blocks) else 1e9

        row = [b["text"] for b in blocks if start <= b["y0"] < end]
        row_text = "\n".join(row)

        try:
            startups.append(build_startup(row_text, nb["text"]))
        except Exception as e:
            print("[PDF ERROR]", e)
            continue

    return startups

def to_startup_schema(data):
    extra = data.get("extra", {})

    website = data.get("site_web")

    if not website and extra.get("urls"):
        website = extra["urls"][0]

    return {
        "entity_type": "startup",

        "name": data.get("nom"),
        "description": data.get("description"),
        "tagline": None,

        "industry": data.get("secteur"),
        "keywords": [],

        "country": data.get("pays"),
        "city": data.get("ville"),
        "headquarters": None,

        "founded_year": None,
        "startup_stage": None,
        "startup_label": True,

        "website": website,
        "linkedin_url": None,

        "social_media": {
            "linkedin": None,
            "facebook": None,
            "instagram": None,
            "youtube": None,
            "github": None
        },

        "contact": {
            "emails": extra.get("emails", []),
            "phones": extra.get("phones", []),
            "address": None
        },

        "founders": [],
        "leadership": [],

        "employee_count": None,
        "employee_range": None,
        "team_size": None,

        "products": [],
        "services": [],
        "technologies": [],

        "customer_segments": [],
        "target_market": None,

        "operating_countries": [],
        "languages_supported": [],

        "notable_customers": [],
        "partners": [],

        "accelerators": [],
        "incubators": [],

        "funding": {
            "total_raised": None,
            "currency": None,
            "stage": None,
            "rounds": []
        },

        "investors": [],

        "awards": [],
        "certifications": [],
        "patents": [],

        "business_metrics": {
            "users_count": None,
            "customers_count": None,
            "downloads": None,
            "monthly_transactions": None,
            "annual_revenue": None,
            "revenue_currency": None
        },

        "recent_news": [],
        "events": [],

        "legal_info": {
            "company_type": None,
            "registration_number": None
        },

        "extra_notes": None,

        "sources": [
            {
                "type": "pdf",
                "url": data.get("source_url", "pdf"),
                "confidence": 1.0
            }
        ],

        "confidence": {
            "overall": 0.7,
            "description": 1.0,
            "founders": 0.0,
            "leadership": 0.0,
            "employees": 0.0,
            "funding": 0.0,
            "investors": 0.0,
            "products": 0.0,
            "technologies": 0.0
        },

        "enrichment": {
            "status": "pdf_extracted",
            "sources_used": ["pdf"],
            "collection_date": "",
            "last_updated": ""
        },

        "stats": {
            "has_website": bool(website),
            "has_linkedin": False,
            "founders_count": 0,
            "leadership_count": 0,
            "investors_count": 0,
            "products_count": 0,
            "services_count": 0,
            "technologies_count": 0,
            "news_count": 0
        }
    }


# =========================
# MAIN ENTRY (🔥 FINAL FIX)
# =========================

def run_pdf_llm_extraction() -> List[Dict]:

    pdf_path = Path(config.PDF_FILE)
    startups: List[StartupBase] = []

    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            startups.extend(extract_page_startups(page))

    print(f"[PDF] extracted startups: {len(startups)}")

    # 🔥 IMPORTANT: dict + nettoyage + fallback safe
    result = []

    for s in startups:
        try:
            data = s.model_dump()

            # 🔥 enrich raw info propre
            data["extra"] = {
                "raw_text": data.get("description"),
                "emails": re.findall(EMAIL_RE, data.get("description", "")),
                "phones": re.findall(PHONE_RE, data.get("description", "")),
                "urls": re.findall(URL_RE, data.get("description", "")),
            }

            result.append(to_startup_schema(data))

        except Exception as e:
            print("[MODEL ERROR]", e)

    return result

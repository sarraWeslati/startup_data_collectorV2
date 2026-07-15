"""
Script 2 : Nettoyage & normalisation des données
==================================================
Prend en entrée merged_news.json (sortie du script 1) et produit clean_news.json.

Ce script :
    - nettoie les textes (HTML, entités, espaces, caractères parasites)
    - normalise les dates vers un format ISO unique (YYYY-MM-DD)
    - normalise les pays (alias -> nom canonique, listes multi-pays, régions)
    - normalise les secteurs/tags (vocabulaire unifié)
    - supprime les articles vides ou inexploitables
    - conserve toutes les métadonnées importantes (entités, montants, sources...)

Usage :
    python 02_clean_data.py
"""

import json
import re
import html
import unicodedata
from pathlib import Path
from datetime import datetime
from dateutil import parser as date_parser

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
INPUT_DIR = Path(__file__).parent
INPUT_FILE = INPUT_DIR / "merged_news.json"
OUTPUT_FILE = INPUT_DIR / "clean_news.json"

MIN_CONTENT_LENGTH = 30  # en dessous de ce nombre de caractères, l'article est jugé vide/inexploitable


# ------------------------------------------------------------------
# 1. Nettoyage de texte
# ------------------------------------------------------------------
HTML_TAG_RE = re.compile(r"<[^>]+>")
MULTI_SPACE_RE = re.compile(r"[ \t]+")
MULTI_NEWLINE_RE = re.compile(r"\n{2,}")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Caractères typographiques à uniformiser (guillemets, tirets, espaces insécables...)
CHAR_REPLACEMENTS = {
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u00a0": " ", "\u200b": "",
    "\ufeff": "",
}


def clean_text(text: str) -> str:
    """Nettoie une chaîne de texte : HTML, entités, caractères parasites, espaces."""
    if not text:
        return ""

    text = html.unescape(text)          # &amp; -> &, &#39; -> ', etc.
    text = HTML_TAG_RE.sub(" ", text)   # supprime les balises HTML résiduelles

    for old, new in CHAR_REPLACEMENTS.items():
        text = text.replace(old, new)

    text = CONTROL_CHARS_RE.sub("", text)
    text = unicodedata.normalize("NFKC", text)  # normalise la représentation unicode

    text = MULTI_SPACE_RE.sub(" ", text)
    text = MULTI_NEWLINE_RE.sub("\n", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = text.strip()

    return text


def clean_list(items: list[str]) -> list[str]:
    """Nettoie une liste de chaînes (tags, montants, noms d'entités...) et supprime les vides/doublons."""
    if not items:
        return []
    cleaned = []
    seen = set()
    for it in items:
        c = clean_text(str(it))
        key = c.lower()
        if c and key not in seen:
            cleaned.append(c)
            seen.add(key)
    return cleaned


# ------------------------------------------------------------------
# 2. Normalisation des dates
# ------------------------------------------------------------------
MONTHS_FR = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5,
    "juin": 6, "juillet": 7, "août": 8, "aout": 8, "septembre": 9,
    "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12,
}

NON_DATE_VALUES = {"", "not specified", "unknown", "n/a", "na", "-", "tbd"}


def _try_fr_date(raw: str) -> datetime | None:
    """Essaie de parser une date en français, ex: '26 juin 2026'."""
    m = re.match(r"^(\d{1,2})\s+([a-zéû]+)\s+(\d{4})$", raw.strip().lower())
    if m:
        day, month_name, year = m.groups()
        month = MONTHS_FR.get(month_name)
        if month:
            try:
                return datetime(int(year), month, int(day))
            except ValueError:
                return None
    return None


def normalize_date(raw: str) -> dict:
    """
    Normalise une date brute (formats très hétérogènes) vers un format ISO.

    Retourne un dict :
        {
          "date": "YYYY-MM-DD" | None,   # date normalisée (jour arbitraire=01 si inconnu)
          "date_precision": "day" | "month" | "year" | "unknown"
        }
    """
    if not raw or raw.strip().lower() in NON_DATE_VALUES:
        return {"date": None, "date_precision": "unknown"}

    raw = raw.strip()

    # Cas "2025-03-xx" -> mois connu, jour inconnu
    m = re.match(r"^(\d{4})-(\d{2})-xx$", raw, re.IGNORECASE)
    if m:
        year, month = m.groups()
        return {"date": f"{year}-{month}-01", "date_precision": "month"}

    # Cas année seule "2025"
    if re.match(r"^\d{4}$", raw):
        return {"date": f"{raw}-01-01", "date_precision": "year"}

    # Cas "YYYY-MM"
    if re.match(r"^\d{4}-\d{2}$", raw):
        return {"date": f"{raw}-01", "date_precision": "month"}

    # Cas plage de dates "February 11-12, 2026" -> on garde la première date
    m = re.match(r"^([A-Za-zéû]+)\s+(\d{1,2})[-–]\d{1,2},?\s+(\d{4})$", raw)
    if m:
        month_name, day, year = m.groups()
        raw = f"{month_name} {day}, {year}"

    # Cas français "26 juin 2026"
    fr_date = _try_fr_date(raw)
    if fr_date:
        return {"date": fr_date.strftime("%Y-%m-%d"), "date_precision": "day"}

    # Cas générique (YYYY-MM-DD, "June 17, 2026", "11 July 2022", "May 2026"...)
    try:
        parsed = date_parser.parse(raw, default=datetime(1900, 1, 1), dayfirst=False)
        # Détecte si le jour a été deviné par défaut (absent de la chaîne d'origine)
        precision = "day"
        if not re.search(r"\b\d{1,2}\b", raw.replace(str(parsed.year), "")):
            precision = "month"
        return {"date": parsed.strftime("%Y-%m-%d"), "date_precision": precision}
    except (ValueError, OverflowError):
        return {"date": None, "date_precision": "unknown"}


# ------------------------------------------------------------------
# 3. Normalisation des pays / régions
# ------------------------------------------------------------------
REGION_TERMS = {"africa", "mena", "north africa", "north america"}

COUNTRY_ALIASES = {
    "ksa": "Saudi Arabia",
    "saudi arabia": "Saudi Arabia",
    "uae": "United Arab Emirates",
    "dubai": "United Arab Emirates",
    "tunisia": "Tunisia",
    "morocco": "Morocco",
    "algeria": "Algeria",
    "libya": "Libya",
    "egypt": "Egypt",
    "nigeria": "Nigeria",
    "kenya": "Kenya",
    "jordan": "Jordan",
    "lebanon": "Lebanon",
    "palestine": "Palestine",
    "turkey": "Turkey",
    "oman": "Oman",
    "malaysia": "Malaysia",
    "india": "India",
    "kazakhstan": "Kazakhstan",
    "togo": "Togo",
    "benin": "Benin",
    "madagascar": "Madagascar",
    "côte d'ivoire": "Côte d'Ivoire",
    "côte d’ivoire": "Côte d'Ivoire",
    "cote d'ivoire": "Côte d'Ivoire",
    "francophone africa": None,  # zone, pas un pays -> ignoré comme pays
}

UNKNOWN_VALUES = {"", "unknown", "n/a", "na", "-"}


def normalize_country(raw: str) -> dict:
    """
    Normalise un champ pays brut, potentiellement multi-valeurs ou contenant une région.

    Retourne :
        {
          "countries": [str, ...],  # liste de pays canoniques (peut être vide)
          "region": str | None      # région si détectée (Africa, MENA...)
        }
    """
    if not raw or raw.strip().lower() in UNKNOWN_VALUES:
        return {"countries": [], "region": None}

    raw_clean = raw.strip()

    # Cas région pure ("Africa", "MENA"...)
    if raw_clean.lower() in REGION_TERMS:
        return {"countries": [], "region": raw_clean}

    # Extrait une éventuelle liste entre parenthèses : "Multiple (Nigeria, Egypt, Kenya, Francophone Africa)"
    region = None
    paren_match = re.search(r"\(([^)]+)\)", raw_clean)
    if paren_match:
        raw_clean = paren_match.group(1)

    # Sépare sur virgules et " and "
    tokens = re.split(r",|\band\b", raw_clean)

    countries = []
    seen = set()
    for tok in tokens:
        tok_clean = tok.strip()
        if not tok_clean:
            continue
        key = tok_clean.lower()

        if key in REGION_TERMS:
            region = tok_clean
            continue

        canonical = COUNTRY_ALIASES.get(key, None)
        if canonical is None and key not in COUNTRY_ALIASES:
            # Pas dans les alias connus : on garde la valeur telle quelle (Title Case)
            canonical = tok_clean
        if canonical and canonical.lower() not in seen:
            countries.append(canonical)
            seen.add(canonical.lower())

    return {"countries": countries, "region": region}


# ------------------------------------------------------------------
# 4. Normalisation des secteurs (tags) et catégories
# ------------------------------------------------------------------
SECTOR_ALIASES = {
    "ai": "AI", "artificial intelligence": "AI",
    "fintech": "Fintech", "financial technology": "Fintech",
    "e-commerce": "E-commerce", "ecommerce": "E-commerce",
    "cleantech": "CleanTech", "climate tech": "CleanTech", "climatetech": "CleanTech",
    "healthtech": "HealthTech", "health tech": "HealthTech",
    "edtech": "EdTech", "education technology": "EdTech",
    "agritech": "AgriTech", "agtech": "AgriTech",
    "logistics": "Logistics",
    "banking": "Banking",
    "insurtech": "InsurTech",
    "proptech": "PropTech",
    "mobility": "Mobility",
    "energy": "Energy",
}

CATEGORY_ALIASES = {
    "funding": "funding",
    "investment": "funding",
    "acquisition": "acquisition",
    "startup": "startup",
    "news": "news",
    "report": "report",
    "banking": "banking",
    "event": "event",
    "other": "other",
}


def normalize_sector(tag: str) -> str:
    """Normalise un tag/secteur individuel vers un vocabulaire unifié."""
    key = tag.strip().lower()
    return SECTOR_ALIASES.get(key, tag.strip().title())


def normalize_category(cat: str) -> str:
    """Normalise le type d'article (catégorie) vers un vocabulaire unifié."""
    if not cat:
        return "other"
    key = cat.strip().lower()
    return CATEGORY_ALIASES.get(key, key)


# ------------------------------------------------------------------
# 5. Pipeline de nettoyage d'un article
# ------------------------------------------------------------------
def clean_article(article: dict) -> dict | None:
    """
    Nettoie et normalise un article complet.
    Retourne None si l'article doit être supprimé (contenu inexploitable).
    """
    title = clean_text(article.get("title", ""))
    summary = clean_text(article.get("summary", ""))
    content = clean_text(article.get("content", ""))

    # Texte de référence pour juger si l'article est exploitable : le plus long des trois
    best_text_len = max(len(content), len(summary), len(title))
    if best_text_len < MIN_CONTENT_LENGTH:
        return None  # article vide ou inexploitable -> supprimé

    date_info = normalize_date(article.get("date", ""))
    country_info = normalize_country(article.get("country", ""))

    entities = article.get("entities") or {}
    tags = article.get("tags") or []

    return {
        "id": article.get("id"),
        "title": title,
        "summary": summary,
        # Si le contenu détaillé est absent, on retombe sur le résumé pour ne pas perdre d'information
        "content": content or summary,
        "date": date_info["date"],
        "date_precision": date_info["date_precision"],
        "countries": country_info["countries"],
        "region": country_info["region"] or clean_text(article.get("region", "")) or None,
        "category": normalize_category(article.get("category", "")),
        "sectors": [normalize_sector(t) for t in clean_list(tags)],
        "amounts": clean_list(article.get("amounts") or []),
        "relevance": clean_text(article.get("relevance", "")) or None,
        "entities": {
            "startups": clean_list(entities.get("startups") or []),
            "investors": clean_list(entities.get("investors") or []),
            "funds": clean_list(entities.get("funds") or []),
        },
        "funding": article.get("funding") or {},
        "source_url": article.get("source_url", ""),
        "origin_file": article.get("origin_file", ""),
    }


# ------------------------------------------------------------------
# Point d'entrée
# ------------------------------------------------------------------
def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        articles = json.load(f)

    print(f"Articles chargés depuis {INPUT_FILE.name} : {len(articles)}")

    cleaned = []
    removed = 0
    for art in articles:
        result = clean_article(art)
        if result is None:
            removed += 1
            continue
        cleaned.append(result)

    print(f"Articles supprimés (vides/inexploitables) : {removed}")
    print(f"Articles conservés après nettoyage         : {len(cleaned)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"\nFichier nettoyé sauvegardé : {OUTPUT_FILE}")

    # Petit résumé statistique pour vérification rapide
    with_date = sum(1 for a in cleaned if a["date"])
    with_country = sum(1 for a in cleaned if a["countries"])
    with_region = sum(1 for a in cleaned if a["region"])
    print(f"\n--- Statistiques ---")
    print(f"Articles avec date normalisée   : {with_date}/{len(cleaned)}")
    print(f"Articles avec pays identifié(s) : {with_country}/{len(cleaned)}")
    print(f"Articles avec région identifiée : {with_region}/{len(cleaned)}")


if __name__ == "__main__":
    main()
import re
from copy import deepcopy

from schemas import INVESTOR_TEMPLATE, STARTUP_TEMPLATE


STARTUP_KEYWORDS = (
    "startup",
    "start-up",
    "jeune pousse",
    "leve",
    "levee",
    "serie a",
    "serie b",
    "serie c",
    "seed",
    "pre-seed",
    "amorçage",
    "amorcage",
    "fondee",
    "fonde",
)

INVESTOR_KEYWORDS = (
    "investisseur",
    "investisseurs",
    "fonds",
    "venture capital",
    "capital-risque",
    "vc",
    "business angel",
    "incubateur",
    "accelerateur",
    "accélérateur",
    "appel a candidatures",
    "appel à candidatures",
    "programme d'investissement",
)

INVESTMENT_KEYWORDS = (
    "investissement",
    "investissements",
    "financement",
    "financements",
    "levee de fonds",
    "levée de fonds",
    "tour de table",
    "million",
    "millions",
    "milliard",
    "milliards",
)

INDUSTRY_KEYWORDS = {
    "AI": ("ia", "intelligence artificielle", "artificial intelligence", "llm"),
    "FinTech": ("fintech", "paiement", "banque", "banking"),
    "ClimateTech": ("climat", "climatique", "recyclage", "environnement"),
    "AgriTech": ("agri", "agriculture", "irrigation", "agronom"),
    "HealthTech": ("sante", "santé", "health", "medical", "médical"),
    "EdTech": ("education", "éducation", "formation", "edtech"),
    "E-commerce": ("e-commerce", "commerce", "retail"),
    "DeepTech": ("deeptech", "deep tech"),
    "IoT": ("iot", "objets connectes", "objets connectés"),
}

COUNTRY_KEYWORDS = {
    "Tunisia": ("tunisie", "tunisien", "tunisienne", "tunis"),
    "Egypt": ("egypte", "égypte", "egyptien", "egyptienne"),
    "France": ("france", "français", "francaise", "française"),
    "Morocco": ("maroc", "marocain", "marocaine"),
    "Algeria": ("algerie", "algérie", "algerien", "algérien"),
    "Senegal": ("senegal", "sénégal"),
    "Ivory Coast": ("cote d'ivoire", "côte d'ivoire", "ivoire"),
    "United Kingdom": ("britannique", "royaume-uni", "uk"),
}

STOP_NAMES = {
    "La",
    "Le",
    "Les",
    "Une",
    "Un",
    "Des",
    "Startup",
    "Startups",
    "Afrique",
    "Tunisie",
    "France",
    "Mena",
    "Africaines",
    "Africains",
    "Entrepreneurs",
    "Innovations",
}

STARTUP_SLUG_STOPWORDS = {
    "la",
    "le",
    "les",
    "une",
    "un",
    "des",
    "startup",
    "startups",
    "tunisienne",
    "tunisien",
    "tunisie",
    "africaine",
    "africaines",
    "africains",
    "francaise",
    "franco",
    "francaises",
    "turque",
    "britannique",
    "egyptienne",
    "nigeriane",
    "sud",
    "scale",
    "up",
    "mena",
    "afrique",
    "millions",
    "milliards",
    "dollars",
    "euros",
    "leve",
    "leves",
    "lever",
    "levee",
    "mobilises",
    "ont",
    "service",
    "immersion",
    "immersive",
    "experience",
    "action",
    "challenge",
    "et",
    "en",
    "qui",
    "quand",
    "developpee",
    "developpe",
    "geant",
    "americain",
    "paiements",
    "visa",
    "societe",
    "capital",
    "risque",
    "senegal",
    "ifc",
    "investit",
}

INVESTOR_SLUG_MARKERS = (
    "capital",
    "ventures",
    "venture",
    "fund",
    "fonds",
    "jif",
    "facility",
    "incubator",
    "accelerator",
    "y-combinator",
    "qualcomm",
    "ifc",
    "a15",
    "coreangels",
    "loftyinc",
    "tarcoola",
    "go-big",
)


def normalize_text(value: str) -> str:
    return " ".join((value or "").split())


def strip_accents_for_matching(value: str) -> str:
    replacements = {
        "à": "a",
        "â": "a",
        "ä": "a",
        "ç": "c",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ÿ": "y",
    }
    lowered = value.lower()
    for accented, plain in replacements.items():
        lowered = lowered.replace(accented, plain)
    return lowered


def summarize(text: str, max_chars: int = 420) -> str:
    text = normalize_text(text)
    if len(text) <= max_chars:
        return text

    cut = text[:max_chars].rsplit(" ", 1)[0]
    return f"{cut}..."


def find_keywords(text: str, keyword_map: dict) -> list:
    normalized = strip_accents_for_matching(text)
    found = []

    for label, keywords in keyword_map.items():
        if any(strip_accents_for_matching(keyword) in normalized for keyword in keywords):
            found.append(label)

    return found


def find_country(text: str) -> str:
    matches = find_keywords(text, COUNTRY_KEYWORDS)
    return matches[0] if matches else ""


def find_amounts(text: str) -> list:
    amount_pattern = re.compile(
        r"(?i)(?:jusqu['’]a\s+)?\d[\d\s.,]*\s*(?:millions?|milliards?|k|m)?\s*(?:dollars?|euros?|\$|€)"
    )
    return [normalize_text(match.group(0)) for match in amount_pattern.finditer(text)]


def clean_name(name: str) -> str:
    name = normalize_text(name)
    name = re.sub(r"^[Ll]a startup\s+", "", name)
    name = re.sub(r"^[Ll]e startup\s+", "", name)
    name = re.sub(r"^[Uu]ne startup\s+", "", name)
    name = re.sub(r"^[Uu]n startup\s+", "", name)
    name = name.strip(" ,:;.-")

    if name in STOP_NAMES or len(name) < 2:
        return ""

    return name[:90]


def title_from_url(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    slug = re.sub(r"^\d+-", "", slug)
    return slug.replace("-", " ")


def clean_slug_name(value: str) -> str:
    words = [word for word in re.split(r"[-\s]+", value) if word]
    kept = []

    for word in words:
        normalized = strip_accents_for_matching(word)
        if normalized in STARTUP_SLUG_STOPWORDS:
            continue
        if normalized.isdigit() or re.fullmatch(r"\d+[.,]?\d*", normalized):
            continue
        kept.append(word)

    if not kept:
        return ""

    return clean_name(" ".join(word[:1].upper() + word[1:] for word in kept[:3]))


def clean_investor_slug_name(value: str) -> str:
    words = [word for word in re.split(r"[-\s]+", value) if word]
    if not words:
        return ""

    return clean_name(
        " ".join(
            word.upper() if word.isdigit() or len(word) <= 3 else word[:1].upper() + word[1:]
            for word in words[:4]
        )
    )


def extract_name_from_url(url: str, entity_type: str) -> str:
    slug = url.rstrip("/").split("/")[-1].lower()

    if entity_type == "investor":
        investor_patterns = [
            r"^(\d+-capital)",
            r"^([a-z0-9]+-ventures)",
            r"^(coreangels)-",
            r"^(edventures)-",
            r"^(f6-group)-",
            r"capital-risque-([a-z0-9]+)-",
            r"fonds-africain-([a-z0-9-]+)",
            r"(go-big-partners)",
            r"(216-capital-ventures)",
            r"(qualcomm)",
            r"(y-combinator)",
            r"(ifc)-investit",
        ]

        for pattern in investor_patterns:
            match = re.search(pattern, slug)
            if match:
                return clean_investor_slug_name(match.group(1))

        if "y-combinator" in slug:
            return "Y Combinator"

        if "qualcomm" in slug:
            return "Qualcomm"

        return ""

    startup_patterns = [
        r"^(basata)-startup",
        r"scale-up-francaise-([a-z0-9-]+?)-leve",
        r"startup-(?:tunisienne|tunisien|francaise|franco-tunisienne|egyptienne|nigeriane|africaine|britannique)-([a-z0-9-]+?)(?:-leve|-quand|-qui|-renforce)",
        r"la-startup-(?:tunisienne|tunisien|francaise|franco-tunisienne|egyptienne|nigeriane|africaine|britannique)-([a-z0-9-]+?)(?:-leve|-quand|-qui|-renforce)",
        r"cette-startup-(?:tunisienne|egyptienne|nigeriane|africaine)-([a-z0-9-]+?)-",
        r"developpee-en-tunisie-([a-z0-9-]+?)-",
        r"en-tunisie-([a-z0-9-]+?)-certifiee",
        r"en-tunisie-([a-z0-9-]+?)-permet",
        r"sassocie-a-la-startup-[a-z-]+-([a-z0-9-]+)",
        r"dans-la-startup-([a-z0-9-]+)",
        r"^([a-z0-9-]+?)-leve-",
        r"^([a-z0-9-]+?)-accelere-",
        r"^([a-z0-9-]+?)-la-startup",
        r"^([a-z0-9-]+?)-sacree-startup",
        r"^([a-z0-9-]+?)-veut-",
        r"^([a-z0-9-]+?)-quand-",
        r"^([a-z0-9-]+?)-recompensee-",
        r"^([a-z0-9-]+?)-primee-",
        r"^([a-z0-9-]+?)-certifiee-",
        r"^([a-z0-9-]+?)-permet-",
        r"^([a-z0-9-]+?)-lidentite-",
        r"^([a-z0-9-]+?)-creer-",
        r"^([a-z0-9-]+?)-la-plateforme",
        r"^(cynoia)-et-",
        r"^(konnect-networks)-parmi-",
        r"^(pixii-motors)-parmi-",
        r"^(world-labs)-la-startup",
        r"^(basata)-startup",
    ]

    for pattern in startup_patterns:
        match = re.search(pattern, slug)
        if match:
            name = clean_slug_name(match.group(1))
            if name:
                return name

    return ""


def extract_name_from_title(title: str, entity_type: str) -> str:
    title = normalize_text(title)
    patterns = []

    if entity_type == "startup":
        patterns = [
            r"\b(?:[Ll]a|[Ll]e|[Uu]ne|[Uu]n)\s+startup\s+(?:tunisienne|tunisien|egyptienne|égyptienne|britannique|francaise|française|africaine|africain)?\s*([A-Z][\w’'&.-]+(?:\s+[A-Z][\w’'&.-]+){0,3})",
            r"\b([A-Z][A-Za-z0-9’'&.-]+(?:\s+[A-Z][A-Za-z0-9’'&.-]+){0,3})\s+(?:leve|lève|vient de lever|boucle|annonce)",
            r"\b([A-Z][A-Za-z0-9’'&.-]+(?:\s+[A-Z][A-Za-z0-9’'&.-]+){0,3})\s*,?\s+(?:[Ll]a|[Ll]e)\s+startup",
        ]
    elif entity_type == "investor":
        patterns = [
            r"\b(?:le fonds|la fondation|l'investisseur|l’accelerateur|l’accélérateur|l'incubateur|l’incubateur)\s+([A-Z][\w’'&.-]+(?:\s+[A-Z][\w’'&.-]+){0,4})",
            r"\b([A-Z][A-Za-z0-9’'&.-]+(?:\s+[A-Z][A-Za-z0-9’'&.-]+){0,4})\s+(?:investit|lance un fonds|prolonge son appel)",
        ]

    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            return clean_name(match.group(1))

    return ""


def has_investor_marker(name: str) -> bool:
    haystack = strip_accents_for_matching(name)
    return any(marker in haystack for marker in INVESTOR_SLUG_MARKERS)


def extract_known_investor_name(url: str, title: str, text: str) -> str:
    from_url = extract_name_from_url(url, "investor")
    if from_url:
        return from_url

    slug = title_from_url(url)
    combined = f"{slug} {title}"
    known_patterns = [
        (r"\by[-\s]?combinator\b", "Y Combinator"),
        (r"\b216\s+capital(?:\s+ventures)?\b", "216 Capital"),
        (r"\bgo\s+big\s+partners\b", "Go Big Partners"),
        (r"\bloftyinc\b", "LoftyInc"),
        (r"\bcoreangels\b", "CoreAngels"),
        (r"\btarcoola\b", "Tarcoola"),
        (r"\bqualcomm\b", "Qualcomm"),
    ]

    normalized = strip_accents_for_matching(combined)
    for pattern, name in known_patterns:
        if re.search(pattern, normalized):
            return name

    return ""


def extract_startup_name(url: str, title: str) -> str:
    return extract_name_from_url(url, "startup")


def classify_article(url: str, title: str, text: str) -> str:
    normalized = strip_accents_for_matching(f"{title} {text}")

    investor_name = extract_known_investor_name(url, title, text)
    if investor_name and (has_investor_marker(investor_name) or "investit dans la startup" in normalized):
        return "investor"

    startup_name = extract_startup_name(url, title)
    if startup_name:
        return "startup"

    return "other"


def build_source(url: str, title: str, text: str) -> dict:
    return {
        "url": url,
        "title": title,
        "content": text,
    }


def build_startup(url: str, title: str, text: str) -> dict:
    data = deepcopy(STARTUP_TEMPLATE)
    amounts = find_amounts(text)
    industries = find_keywords(text, INDUSTRY_KEYWORDS)

    data.update(
        {
            "name": extract_startup_name(url, title),
            "description": summarize(text),
            "industry": industries[0] if industries else "",
            "keywords": industries,
            "country": find_country(text),
            "funding": {"amounts": amounts} if amounts else {},
            "sources": [url],
            "confidence": {"classification": "rules"},
            "source_article": build_source(url, title, text),
        }
    )
    return data


def build_investor(url: str, title: str, text: str) -> dict:
    data = deepcopy(INVESTOR_TEMPLATE)
    amounts = find_amounts(text)
    focus = find_keywords(text, INDUSTRY_KEYWORDS)

    data.update(
        {
            "name": extract_known_investor_name(url, title, text),
            "description": summarize(text),
            "country": find_country(text),
            "investment_focus": {"sectors": focus} if focus else {},
            "recent_investments": [{"amounts": amounts, "source": url}] if amounts else [],
            "sources": [url],
            "confidence": {"classification": "rules"},
            "source_article": build_source(url, title, text),
        }
    )
    return data


def build_other(url: str, title: str, text: str) -> dict:
    tags = find_keywords(text, INDUSTRY_KEYWORDS)
    amounts = find_amounts(text)

    return {
        "entity_type": "other",
        "title": title,
        "summary": summarize(text),
        "tags": tags,
        "relevance": "high" if amounts or tags else "medium",
        "amounts": amounts,
        "source_article": build_source(url, title, text),
        "others": {},
    }


def extract_structured_data(url, title, text):
    if not text:
        return None

    title = normalize_text(title)
    text = normalize_text(text)
    entity_type = classify_article(url, title, text)

    if entity_type == "startup":
        return build_startup(url, title, text)

    if entity_type == "investor":
        return build_investor(url, title, text)

    return build_other(url, title, text)

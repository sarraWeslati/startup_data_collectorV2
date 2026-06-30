from enrichment.tavily_client import tavily_search
import re
from difflib import SequenceMatcher

INVESTOR_QUERIES = [

    "{name} investors",

    "{name} funding",

    "{name} funding round",

    "{name} raised",

    "{name} investment",

    "{name} venture capital",

    "{name} seed",

    "{name} series A",

    "{name} backed by",

    '"{name}" investors'
]

INVESTOR_KEYWORDS = [

    "investor",
    "investors",
    "investment",
    "funding",
    "fundraising",
    "venture capital",
    "vc",
    "seed",
    "pre-seed",
    "series a",
    "series b",
    "series c",
    "raised",
    "backed by",
    "financing",
    "financed",
    "capital"
]


TRUSTED_DOMAINS = [

    "crunchbase",
    "wellfound",
    "dealroom",
    "pitchbook",
    "techcrunch",
    "forbes",
    "ventureburn",
    "disruptafrica",
    "startupblink",
    "magnitt",
    "linkedin"
]

FUNDING_PATTERNS = [

    r"backed by ([^.]+)",
    r"funded by ([^.]+)",
    r"invested by ([^.]+)",
    r"investment from ([^.]+)",
    r"raised .*? from ([^.]+)",
    r"raised .*? led by ([^.]+)",
    r"led by ([^.]+)",
    r"participation from ([^.]+)"
]


def search_startup_investors(
    startup_name: str
):

    all_results = []

    answers = []

    searched_queries = []

    for query in INVESTOR_QUERIES:

        query = query.format(
            name=startup_name
        )

        searched_queries.append(query)

        try:

            result = tavily_search(query)

            if not result:
                continue

            if result.get("answer"):

                answers.append(
                    result["answer"]
                )

            all_results.extend(

                result.get(
                    "results",
                    []
                )

            )

        except Exception as e:

            print(
                f"[INVESTOR SEARCH] {e}"
            )

    all_results = deduplicate_results(
        all_results
    )

    all_results = filter_investor_results(
        all_results
    )

    possible_investors = extract_possible_investors(
        all_results
    )

    funding_mentions = extract_funding_mentions(
        all_results
    )

    return {

        "queries": searched_queries,

        "answers": answers,

        "possible_investors": possible_investors,

        "funding_mentions": funding_mentions,

        "results": all_results

    }

def normalize_name(name: str) -> str:
    """
    Normalise un nom pour comparer les entreprises.
    """

    if not name:
        return ""

    name = name.lower()

    name = re.sub(r"[^a-z0-9 ]", " ", name)

    name = re.sub(r"\s+", " ", name)

    return name.strip()
def similarity(a: str, b: str) -> float:
    """
    Retourne un score de similarité entre 0 et 1.
    """

    return SequenceMatcher(
        None,
        normalize_name(a),
        normalize_name(b)
    ).ratio()

def deduplicate_results(results: list) -> list:
    """
    Supprime les résultats très similaires.
    Conserve celui ayant le meilleur score Tavily.
    """

    unique = []

    for result in results:

        title = result.get("title", "")

        if not title:
            continue

        duplicated = False

        for existing in unique:

            score = similarity(
                title,
                existing.get("title", "")
            )

            if score >= 0.90:

                duplicated = True

                if result.get("score", 0) > existing.get("score", 0):

                    existing.update(result)

                break

        if not duplicated:

            unique.append(result)

    return unique
def filter_investor_results(results: list) -> list:
    """
    Conserve uniquement les résultats susceptibles
    de contenir des informations d'investissement.
    """

    filtered = []

    for result in results:

        score = result.get("score", 0)

        if score < 0.60:
            continue

        text = " ".join([

            result.get("title", ""),

            result.get("content", ""),

            result.get("url", "")

        ]).lower()

        # Domaine fiable
        if any(domain in text for domain in TRUSTED_DOMAINS):

            filtered.append(result)

            continue

        # Mots-clés d'investissement
        if any(keyword in text for keyword in INVESTOR_KEYWORDS):

            filtered.append(result)

    return filtered

def extract_possible_investors(results: list) -> list:
    """
    Extrait automatiquement les noms des investisseurs
    présents dans les résultats Tavily.
    """

    investors = set()

    for result in results:

        text = " ".join([

            result.get("title", ""),

            result.get("content", "")

        ])

        for pattern in FUNDING_PATTERNS:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for match in matches:

                # Séparation par "and", ","...
                parts = re.split(
                    r",| and | & |;",
                    match
                )

                for investor in parts:

                    investor = investor.strip()

                    if len(investor) > 2:

                        investors.add(investor)

    return sorted(investors)

def extract_funding_mentions(results: list) -> list:
    """
    Garde uniquement les passages parlant de financement.
    """

    mentions = []

    keywords = [

        "raised",
        "funding",
        "investor",
        "investment",
        "backed",
        "seed",
        "series",
        "venture capital"
    ]

    for result in results:

        content = result.get(
            "content",
            ""
        )

        if any(

            keyword in content.lower()

            for keyword in keywords

        ):

            mentions.append(content[:600])

    return mentions


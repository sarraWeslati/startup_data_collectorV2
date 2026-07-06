from copy import deepcopy
from typing import Any, Dict, List
import json
import re


# =====================================================
# EMPTY VALUES
# =====================================================

EMPTY_VALUES = {
    None,
    "",
    " ",
    "None",
    "none",
    "NULL",
    "null",
    "Null",
    "N/A",
    "n/a",
    "-",
    "--",
    "undefined",
    "Undefined",
    "unknown",
    "Unknown"
}


# =====================================================
# FIELDS THAT CAN BE UPDATED
# =====================================================

REPLACEABLE_FIELDS = {

    "website",
    "linkedin",
    "linkedin_url",

    "country",
    "city",
    "headquarters",

    "description",
    "tagline",

    "logo",

    "company_size",
    "employee_count",
    "employee_range",

    "startup_stage",
    "organization_type",

    "founded_year"
}


# =====================================================
# OBJECT LIST FIELDS
# =====================================================

OBJECT_LIST_FIELDS = {

    "founders",
    "investors",
    "partners",
    "team_members",
    "leadership",
    "advisors",
    "portfolio_startups",
    "board_members"

}

# =====================================================
# SOURCE PRIORITY
# =====================================================

SOURCE_PRIORITY = {

    "manual": 100,

    "website": 90,

    "linkedin": 85,

    "github": 80,

    "crunchbase": 78,

    "pitchbook": 75,

    "dealroom": 74,

    "wellfound": 73,

    "tavily": 70,

    "llm": 60,

    "extraction": 50

}

# =====================================================
# VALUE QUALITY
# =====================================================

def compute_quality(
    value: Any
) -> int:
    """
    Calcule un score de qualité
    d'une valeur.
    """

    if is_empty(value):

        return 0

    if isinstance(value, str):

        value = value.strip()

        score = len(value)

        if value.startswith("https://"):

            score += 100

        elif value.startswith("http://"):

            score += 50

        if "linkedin.com" in value:

            score += 120

        if "@" in value:

            score += 60

        return score

    if isinstance(value, list):

        return len(value) * 10

    if isinstance(value, dict):

        return len(value) * 10

    return 10


# =====================================================
# EMPTY CHECK
# =====================================================

def is_empty(
    value: Any
) -> bool:
    """
    Retourne True si la valeur est considérée vide.
    Compatible avec les dictionnaires et les listes.
    """

    # None
    if value is None:
        return True

    # Chaînes
    if isinstance(value, str):

        value = value.strip()

        return value in EMPTY_VALUES

    # Listes
    if isinstance(value, list):

        return len(value) == 0

    # Dictionnaires
    if isinstance(value, dict):

        return len(value) == 0

    return False


# =====================================================
# STRING NORMALIZATION
# =====================================================

def normalize_string(
    value: str
) -> str:
    """
    Normalise une chaîne pour les comparaisons.
    """

    if not isinstance(value, str):

        return ""

    value = value.lower().strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


# =====================================================
# SIMPLE VALUE MERGING
# =====================================================

def merge_simple_value(
    old_value,
    new_value,
    field_name=""
):
    """
    Fusion intelligente
    d'une valeur simple.
    """

    if is_empty(new_value):

        return deepcopy(old_value)

    if is_empty(old_value):

        return deepcopy(new_value)

    # Toujours garder True

    if isinstance(old_value, bool):

        return old_value or new_value

    # Nombres

    if isinstance(old_value, (int, float)):

        if old_value == 0:

            return deepcopy(new_value)

        return old_value

    # Chaînes

    if (
        isinstance(old_value, str)
        and isinstance(new_value, str)
    ):

        old_score = compute_quality(
            old_value
        )

        new_score = compute_quality(
            new_value
        )

        if new_score > old_score:

            return deepcopy(new_value)

        return deepcopy(old_value)

    return deepcopy(old_value)

# =====================================================
# SIMPLE LIST MERGING
# =====================================================

def merge_lists(
    original: List[Any],
    enriched: List[Any]
) -> List[Any]:
    """
    Fusionne deux listes simples.

    Compatible avec :

    - chaînes
    - nombres
    - booléens

    Les listes de dictionnaires sont gérées
    par merge_named_objects().
    """

    merged = []

    seen = set()

    for item in original + enriched:

        if is_empty(item):

            continue

        if isinstance(item, dict):

            key = json.dumps(
                item,
                sort_keys=True,
                ensure_ascii=False
            )

        elif isinstance(item, list):

            key = json.dumps(
                item,
                sort_keys=True,
                ensure_ascii=False
            )

        else:

            key = normalize_string(
                str(item)
            )

        if key in seen:

            continue

        seen.add(key)

        merged.append(item)

    return merged


# =====================================================
# SMART OBJECT MERGING
# =====================================================

def merge_named_objects(
    original: List[Dict],
    enriched: List[Dict]
) -> List[Dict]:
    """
    Fusion intelligente d'objets possédant un champ 'name'.

    Compatible avec :

    - founders
    - investors
    - partners
    - advisors
    - leadership
    - team_members
    - portfolio_startups
    """

    merged = {}

    # -------------------------
    # Charge les objets existants
    # -------------------------

    for obj in original:

        if not isinstance(obj, dict):
            continue

        name = normalize_string(
            obj.get("name", "")
        )

        if not name:
            continue

        merged[name] = deepcopy(obj)

    # -------------------------
    # Fusion des nouveaux objets
    # -------------------------

    for obj in enriched:

        if not isinstance(obj, dict):
            continue

        name = normalize_string(
            obj.get("name", "")
        )

        if not name:
            continue

        if name not in merged:

            merged[name] = deepcopy(obj)

            continue

        existing = merged[name]

        for field, value in obj.items():

            # -------------------------
            # Nouveau champ
            # -------------------------

            if field not in existing:

                existing[field] = deepcopy(value)

                continue

            old = existing[field]

            # -------------------------
            # Dict
            # -------------------------

            if (
                isinstance(old, dict)
                and isinstance(value, dict)
            ):

                existing[field] = merge_dicts(
                    old,
                    value
                )

                continue

            # -------------------------
            # Liste
            # -------------------------

            if (
                isinstance(old, list)
                and isinstance(value, list)
            ):

                existing[field] = merge_lists(
                    old,
                    value
                )

                continue

            # -------------------------
            # Valeur simple
            # -------------------------

            existing[field] = merge_simple_value(
                old,
                value,
                field
            )

    return list(
        merged.values()
    )

# =====================================================
# DICTIONARY MERGING
# =====================================================

def merge_dicts(
    original: Dict,
    enriched: Dict
) -> Dict:
    """
    Fusion récursive de deux dictionnaires.

    Règles :

    - Ne jamais supprimer une donnée.
    - Ajouter les nouvelles clés.
    - Fusionner récursivement.
    - Fusionner intelligemment les listes.
    """

    merged = deepcopy(original)

    for key, new_value in enriched.items():

        # -----------------------------------
        # Nouvelle clé
        # -----------------------------------

        if key not in merged:

            merged[key] = deepcopy(new_value)

            continue

        old_value = merged[key]

        # -----------------------------------
        # Valeurs simples
        # -----------------------------------

        if (
            not isinstance(old_value, (dict, list))
            and
            not isinstance(new_value, (dict, list))
        ):

            merged[key] = merge_simple_value(
                old_value,
                new_value,
                key
            )

            continue

        # -----------------------------------
        # Dictionnaires
        # -----------------------------------

        if (
            isinstance(old_value, dict)
            and isinstance(new_value, dict)
        ):

            merged[key] = merge_dicts(
                old_value,
                new_value
            )

            continue

        # -----------------------------------
        # Listes
        # -----------------------------------

        if (
            isinstance(old_value, list)
            and isinstance(new_value, list)
        ):

            # -----------------------------------
            # Liste d'objets
            # -----------------------------------

            if (
                key in OBJECT_LIST_FIELDS
                or (
                    old_value
                    and isinstance(
                        old_value[0],
                        dict
                    )
                )
                or (
                    new_value
                    and isinstance(
                        new_value[0],
                        dict
                    )
                )
            ):

                merged[key] = merge_named_objects(
                    old_value,
                    new_value
                )

            else:

                merged[key] = merge_lists(
                    old_value,
                    new_value
                )

            continue

        # -----------------------------------
        # Types incompatibles
        # -----------------------------------

        if is_empty(old_value):

            merged[key] = deepcopy(new_value)

    return merged


# =====================================================
# CLEAN ENTITY
# =====================================================

def clean_entity(
    entity: Dict
) -> Dict:
    """
    Nettoyage léger après fusion.

    Supprime uniquement les valeurs
    inutiles dans les listes.
    """

    cleaned = deepcopy(entity)

    for key, value in cleaned.items():

        if isinstance(value, list):

            cleaned[key] = [

                item

                for item in value

                if not is_empty(item)

            ]

        elif isinstance(value, dict):

            cleaned[key] = clean_entity(
                value
            )

    return cleaned


# =====================================================
# ENTITY MERGER
# =====================================================

def merge_entities(
    original: Dict,
    enriched: Dict
) -> Dict:
    """
    Fonction principale.

    Cette fonction est utilisée
    par tout le pipeline.

    Garanties :

    ✓ aucune donnée supprimée

    ✓ aucune valeur vide ne remplace
      une valeur valide

    ✓ ajout automatique des nouveaux champs

    ✓ fusion récursive

    ✓ fusion intelligente des listes

    ✓ fusion des founders,
      investors,
      partners,
      leadership,
      team_members...

    ✓ compatible Startup

    ✓ compatible Investor

    ✓ compatible Accelerator

    ✓ compatible Incubator
    """

    if not isinstance(original, dict):

        original = {}

    if not isinstance(enriched, dict):

        return deepcopy(original)

    merged = merge_dicts(
        original,
        enriched
    )

    return clean_entity(
        merged
    )
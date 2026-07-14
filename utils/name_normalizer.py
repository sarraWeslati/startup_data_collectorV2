# utils/name_normalizer.py

import re
import unicodedata


# =====================================================
# NORMALIZE NAME
# =====================================================

def normalize_name(
    name: str
) -> str:
    """
    Normalise le nom d'une entreprise.

    Exemple :

    " InstaDeep "

        ↓

    "instadeep"

    "216 Capital Ventures"

        ↓

    "216 capital ventures"
    """

    if not isinstance(
        name,
        str
    ):

        return ""

    # -----------------------------------------
    # Strip
    # -----------------------------------------

    name = name.strip()

    # -----------------------------------------
    # Lowercase
    # -----------------------------------------

    name = name.lower()

    # -----------------------------------------
    # Remove accents
    # -----------------------------------------

    name = unicodedata.normalize(
        "NFKD",
        name
    )

    name = "".join(

        c

        for c in name

        if not unicodedata.combining(c)

    )

    # -----------------------------------------
    # Replace separators
    # -----------------------------------------

    name = name.replace(
        "_",
        " "
    )

    name = name.replace(
        "-",
        " "
    )

    # -----------------------------------------
    # Remove punctuation
    # -----------------------------------------

    name = re.sub(

        r"[^\w\s]",

        "",

        name

    )

    # -----------------------------------------
    # Collapse spaces
    # -----------------------------------------

    name = re.sub(

        r"\s+",

        " ",

        name

    ).strip()

    return name


# =====================================================
# BUILD ENTITY ID
# =====================================================

def build_entity_id(
    normalized_name: str,
    website: str = ""
) -> str:
    """
    Génère un identifiant stable
    à partir du nom et du domaine.

    Exemple :

    instadeep
    +
    instadeep.com

        ↓

    instadeep_instadeep_com
    """

    if not normalized_name:

        return ""

    website = website.lower()

    website = website.replace(
        "https://",
        ""
    )

    website = website.replace(
        "http://",
        ""
    )

    website = website.replace(
        "www.",
        ""
    )

    website = website.replace(
        "/",
        ""
    )

    website = website.replace(
        ".",
        "_"
    )

    if website:

        return f"{normalized_name}_{website}"

    return normalized_name
# etl/normalizers/phone_normalizer.py

import re

from typing import (
    Dict,
    List,
    Tuple
)

# =====================================================
# E164
# =====================================================

MIN_PHONE_LENGTH = 8
MAX_PHONE_LENGTH = 15


# =====================================================
# INVALID PHONE VALUES
# =====================================================

INVALID_VALUES = {

    "",

    "-",

    "--",

    "---",

    "none",

    "null",

    "n/a",

    "na",

    "undefined",

    "unknown",

    "0"

}


# =====================================================
# INVALID PATTERNS
# =====================================================

INVALID_PATTERNS = [

    # timestamps Javascript
    r"^1[56789]\d{9,}$",

    # ids HTML
    r"^\d{12,20}$",

    # petits ids
    r"^\d{1,6}$",

    # seulement des zéros
    r"^0+$"

]


# =====================================================
# AFRICAN PHONE PREFIXES
# =====================================================

AFRICAN_PREFIXES = {

    "20": "Egypt",

    "27": "South Africa",

    "212": "Morocco",

    "213": "Algeria",

    "216": "Tunisia",

    "218": "Libya",

    "220": "Gambia",

    "221": "Senegal",

    "222": "Mauritania",

    "223": "Mali",

    "224": "Guinea",

    "225": "Côte d'Ivoire",

    "226": "Burkina Faso",

    "227": "Niger",

    "228": "Togo",

    "229": "Benin",

    "230": "Mauritius",

    "231": "Liberia",

    "232": "Sierra Leone",

    "233": "Ghana",

    "234": "Nigeria",

    "235": "Chad",

    "236": "Central African Republic",

    "237": "Cameroon",

    "238": "Cape Verde",

    "239": "São Tomé and Príncipe",

    "240": "Equatorial Guinea",

    "241": "Gabon",

    "242": "Republic of the Congo",

    "243": "Democratic Republic of the Congo",

    "244": "Angola",

    "245": "Guinea-Bissau",

    "248": "Seychelles",

    "249": "Sudan",

    "250": "Rwanda",

    "251": "Ethiopia",

    "252": "Somalia",

    "253": "Djibouti",

    "254": "Kenya",

    "255": "Tanzania",

    "256": "Uganda",

    "257": "Burundi",

    "258": "Mozambique",

    "260": "Zambia",

    "261": "Madagascar",

    "262": "Réunion",

    "263": "Zimbabwe",

    "264": "Namibia",

    "265": "Malawi",

    "266": "Lesotho",

    "267": "Botswana",

    "268": "Eswatini",

    "269": "Comoros"

}


# =====================================================
# NATIONAL NUMBER LENGTHS
# (after country code)
# =====================================================

PHONE_LENGTHS = {

    "216": 8,

    "212": 9,

    "213": 9,

    "234": 10,

    "233": 9,

    "254": 9,

    "27": 9,

    "20": 10,

    "225": 8,

    "221": 9,

    "250": 9,

    "251": 9,

    "255": 9,

    "256": 9

}

# =====================================================
# EXTRACT DIGITS
# =====================================================

def extract_digits(
    phone: str
) -> str:
    """
    Garde uniquement les chiffres.
    """

    if not phone:
        return ""

    return re.sub(
        r"\D",
        "",
        str(phone)
    )


# =====================================================
# NORMALIZE PLUS
# =====================================================

def normalize_plus(
    phone: str
) -> str:
    """
    Corrige le caractère '+'.

    Exemple :

    ++21650747433
    -> +21650747433

    21650747433
    -> +21650747433
    """

    if not phone:
        return ""

    phone = phone.strip()

    # Plusieurs +
    if phone.count("+") > 1:

        phone = "+" + phone.replace(
            "+",
            ""
        )

    # + au milieu
    elif "+" in phone and not phone.startswith("+"):

        phone = "+" + phone.replace(
            "+",
            ""
        )

    return phone


# =====================================================
# CLEAN PHONE
# =====================================================

def clean_phone(
    phone: str
) -> str:
    """
    Nettoie complètement un numéro.
    """

    if not phone:
        return ""

    phone = str(phone)

    # Parenthèses
    phone = phone.replace(
        "(",
        ""
    )

    phone = phone.replace(
        ")",
        ""
    )

    # Tirets
    phone = phone.replace(
        "-",
        ""
    )

    # Espaces
    phone = phone.replace(
        " ",
        ""
    )

    # Tabulations
    phone = phone.replace(
        "\t",
        ""
    )

    phone = phone.replace(
        "\n",
        ""
    )

    # Corrige le +
    phone = normalize_plus(
        phone
    )

    # Si aucun +
    if not phone.startswith("+"):

        digits = extract_digits(
            phone
        )

        # On garde seulement les chiffres
        phone = digits

    else:

        digits = extract_digits(
            phone
        )

        phone = "+" + digits

    return phone

# =====================================================
# INVALID PATTERN
# =====================================================

def is_invalid_pattern(
    phone: str
) -> bool:
    """
    Détecte les faux numéros provenant
    du scraping HTML.

    Exemples :

    1700577148
    1767858566164
    900104
    """

    digits = extract_digits(
        phone
    )

    if not digits:
        return True

    for pattern in INVALID_PATTERNS:

        if re.match(
            pattern,
            digits
        ):

            return True

    return False


# =====================================================
# DETECT PREFIX
# =====================================================

def detect_country_prefix(
    phone: str
) -> tuple:

    digits = extract_digits(
        phone
    )

    for prefix in sorted(

        AFRICAN_PREFIXES.keys(),

        key=len,

        reverse=True

    ):

        if digits.startswith(
            prefix
        ):

            return (

                prefix,

                AFRICAN_PREFIXES[
                    prefix
                ]

            )

    return None, None


# =====================================================
# VALID PREFIX
# =====================================================

def has_valid_prefix(
    phone: str
) -> bool:

    prefix, _ = detect_country_prefix(
        phone
    )

    return prefix is not None

# =====================================================
# VALID LENGTH
# =====================================================

def has_valid_length(
    phone: str
) -> bool:

    prefix, _ = detect_country_prefix(
        phone
    )

    if not prefix:

        return False

    digits = extract_digits(
        phone
    )

    national_number = digits[
        len(prefix):
    ]

    expected = PHONE_LENGTHS.get(
        prefix
    )

    if expected is None:

        return (

            MIN_PHONE_LENGTH

            <=

            len(national_number)

            <=

            MAX_PHONE_LENGTH

        )

    return len(
        national_number
    ) == expected

# =====================================================
# VALID PHONE
# =====================================================

def is_valid_phone(
    phone: str
) -> bool:

    phone = clean_phone(
        phone
    )

    if not phone:

        return False

    if is_invalid_pattern(
        phone
    ):

        return False

    if not phone.startswith("+"):

        return False

    if not has_valid_prefix(
        phone
    ):

        return False

    if not has_valid_length(
        phone
    ):

        return False

    return True

# =====================================================
# NORMALIZE PHONE LIST
# =====================================================

def normalize_phone_list(
    phones: List[str]
) -> Tuple[List[str], Dict]:
    """
    Nettoie une liste de numéros.

    Retourne :

        phones nettoyés

        rapport qualité
    """

    normalized = []

    invalid = []

    duplicates = 0

    seen = set()

    for phone in phones:

        cleaned = clean_phone(
            phone
        )

        if not is_valid_phone(
            cleaned
        ):

            invalid.append(phone)

            continue

        if cleaned in seen:

            duplicates += 1

            continue

        seen.add(cleaned)

        normalized.append(build_phone_object(
            cleaned
        ))

    report = {

        "total": len(phones),

        "valid": len(normalized),

        "removed": len(invalid),

        "duplicates": duplicates,

        "invalid": invalid

    }

    return normalized, report

# =====================================================
# NORMALIZE ENTITY PHONES
# =====================================================

def normalize_phone_numbers(
    entity: Dict
) -> Dict:
    """
    Nettoie les téléphones d'une startup
    ou d'un investisseur.
    """

    contact = entity.get(
        "contact",
        {}
    )

    if not isinstance(contact, dict):

        contact = {}

    phones = contact.get(
        "phones",
        []
    )

    if not isinstance(phones, list):

        phones = []

    country = entity.get(
        "country",
        ""
    )
    phones = [
        add_country_prefix(
            phone,
            country
        )
        for phone in phones
    ]
    normalized, report = normalize_phone_list(
        phones
    )

    contact["phones"] = normalized

    entity["contact"] = contact

    entity.setdefault(
        "quality",
        {}
    )

    entity["quality"]["phones"] = report

    entity["stats"] = entity.get(
        "stats",
        {}
    )

    entity["stats"]["phones"] = phone_statistics(

        normalized

    )

    return entity
# =====================================================
# ADD COUNTRY PREFIX
# =====================================================

def add_country_prefix(
    phone: str,
    country: str
) -> str:
    """
    Ajoute automatiquement l'indicatif
    international si le numéro est national.

    Exemple

    Tunisia
    50747433
    ->
    +21650747433
    """

    if not phone:

        return ""

    phone = clean_phone(
        phone
    )

    if phone.startswith("+"):

        return phone

    country_prefix = {

        "Tunisia": "+216",

        "Morocco": "+212",

        "Algeria": "+213",

        "Nigeria": "+234",

        "Ghana": "+233",

        "Kenya": "+254",

        "South Africa": "+27",

        "Egypt": "+20",

        "Senegal": "+221"

    }

    prefix = country_prefix.get(
        country
    )

    if not prefix:

        return phone

    return prefix + phone

# =====================================================
# BUILD PHONE OBJECT
# =====================================================

def build_phone_object(
    phone: str,
    source: str = "website"
) -> Dict:
    """
    Construit un objet téléphone normalisé.
    """

    prefix, country = detect_country_prefix(
        phone
    )

    return {

        "number": phone,

        "country": country,

        "country_code": (

            "+" + prefix

            if prefix

            else ""

        ),

        "valid": is_valid_phone(
            phone
        ),

        "source": source

    }

# =====================================================
# PHONE STATISTICS
# =====================================================

def phone_statistics(
    phones: List[Dict]
) -> Dict:

    countries = sorted({

        phone["country"]

        for phone in phones

        if phone["country"]

    })

    return {

        "count": len(
            phones
        ),

        "countries": countries,

        "valid": sum(

            phone["valid"]

            for phone in phones

        )

    }

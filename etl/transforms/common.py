# etl/transforms/common.py

from copy import deepcopy
from typing import Any
from typing import Dict
from typing import List


# =====================================================
# EMPTY VALUES
# =====================================================

EMPTY_VALUES = (

    None,

    "",

    [],

    {},

    "None",

    "none",

    "NULL",

    "null",

    "N/A",

    "n/a",

    "-"

)


# =====================================================
# EMPTY CHECK
# =====================================================

def is_empty(
    value: Any
) -> bool:

    return value in EMPTY_VALUES


# =====================================================
# STRING
# =====================================================

def normalize_string(
    value: Any
):

    if not isinstance(
        value,
        str
    ):

        return value

    value = value.strip()

    return value


# =====================================================
# LIST
# =====================================================

def normalize_list(
    values
):

    if not isinstance(
        values,
        list
    ):

        return values

    cleaned = []

    seen = set()

    for value in values:

        if is_empty(
            value
        ):

            continue

        if isinstance(
            value,
            str
        ):

            value = normalize_string(
                value
            )

        key = str(
            value
        ).lower()

        if key in seen:

            continue

        seen.add(
            key
        )

        cleaned.append(
            value
        )

    return cleaned


# =====================================================
# DICTIONARY
# =====================================================

def normalize_dict(
    data: Dict
):

    if not isinstance(
        data,
        dict
    ):

        return data

    cleaned = {}

    for key, value in data.items():

        if is_empty(
            value
        ):

            continue

        cleaned[key] = value

    return cleaned


# =====================================================
# COPY
# =====================================================

def clone_entity(
    entity: Dict
) -> Dict:

    return deepcopy(
        entity
    )
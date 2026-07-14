# etl/validators/common.py

import re

from typing import Any
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
# EMPTY
# =====================================================

def is_empty(
    value: Any
) -> bool:

    return value in EMPTY_VALUES


# =====================================================
# REQUIRED FIELD
# =====================================================

def validate_required(
    value: Any,
    field: str,
    errors: List[str]
):

    if is_empty(value):

        errors.append(

            f"{field} is required."

        )


# =====================================================
# URL
# =====================================================

def validate_url(
    url: str,
    field: str,
    errors: List[str]
):

    if is_empty(url):

        return

    pattern = r"^https?://"

    if not re.match(
        pattern,
        url
    ):

        errors.append(

            f"{field} is not a valid URL."

        )


# =====================================================
# EMAIL
# =====================================================

def validate_email(
    email: str,
    field: str,
    errors: List[str]
):

    if is_empty(email):

        return

    pattern = r"^[^@]+@[^@]+\.[^@]+$"

    if not re.match(
        pattern,
        email
    ):

        errors.append(

            f"{field} is not a valid email."

        )


# =====================================================
# LIST
# =====================================================

def validate_list(
    value,
    field: str,
    errors: List[str]
):

    if is_empty(value):

        return

    if not isinstance(
        value,
        list
    ):

        errors.append(

            f"{field} must be a list."

        )


# =====================================================
# DICTIONARY
# =====================================================

def validate_dict(
    value,
    field: str,
    errors: List[str]
):

    if is_empty(value):

        return

    if not isinstance(
        value,
        dict
    ):

        errors.append(

            f"{field} must be a dictionary."

        )
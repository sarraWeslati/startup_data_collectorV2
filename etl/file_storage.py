import json

from pathlib import Path
from typing import Dict
from typing import List

from etl.config import (

    JSON_ENCODING,
    JSON_INDENT,
    JSON_ASCII,

    TRANSFORMED_STARTUPS_DIR,
    TRANSFORMED_INVESTORS_DIR,

    VALIDATED_STARTUPS_DIR,
    VALIDATED_INVESTORS_DIR,

    REJECTED_STARTUPS_DIR,
    REJECTED_INVESTORS_DIR,

    DEDUPLICATED_STARTUPS_DIR,
    DEDUPLICATED_INVESTORS_DIR,

    REPORTS_DIR
)

# =====================================================
# CREATE DIRECTORY
# =====================================================

def ensure_directory(
    directory: Path
):

    directory.mkdir(

        parents=True,

        exist_ok=True

    )

# =====================================================
# SAVE JSON
# =====================================================

def save_json(
    filepath: Path,
    data
):

    ensure_directory(

        filepath.parent

    )

    with open(

        filepath,

        "w",

        encoding=JSON_ENCODING

    ) as f:

        json.dump(

            data,

            f,

            indent=JSON_INDENT,

            ensure_ascii=JSON_ASCII

        )

# =====================================================
# SAFE FILE NAME
# =====================================================

def safe_filename(
    name: str
) -> str:

    if not name:

        return "unknown"

    return (

        name

        .replace("/", "_")

        .replace("\\", "_")

        .replace(":", "_")

        .replace("*", "_")

        .replace("?", "_")

        .replace('"', "_")

        .replace("<", "_")

        .replace(">", "_")

        .replace("|", "_")

        .strip()

    )

# =====================================================
# SAVE TRANSFORMED
# =====================================================

def save_transformed_entities(
    entities: Dict[str, List[Dict]]
):
    """
    Sauvegarde toutes les entités
    transformées.
    """

    # -----------------------------------------
    # STARTUPS
    # -----------------------------------------

    for startup in entities.get(
        "startups",
        []
    ):

        filename = (

            safe_filename(

                startup.get(
                    "name",
                    "startup"
                )

            )

            + ".json"

        )

        save_json(

            TRANSFORMED_STARTUPS_DIR / filename,

            startup

        )

    # -----------------------------------------
    # INVESTORS
    # -----------------------------------------

    for investor in entities.get(
        "investors",
        []
    ):

        filename = (

            safe_filename(

                investor.get(
                    "name",
                    "investor"
                )

            )

            + ".json"

        )

        save_json(

            TRANSFORMED_INVESTORS_DIR / filename,

            investor

        )

# =====================================================
# SAVE VALIDATED
# =====================================================

def save_validated_entities(
    entities: Dict[str, List[Dict]]
):
    """
    Sauvegarde les entités validées.
    """

    # -----------------------------------------
    # STARTUPS
    # -----------------------------------------

    for startup in entities.get(
        "startups",
        []
    ):

        filename = (

            safe_filename(

                startup.get(
                    "name",
                    "startup"
                )

            )

            + ".json"

        )

        save_json(

            VALIDATED_STARTUPS_DIR / filename,

            startup

        )

    # -----------------------------------------
    # INVESTORS
    # -----------------------------------------

    for investor in entities.get(
        "investors",
        []
    ):

        filename = (

            safe_filename(

                investor.get(
                    "name",
                    "investor"
                )

            )

            + ".json"

        )

        save_json(

            VALIDATED_INVESTORS_DIR / filename,

            investor

        )

# =====================================================
# SAVE REJECTED
# =====================================================

def save_rejected_entities(
    validated: Dict
):
    """
    Sauvegarde les entités rejetées
    avec leurs erreurs.
    """

    # -----------------------------------------
    # STARTUPS
    # -----------------------------------------

    rejected_startups = validated.get(
        "startups",
        {}
    ).get(
        "rejected_entities",
        []
    )

    for item in rejected_startups:

        entity = item["entity"]

        filename = (
            safe_filename(
                entity.get(
                    "name",
                    "startup"
                )
            )
            + ".json"
        )

        save_json(
            REJECTED_STARTUPS_DIR / filename,
            item
        )

    # -----------------------------------------
    # INVESTORS
    # -----------------------------------------

    rejected_investors = validated.get(
        "investors",
        {}
    ).get(
        "rejected_entities",
        []
    )

    for item in rejected_investors:

        entity = item["entity"]

        filename = (
            safe_filename(
                entity.get(
                    "name",
                    "investor"
                )
            )
            + ".json"
        )

        save_json(
            REJECTED_INVESTORS_DIR / filename,
            item
        )
        
# =====================================================
# SAVE DEDUPLICATED
# =====================================================

def save_deduplicated_entities(
    entities: Dict[str, List[Dict]]
):
    """
    Sauvegarde les entités
    après déduplication.
    """

    for startup in entities.get(
        "startups",
        []
    ):

        filename = (

            safe_filename(
                startup.get(
                    "name",
                    "startup"
                )
            )

            + ".json"

        )

        save_json(

            DEDUPLICATED_STARTUPS_DIR / filename,

            startup

        )

    for investor in entities.get(
        "investors",
        []
    ):

        filename = (

            safe_filename(
                investor.get(
                    "name",
                    "investor"
                )
            )

            + ".json"

        )

        save_json(

            DEDUPLICATED_INVESTORS_DIR / filename,

            investor

        )

# =====================================================
# SAVE REPORT
# =====================================================

def save_etl_report(
    report: Dict
):
    """
    Sauvegarde le rapport ETL.
    """

    save_json(

        REPORTS_DIR / "etl_report.json",

        report

    )


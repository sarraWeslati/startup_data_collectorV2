# etl/extractor.py

import json

from pathlib import Path
from typing import Dict
from typing import List

from etl.config import (
    STARTUPS_DIR,
    INVESTORS_DIR,
    JSON_ENCODING
)


# =====================================================
# JSON LOADER
# =====================================================

def load_json(
    filepath: Path
) -> Dict:
    """
    Charge un fichier JSON.
    """

    with open(
        filepath,
        "r",
        encoding=JSON_ENCODING
    ) as f:

        return json.load(f)


# =====================================================
# DIRECTORY LOADER
# =====================================================

def load_directory(
    directory: Path
) -> List[Dict]:
    """
    Charge tous les JSON d'un dossier.
    """

    entities = []

    if not directory.exists():

        return entities

    json_files = sorted(
        directory.rglob("*.json")
    )

    print(
        f"[EXTRACT] {directory.name} : {len(json_files)} file(s)"
    )

    for filepath in json_files:

        try:

            entity = load_json(
                filepath
            )

            entity["_source_file"] = str(
                filepath
            )

            entities.append(
                entity
            )

        except Exception as e:

            print(
                f"[EXTRACT ERROR] {filepath.name}"
            )

            print(e)

    return entities


# =====================================================
# STARTUPS
# =====================================================

def load_startups() -> List[Dict]:
    """
    Charge toutes les startups enrichies.
    """

    return load_directory(
        STARTUPS_DIR
    )


# =====================================================
# INVESTORS
# =====================================================

def load_investors() -> List[Dict]:
    """
    Charge tous les investisseurs enrichis.
    """

    return load_directory(
        INVESTORS_DIR
    )


# =====================================================
# ALL ENTITIES
# =====================================================

def load_entities() -> Dict[str, List[Dict]]:
    """
    Charge toutes les entités.
    """

    startups = load_startups()

    investors = load_investors()

    print()

    print(
        f"Startups  : {len(startups)}"
    )

    print(
        f"Investors : {len(investors)}"
    )

    print()

    return {

        "startups": startups,

        "investors": investors

    }

# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    entities = load_entities()

    print("\n")
    print("=" * 80)
    print("EXTRACT TEST")
    print("=" * 80)

    print(
        f"Startups : {len(entities['startups'])}"
    )

    print(
        f"Investors : {len(entities['investors'])}"
    )

    if entities["startups"]:

        print("\nFirst startup:\n")

        print(
            entities["startups"][0]
        )

    if entities["investors"]:

        print("\nFirst investor:\n")

        print(
            entities["investors"][0]
        )
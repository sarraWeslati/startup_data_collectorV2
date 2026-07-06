# utils/entity_loader.py

import json

from pathlib import Path
from typing import Dict

from utils.entity_merger import merge_entities


EXTRACTED_DIR = Path(
    "storage/extracted"
)

ENRICHED_DIR = Path(
    "storage/enriched"
)


def load_json(
    filepath: Path
) -> Dict:

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def load_best_entity(
    extracted_filepath: Path,
    extracted_entity: Dict
) -> Dict:
    """
    Charge la meilleure version disponible.

    Priorité :

    storage/enriched

    puis

    storage/extracted
    """

    relative = extracted_filepath.relative_to(
        EXTRACTED_DIR
    )

    enriched_path = (
        ENRICHED_DIR /
        relative
    )

    if not enriched_path.exists():

        return extracted_entity

    print(
        f"[FOUND ENRICHED] {enriched_path.name}"
    )

    try:

        enriched_entity = load_json(
            enriched_path
        )

    except Exception as e:

        print(
            f"[ENTITY LOADER] {e}"
        )

        return extracted_entity

    merged = merge_entities(

        enriched_entity,

        extracted_entity

    )

    print(
        "[MERGED] Existing enriched entity loaded."
    )

    return merged
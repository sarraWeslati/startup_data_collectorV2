# storage/entity_storage.py

import json
import re
from pathlib import Path
from typing import Dict, Any


def slugify(text: str) -> str:
    """
    Transforme un nom en nom de fichier valide.

    Exemple:
    "216 Capital" -> "216_capital"
    "The Dot" -> "the_dot"
    """

    if not text:
        return "unknown"

    text = text.lower().strip()

    text = re.sub(r"[^a-z0-9]+", "_", text)

    text = text.strip("_")

    return text or "unknown"


def get_entity_folder(entity_type: str) -> str:
    """
    Détermine le dossier de destination.
    """

    mapping = {
        "startup": "startups",
        "investor": "investors",
        "venture_capital_fund": "investors",
        "incubator": "incubators",
        "accelerator": "accelerators",
        "support_organization": "organizations",
        "government_program": "government_programs",
    }

    return mapping.get(entity_type, "others")


def save_entity(entity: Dict[str, Any]) -> str:
    """
    Sauvegarde une entité dans un fichier JSON.
    """

    entity_type = entity.get(
        "entity_type",
        "other"
    )

    entity_name = entity.get(
        "name",
        "unknown"
    )

    folder = get_entity_folder(entity_type)

    output_dir = Path(
        f"storage/extracted/{folder}"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = slugify(entity_name) + ".json"

    filepath = output_dir / filename

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            entity,
            f,
            indent=4,
            ensure_ascii=False
        )

    return str(filepath)


def save_entities(entities: list) -> list:
    """
    Sauvegarde plusieurs entités.
    """

    saved_files = []

    for entity in entities:

        try:

            filepath = save_entity(entity)

            saved_files.append(filepath)

            print(
                f"[SAVED] {filepath}"
            )

        except Exception as e:

            print(
                f"[ERROR] Impossible de sauvegarder l'entité : {e}"
            )

    return saved_files


if __name__ == "__main__":

    test_entity = {
        "entity_type": "startup",
        "name": "Deplike",
        "description": "MusicTech startup",
        "country": "Tunisia",
        "website": "https://deplike.com"
    }

    saved_file = save_entity(
        test_entity
    )

    print(
        f"\nFichier créé : {saved_file}"
    )
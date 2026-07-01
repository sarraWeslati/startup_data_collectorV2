from typing import Dict, List

from storage.entity_storage import save_entity


DIRECTORY_MAPPING = {

    "startup_directory": (
        "startups",
        "startup"
    ),

    "investor_directory": (
        "investors",
        "investor"
    ),

    "incubator_directory": (
        "incubators",
        "incubator"
    ),

    "accelerator_directory": (
        "accelerators",
        "accelerator"
    )

}


def save_directory_result(
    directory_result: Dict
) -> List[str]:
    """
    Sauvegarde automatiquement toutes les entités
    extraites d'un annuaire.
    """

    entity_type = directory_result.get(
        "entity_type",
        ""
    )

    mapping = DIRECTORY_MAPPING.get(
        entity_type
    )

    if mapping is None:

        print(
            f"[WARNING] Unsupported directory type: {entity_type}"
        )

        return []

    collection_name, entity_name = mapping

    entities = directory_result.get(
        collection_name,
        []
    )

    saved_files = []

    for entity in entities:

        entity["entity_type"] = entity_name

        filepath = save_entity(
            entity
        )

        saved_files.append(
            filepath
        )

    return saved_files


if __name__ == "__main__":

    test_data = {

        "entity_type": "startup_directory",

        "startups": [

            {
                "name": "Deplike",
                "description": "MusicTech startup",
                "country": "Tunisia"
            },

            {
                "name": "Konnect",
                "description": "FinTech startup",
                "country": "Tunisia"
            }

        ]

    }

    files = save_directory_result(
        test_data
    )

    print("\nFichiers créés :")

    for file in files:

        print(file)
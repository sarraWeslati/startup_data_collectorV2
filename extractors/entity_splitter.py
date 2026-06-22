# extractors/entity_splitter.py

from typing import Dict, List

from storage.entity_storage import save_entity


def save_startups(directory_result: Dict) -> List[str]:
    """
    Sauvegarde toutes les startups trouvées.
    """

    startups = directory_result.get(
        "startups",
        []
    )

    saved_files = []

    for startup in startups:

        startup["entity_type"] = "startup"

        filepath = save_entity(startup)

        saved_files.append(filepath)

    return saved_files


def save_investors(directory_result: Dict) -> List[str]:
    """
    Sauvegarde tous les investisseurs trouvés.
    """

    investors = directory_result.get(
        "investors",
        []
    )

    saved_files = []

    for investor in investors:

        investor["entity_type"] = "investor"

        filepath = save_entity(investor)

        saved_files.append(filepath)

    return saved_files


def save_incubators(directory_result: Dict) -> List[str]:
    """
    Sauvegarde tous les incubateurs trouvés.
    """

    incubators = directory_result.get(
        "incubators",
        []
    )

    saved_files = []

    for incubator in incubators:

        incubator["entity_type"] = "incubator"

        filepath = save_entity(incubator)

        saved_files.append(filepath)

    return saved_files


def save_accelerators(directory_result: Dict) -> List[str]:
    """
    Sauvegarde tous les accélérateurs trouvés.
    """

    accelerators = directory_result.get(
        "accelerators",
        []
    )

    saved_files = []

    for accelerator in accelerators:

        accelerator["entity_type"] = "accelerator"

        filepath = save_entity(accelerator)

        saved_files.append(filepath)

    return saved_files


def save_directory_result(directory_result: Dict) -> List[str]:
    """
    Détecte automatiquement le type du répertoire
    et appelle la bonne fonction.
    """

    entity_type = directory_result.get(
        "entity_type",
        ""
    )

    if entity_type == "startup_directory":
        return save_startups(directory_result)

    if entity_type == "investor_directory":
        return save_investors(directory_result)

    if entity_type == "incubator_directory":
        return save_incubators(directory_result)

    if entity_type == "accelerator_directory":
        return save_accelerators(directory_result)

    print(
        f"[WARNING] Type non supporté : {entity_type}"
    )

    return []


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
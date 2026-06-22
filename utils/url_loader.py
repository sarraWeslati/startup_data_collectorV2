# utils/url_loader.py

from pathlib import Path
from typing import List


def load_urls(file_path: str) -> List[str]:
    """
    Charge les URLs depuis un fichier texte.

    Exemple de fichier :

    # Sources startups
    https://startup.gov.tn
    https://www.thedot.tn

    # Investisseurs
    https://216capital.vc
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {file_path}"
        )

    urls = []
    seen = set()

    with open(path, "r", encoding="utf-8") as file:

        for line in file:

            line = line.strip()

            # Ignorer les lignes vides
            if not line:
                continue

            # Ignorer les commentaires
            if line.startswith("#"):
                continue

            # Supprimer les doublons
            if line in seen:
                continue

            seen.add(line)
            urls.append(line)

    return urls


def save_urls(
    urls: List[str],
    file_path: str
) -> None:
    """
    Sauvegarde une liste d'URLs dans un fichier.
    """

    path = Path(file_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(path, "w", encoding="utf-8") as file:

        for url in urls:
            file.write(url.strip() + "\n")


def add_url(
    url: str,
    file_path: str
) -> None:
    """
    Ajoute une URL au fichier si elle n'existe pas déjà.
    """

    urls = []

    if Path(file_path).exists():
        urls = load_urls(file_path)

    if url not in urls:
        urls.append(url)

    save_urls(urls, file_path)


def remove_url(
    url: str,
    file_path: str
) -> None:
    """
    Supprime une URL du fichier.
    """

    if not Path(file_path).exists():
        return

    urls = load_urls(file_path)

    urls = [
        existing_url
        for existing_url in urls
        if existing_url != url
    ]

    save_urls(urls, file_path)


if __name__ == "__main__":

    urls = load_urls(
        "data/sources.txt"
    )

    print("\nURLs chargées :\n")

    for url in urls:
        print(url)

    print(
        f"\nTotal : {len(urls)} URL(s)"
    )
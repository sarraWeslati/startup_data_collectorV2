# utils/url_normalizer.py

from typing import Any


def normalize_website(
    url: Any
) -> str:
    """
    Normalise une URL.

    Accepte :
        - str
        - dict
        - None

    Retourne toujours une chaîne.
    """

    if not url:
        return ""

    # --------------------------------------------------
    # Cas dictionnaire
    # --------------------------------------------------

    if isinstance(url, dict):

        # cas {"url": "..."}
        if "url" in url:
            url = url["url"]

        # cas {"website": "..."}
        elif "website" in url:
            url = url["website"]

        else:
            return ""

    # --------------------------------------------------
    # Sécurité
    # --------------------------------------------------

    if not isinstance(url, str):
        url = str(url)

    url = url.strip()

    if not url:
        return ""

    # Supprime les espaces
    url = url.replace(" ", "")

    # www.domain.com
    if url.startswith("www."):
        return f"https://{url}"

    # domain.com
    if (
        "." in url
        and not url.startswith(("http://", "https://"))
        and "/" not in url
    ):
        return f"https://{url}"

    # Cas spécifique TheDot
    if url.startswith("https://thedot.tn/"):

        candidate = url.replace(
            "https://thedot.tn/",
            ""
        )

        if "." in candidate:
            return f"https://{candidate}"

    return url
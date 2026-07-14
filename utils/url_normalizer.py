from typing import Any

from urllib.parse import urlparse


# =====================================================
# NORMALIZE WEBSITE
# =====================================================

def normalize_website(
    url: Any
) -> str:

    if not url:
        return ""

    if isinstance(url, dict):

        if "url" in url:
            url = url["url"]

        elif "website" in url:
            url = url["website"]

        else:
            return ""

    if not isinstance(url, str):
        url = str(url)

    url = url.strip()

    if not url:
        return ""

    url = url.replace(" ", "")

    if url.startswith("www."):
        url = f"https://{url}"

    elif (
        "." in url
        and not url.startswith(("http://", "https://"))
        and "/" not in url
    ):
        url = f"https://{url}"

    if url.startswith("https://thedot.tn/"):

        candidate = url.replace(
            "https://thedot.tn/",
            ""
        )

        if "." in candidate:

            url = f"https://{candidate}"

    return url


# =====================================================
# DOMAIN
# =====================================================

def get_domain(
    url: Any
) -> str:
    """
    Retourne uniquement le domaine.

    Exemple :

    https://www.instadeep.com/about

    →

    instadeep.com
    """

    url = normalize_website(url)

    if not url:
        return ""

    parsed = urlparse(url)

    domain = parsed.netloc.lower()

    if domain.startswith("www."):

        domain = domain[4:]

    return domain
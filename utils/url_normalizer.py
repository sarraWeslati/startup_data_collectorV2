# utils/url_normalizer.py

def normalize_website(
    url: str
) -> str:

    if not url:
        return ""

    url = url.strip()

    # Supprime espaces
    url = url.replace(
        " ",
        ""
    )

    # Cas www.domain.com

    if url.startswith(
        "www."
    ):

        return (
            f"https://{url}"
        )

    # Cas domain.com

    if (
        "." in url
        and not url.startswith(
            "http"
        )
        and "/" not in url
    ):

        return (
            f"https://{url}"
        )

    # Cas URL cassée venant de TheDot

    if url.startswith(
        "https://thedot.tn/"
    ):

        candidate = (
            url.replace(
                "https://thedot.tn/",
                ""
            )
        )

        if "." in candidate:

            return (
                f"https://{candidate}"
            )

    return url
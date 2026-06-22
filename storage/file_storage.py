from pathlib import Path


def generate_filename(url: str) -> str:

    filename = (
        url.replace("https://", "")
        .replace("http://", "")
        .replace("/", "_")
        .replace("?", "_")
        .replace("&", "_")
        .replace("=", "_")
    )

    return filename + ".md"


def save_raw_content(
    url: str,
    content: str
):

    raw_dir = Path("storage/raw")

    raw_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = generate_filename(url)

    filepath = raw_dir / filename

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(content)

    return filepath
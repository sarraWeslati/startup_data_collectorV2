import re
from typing import List


DEFAULT_CHUNK_SIZE = 5000


# ----------------------------------------------------
# Séparateurs fréquents
# ----------------------------------------------------

SEPARATORS = [

    r"\n-{5,}\n",
    r"\n={5,}\n",
    r"\n_{5,}\n",

]


# ----------------------------------------------------
# Découpage sur séparateurs
# ----------------------------------------------------

def split_by_separator(
    text: str
) -> List[str]:

    for separator in SEPARATORS:

        blocks = re.split(
            separator,
            text
        )

        blocks = [

            block.strip()

            for block in blocks

            if block.strip()

        ]

        if len(blocks) > 1:

            return blocks

    return [text]


# ----------------------------------------------------
# Découpage sur titres (MAJUSCULES)
# ----------------------------------------------------

def split_by_titles(
    text: str
) -> List[str]:
    """
    Détecte les annuaires contenant
    une suite de titres en majuscules.

    Exemple :

    ALIRET SERVICE

    Description...

    BNB TUNISIE

    Description...
    """

    lines = text.splitlines()

    blocks = []

    current = []

    title_pattern = re.compile(
        r"^[A-Z0-9&'().,\- ]{4,}$"
    )

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if (
            title_pattern.match(line)
            and current
        ):

            blocks.append(
                "\n".join(current)
            )

            current = []

        current.append(line)

    if current:

        blocks.append(
            "\n".join(current)
        )

    if len(blocks) > 1:

        return blocks

    return [text]


# ----------------------------------------------------
# Découpage intelligent par taille
# ----------------------------------------------------

def split_by_size(
    blocks: List[str],
    chunk_size: int = DEFAULT_CHUNK_SIZE
) -> List[str]:

    chunks = []

    current = ""

    for block in blocks:

        if len(block) > chunk_size:

            if current:

                chunks.append(
                    current.strip()
                )

                current = ""

            for i in range(
                0,
                len(block),
                chunk_size
            ):

                chunks.append(
                    block[
                        i:i + chunk_size
                    ]
                )

            continue

        if len(current) + len(block) < chunk_size:

            current += "\n\n" + block

        else:

            if current.strip():

                chunks.append(
                    current.strip()
                )

            current = block

    if current.strip():

        chunks.append(
            current.strip()
        )

    return chunks


# ----------------------------------------------------
# Fonction principale
# ----------------------------------------------------

def smart_chunk(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE
) -> List[str]:
    """
    Découpe intelligemment un document.

    Priorité :

    1. Séparateurs ---------
    2. Titres en majuscules
    3. Taille maximale
    """

    blocks = split_by_separator(
        text
    )

    if len(blocks) == 1:

        blocks = split_by_titles(
            text
        )

    chunks = split_by_size(
        blocks,
        chunk_size
    )

    print(
        f"[SMART CHUNKER] {len(chunks)} chunk(s)"
    )

    return chunks
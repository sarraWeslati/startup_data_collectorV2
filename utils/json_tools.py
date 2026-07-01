import json
import re
from typing import Any, Optional


def clean_json_string(
    text: str
) -> str:
    """
    Nettoie les erreurs courantes produites par les LLM.
    """

    text = text.strip()

    # Supprime les balises Markdown
    text = text.replace("```json", "")
    text = text.replace("```", "")

    # Garde uniquement le JSON
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    # Supprime les virgules avant } ou ]
    text = re.sub(
        r",\s*}",
        "}",
        text
    )

    text = re.sub(
        r",\s*]",
        "]",
        text
    )

    # Supprime les caractères de contrôle
    text = re.sub(
        r"[\x00-\x1f]",
        "",
        text
    )

    return text


def parse_llm_json(
    response: Optional[str]
) -> Optional[Any]:
    """
    Parse une réponse LLM en essayant de corriger
    automatiquement les erreurs JSON les plus fréquentes.
    """

    if not response:
        return None

    json_text = clean_json_string(
        response
    )

    # --------------------------------------------------
    # Premier essai
    # --------------------------------------------------

    try:

        return json.loads(
            json_text
        )

    except json.JSONDecodeError as e:

        print(
            f"[JSON WARNING] {e}"
        )

    # --------------------------------------------------
    # Deuxième essai :
    # suppression des virgules finales
    # --------------------------------------------------

    try:

        fixed = re.sub(
            r",(\s*[}\]])",
            r"\1",
            json_text
        )

        return json.loads(
            fixed
        )

    except json.JSONDecodeError as e:

        print(
            f"[JSON WARNING] Second attempt failed : {e}"
        )

    # --------------------------------------------------
    # Troisième essai :
    # suppression des doubles virgules
    # --------------------------------------------------

    try:

        fixed = re.sub(
            r",\s*,",
            ",",
            json_text
        )

        return json.loads(
            fixed
        )

    except json.JSONDecodeError as e:

        print(
            f"[JSON PARSE ERROR] {e}"
        )

        print("\n========== INVALID JSON ==========\n")
        print(json_text)
        print("\n==================================\n")

        return None
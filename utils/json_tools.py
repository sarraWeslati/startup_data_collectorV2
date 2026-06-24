# utils/json_tools.py

import json
from typing import Any, Optional


def parse_llm_json(
    response: Optional[str]
) -> Optional[Any]:

    if not response:
        return None

    try:

        response = response.strip()

        response = response.replace(
            "```json",
            ""
        )

        response = response.replace(
            "```",
            ""
        )

        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1:
            return None

        json_text = response[
            start:end + 1
        ]

        return json.loads(
            json_text
        )

    except Exception as e:

        print(
            f"[JSON PARSE ERROR] {e}"
        )

        return None

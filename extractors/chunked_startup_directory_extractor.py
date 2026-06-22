# extractors/chunked_startup_directory_extractor.py

import json
from typing import Dict, List

from llm.openrouter_client import call_llm


CHUNK_SIZE = 5000


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE
) -> List[str]:

    chunks = []

    for i in range(
        0,
        len(text),
        chunk_size
    ):
        chunks.append(
            text[i:i + chunk_size]
        )

    return chunks


def build_prompt(content: str) -> str:

    return f"""
You are an expert startup ecosystem analyst.

Extract ALL startups mentioned in the text.

Return ONLY valid JSON.

Schema:

{{
  "startups": [
    {{
      "name": "",
      "description": "",
      "industry": "",
      "country": "",
      "city": "",
      "website": "",
      "linkedin": "",
      "founders": []
    }}
  ]
}}

Rules:

- Return ONLY JSON.
- No markdown.
- No explanations.
- Empty string if unknown.
- Empty array if unknown.

TEXT:

{content}
"""


def parse_response(
    response: str
) -> List[Dict]:

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
            return []

        json_text = response[start:end + 1]

        data = json.loads(json_text)

        return data.get(
            "startups",
            []
        )

    except Exception as e:

        print(
            f"[PARSE ERROR] {e}"
        )

        return []


def deduplicate_startups(
    startups: List[Dict]
) -> List[Dict]:

    unique = {}

    for startup in startups:

        name = startup.get(
            "name",
            ""
        ).strip()

        if not name:
            continue

        key = name.lower()

        if key not in unique:

            startup["entity_type"] = (
                "startup"
            )

            unique[key] = startup

    return list(
        unique.values()
    )


def extract_chunk(
    chunk: str
) -> List[Dict]:

    prompt = build_prompt(chunk)

    response = call_llm(
        prompt=prompt,
        max_tokens=1500
    )

    return parse_response(
        response
    )


def extract_startup_directory_chunked(
    content: str
) -> Dict:

    chunks = chunk_text(content)

    print(
        f"[CHUNKS] {len(chunks)}"
    )

    all_startups = []

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"[PROCESSING CHUNK {index}/{len(chunks)}]"
        )

        startups = extract_chunk(
            chunk
        )

        print(
            f"[FOUND] {len(startups)} startups"
        )

        all_startups.extend(
            startups
        )

    all_startups = (
        deduplicate_startups(
            all_startups
        )
    )

    return {
        "entity_type":
        "startup_directory",
        "startups":
        all_startups
    }


if __name__ == "__main__":

    with open(
        "storage/raw/thedot.tn_4-nos-staurtups.md",
        "r",
        encoding="utf-8"
    ) as f:

        content = f.read()

    result = (
        extract_startup_directory_chunked(
            content
        )
    )

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )
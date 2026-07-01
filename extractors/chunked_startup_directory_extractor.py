# extractors/chunked_startup_directory_extractor.py

import json
from typing import Dict, List

from utils.json_tools import parse_llm_json

from llm.openrouter_client import call_llm_json
from utils.smart_chunker import (
    smart_chunk
)


def build_prompt(
    content: str
) -> str:

    return f"""
You are an expert startup intelligence analyst.

The document is a STARTUP DIRECTORY.

It contains multiple independent startup profiles.

Each startup profile must be extracted independently.

Never merge information from two startups.

Never copy the description of one startup into another.

Extract ONLY startups explicitly present in THIS chunk.

Never use information from previous chunks.

Return ONLY valid JSON.

Schema:

{{
    "startups":[
        {{
            "name":"",
            "description":"",
            "industry":"",
            "country":"",
            "city":"",
            "website":"",
            "linkedin":"",
            "founders":[]
        }}
    ]
}}

Rules:

- One JSON object = one startup.
- One description = one startup.
- Never merge two startups.
- Never invent information.
- Empty string if unknown.
- Empty array if unknown.
- Ignore advertisements.
- Ignore navigation menus.
- Ignore footer links.
- Ignore contact pages.

TEXT:

{content}
"""


def parse_response(
    response: str
) -> List[Dict]:
    """
    Parse la réponse du LLM et retourne
    la liste des startups.
    """

    data = parse_llm_json(
        response
    )

    if not data:
        return []

    if not isinstance(
        data,
        dict
    ):
        return []

    return data.get(
        "startups",
        []
    )


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

    response = call_llm_json(
        prompt=prompt,
        max_tokens=3500
    )

    return parse_response(
        response
    )


def extract_startup_directory_chunked(
    content: str
) -> Dict:

    chunks = smart_chunk(content)

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
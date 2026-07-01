
from typing import Dict, List

from llm.openrouter_client import call_llm_json
from utils.json_tools import parse_llm_json

from utils.smart_chunker import (
    smart_chunk
)

def build_prompt(
    content: str
) -> str:

    return f"""
You are an expert Venture Capital and Investor Intelligence analyst.

The document is an INVESTOR DIRECTORY.

It contains multiple independent investor profiles.

Each investor profile must be extracted independently.

Never merge information from two investors.

Never copy the portfolio of one investor into another.

Extract ONLY investors explicitly present in THIS chunk.

Never use information from previous chunks.

Return ONLY valid JSON.

Schema:

{{
    "investors":[
        {{
            "name":"",
            "description":"",
            "organization_type":"",
            "country":"",
            "city":"",
            "website":"",
            "linkedin":"",
            "investment_focus":[],
            "investment_stages":[],
            "portfolio_startups":[]
        }}
    ]
}}

Rules:

- One JSON object = one investor.
- One portfolio = one investor.
- Never merge investors.
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
    Parse la réponse du LLM.
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
        "investors",
        []
    )

def extract_chunk(
    chunk: str
) -> List[Dict]:

    prompt = build_prompt(
        chunk
    )

    response = call_llm_json(
        prompt,
        max_tokens=3500
    )

    return parse_response(
        response
    )


def deduplicate_investors(
    investors: List[Dict]
) -> List[Dict]:

    unique = {}

    for investor in investors:

        name = investor.get(
            "name",
            ""
        ).strip()

        if not name:
            continue

        key = name.lower()

        if key not in unique:

            investor["entity_type"] = "investor"

            unique[key] = investor

    return list(
        unique.values()
    )

def extract_investor_directory_chunked(
    content: str
) -> Dict:

    chunks = smart_chunk(
        content
    )

    investors = []

    print(
        f"[CHUNKS] {len(chunks)}"
    )

    for index, chunk in enumerate(chunks, start=1):

        print(
            f"[CHUNK {index}/{len(chunks)}]"
        )

        print(
            f"[PROCESSING CHUNK {index}/{len(chunks)}]"
        )

        investors_chunk = extract_chunk(
            chunk
        )

        print(
            f"[FOUND] {len(investors_chunk)} investors"
        )

        investors.extend(
            investors_chunk
        )

    investors = deduplicate_investors(
        investors
    )

    return {

        "entity_type": "investor_directory",

        "investors": investors

    }


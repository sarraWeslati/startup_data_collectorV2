
from typing import Dict, List

from llm.openrouter_client import call_llm_json
from utils.json_tools import parse_llm_json

from utils.smart_chunker import (
    smart_chunk
)

import re

def prepare_directory_chunks(
    content: str
) -> List[str]:
    """
    Prépare intelligemment les blocs à envoyer au LLM
    selon le type d'annuaire.
    """

    # ------------------------------------------------
    # Cas 1 : Tableau Markdown
    # ------------------------------------------------

    table_lines = [

        line

        for line in content.splitlines()

        if line.strip().startswith("|")

    ]

    if len(table_lines) > 20:

        print("[DIRECTORY] Markdown table detected")

        chunks = []

        current = []

        for line in table_lines:

            current.append(line)

            if len(current) >= 10:

                chunks.append("\n".join(current))

                current = []

        if current:

            chunks.append("\n".join(current))

        return chunks

    # ------------------------------------------------
    # Cas 2 : Sections numérotées
    # ------------------------------------------------

    sections = re.split(

        r"\n(?=\d+\.)",

        content

    )

    if len(sections) > 5:

        print("[DIRECTORY] Numbered sections detected")

        return sections

    # ------------------------------------------------
    # Cas 3 : Titres Markdown
    # ------------------------------------------------

    sections = re.split(

        r"\n(?=##+\s)",

        content

    )

    if len(sections) > 5:

        print("[DIRECTORY] Markdown sections detected")

        return sections

    # ------------------------------------------------
    # Cas général
    # ------------------------------------------------

    return smart_chunk(content)


def build_prompt(
    content: str
) -> str:

    return f"""
You are an expert Venture Capital, Angel Investor and Investment Intelligence analyst.

The text below is a fragment of an investor directory.

The directory may come from:

- a markdown table
- a blog article
- a website
- business cards
- search results
- an ecosystem report
- an accelerator website
- an investment platform

Each investor must be extracted independently.

Never merge two investors.

Never invent information.

Ignore:

- menus
- advertisements
- navigation
- cookies
- footer
- contact page
- newsletter
- social buttons

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

- One investor = one JSON object.
- Every investor explicitly mentioned in THIS chunk must appear exactly once.
- Return EVERY investor until the end of the chunk.
- Do NOT stop after extracting only a few investors.
- The JSON array must contain one object for EACH investor found in this chunk.
- If the chunk contains 5 investors, return 5 JSON objects.
- If the chunk contains 20 investors, return 20 JSON objects.
- If the chunk contains 50 investors, return 50 JSON objects.
- Do not skip any investor.
- Ignore duplicate mentions of the same investor.
- Keep empty strings when information is missing.
- Keep empty arrays when information is missing.
- Never infer information.
- Never use information outside this chunk.
- Return ONLY valid JSON.

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
        max_tokens=5000
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

        website = investor.get("website", "").lower().strip()

        linkedin = investor.get("linkedin", "").lower().strip()

        key = website or linkedin or name.lower()

        if key not in unique:

            investor["entity_type"] = "investor"

            unique[key] = investor

    return list(
        unique.values()
    )

def extract_investor_directory_chunked(
    content: str
) -> Dict:

    chunks = prepare_directory_chunks(
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


import json
import os
import re
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()

import requests
from bs4 import BeautifulSoup


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
HEADERS = {"User-Agent": "Mozilla/5.0"}

AFRICAN_COUNTRIES = {
    "algeria", "angola", "benin", "botswana", "burkina faso", "burundi",
    "cabo verde", "cameroon", "central african republic", "chad", "comoros",
    "congo", "democratic republic of the congo", "djibouti", "egypt",
    "equatorial guinea", "eritrea", "eswatini", "ethiopia", "gabon",
    "gambia", "ghana", "guinea", "guinea-bissau", "ivory coast", "kenya",
    "lesotho", "liberia", "libya", "madagascar", "malawi", "mali",
    "mauritania", "mauritius", "morocco", "mozambique", "namibia", "niger",
    "nigeria", "rwanda", "sao tome and principe", "senegal", "seychelles",
    "sierra leone", "somalia", "south africa", "south sudan", "sudan",
    "tanzania", "togo", "tunisia", "uganda", "zambia", "zimbabwe",
}

SCHEMA_KEYS = [
    "name",
    "type",
    "country",
    "website",
    "description",
    "focus",
    "portfolio",
    "source_url",
]


def fetch_page_text(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    meta_description = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        meta_description = meta.get("content", "")

    body = soup.get_text(" ", strip=True)
    return " ".join([title, meta_description, body])


def _extract_json(content):
    content = content.strip()

    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def _is_african_country(country):
    normalized = (country or "").strip().lower()
    return normalized in AFRICAN_COUNTRIES or "africa" in normalized


def _normalise_investor(item, source_url):
    investor = {key: item.get(key, "") for key in SCHEMA_KEYS}
    investor["source_url"] = investor["source_url"] or source_url
    investor["focus"] = investor["focus"] if isinstance(investor["focus"], list) else []
    investor["portfolio"] = (
        investor["portfolio"] if isinstance(investor["portfolio"], list) else []
    )

    for key in ("name", "type", "country", "website", "description", "source_url"):
        investor[key] = str(investor[key] or "").strip()

    investor["focus"] = [str(value).strip() for value in investor["focus"] if value]
    investor["portfolio"] = [
        str(value).strip() for value in investor["portfolio"] if value
    ]

    return investor


def _fallback_website(url):
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


def extract_investors(text, url):
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is missing")

    prompt = f"""
You extract ONLY investors from web page text.

Return ONLY valid JSON. Do not add markdown.

Keep ONLY investors based in Africa, investing in Africa, or based in Tunisia.
Tunisia must be included. Ignore startups, portfolio companies, founders,
events, blog categories, jobs, contact links, generic navigation, and unrelated
companies.

Valid investor types: VC, Angel, Fund, Accelerator, Incubator, Corporate VC,
Private Equity, Family Office, Investment Company.

Each investor must match this exact structure:
{{
  "name": "",
  "type": "",
  "country": "",
  "website": "",
  "description": "",
  "focus": [],
  "portfolio": [],
  "source_url": ""
}}

If no matching investor is present, return:
{{"investors": []}}

TEXT:
{text[:12000]}

SOURCE_URL:
{url}

JSON format:
{{
  "investors": [
    {{
      "name": "",
      "type": "",
      "country": "",
      "website": "",
      "description": "",
      "focus": [],
      "portfolio": [],
      "source_url": ""
    }}
  ]
}}
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    parsed = _extract_json(content)

    investors = []
    for item in parsed.get("investors", []):
        investor = _normalise_investor(item, url)
        if not investor["name"]:
            continue
        if not _is_african_country(investor["country"]):
            continue
        if not investor["website"]:
            investor["website"] = _fallback_website(url)
        investors.append(investor)

    return investors


def run(input_file, output_file, max_pages=None):
    with open(input_file, "r", encoding="utf-8") as f:
        links = json.load(f)

    results = []
    seen = set()
    pages = links[:max_pages] if max_pages else links

    for index, item in enumerate(pages, start=1):
        url = item.get("url", "")
        if not url.startswith(("http://", "https://")):
            continue

        print(f"[{index}/{len(pages)}] Extracting investors from {url}")

        try:
            page_text = fetch_page_text(url)
            investors = extract_investors(page_text, url)
        except Exception as exc:
            print(f"  Error: {exc}")
            continue

        for investor in investors:
            key = (
                investor["name"].lower(),
                investor["website"].lower(),
                investor["source_url"].lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            results.append(investor)

        print(f"  -> {len(investors)} investors")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(results)} African/Tunisian investors to {output_file}")

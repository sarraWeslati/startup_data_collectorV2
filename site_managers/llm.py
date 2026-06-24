from openai import OpenAI
import json

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_API_KEY"
)

SYSTEM_PROMPT = """
You are a precise data extraction engine for startup/news articles.

Return ONLY valid JSON.

Rules:
- startup_name must be real (not generic words like "Après", "C’est")
- entities must be real organizations, companies, people, products
- remove noise words
- ignore numbers that are not meaningful
- funding must include amount + currency if possible
- if unknown, return null

Output format:
{
  "startup_name": "",
  "year": "",
  "funding": [
    {"amount": "", "currency": ""}
  ],
  "entities": [],
  "summary": ""
}
"""


def llm_extract(url: str, title: str, text: str):

    # 🧠 token control (VERY IMPORTANT)
    text = text[:1800]

    prompt = f"""
URL: {url}
TITLE: {title}

CONTENT:
{text}

Extract structured data.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print("LLM ERROR:", e)
        return None
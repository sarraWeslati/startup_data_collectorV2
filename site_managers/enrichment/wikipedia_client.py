import requests
import urllib.parse


def get_wikipedia_summary(name: str):
    if not name:
        return {}

    try:
        # encode name (important pour Autoliv, AI etc.)
        title = urllib.parse.quote(name)

        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return {}

        data = r.json()

        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "summary": data.get("extract", ""),
            "wiki_url": data.get("content_urls", {})
            .get("desktop", {})
            .get("page", "")
        }

    except Exception as e:
        print("[WIKI ERROR]", e)
        return {}
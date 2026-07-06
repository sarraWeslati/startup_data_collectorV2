import time
import requests
import xml.etree.ElementTree as ET


def get_wamda_urls(limit=200):
    url = "https://www.wamda.com/sitemap.xml"

    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    except Exception as exc:
        print(f"Wamda sitemap error: {exc}")
        return []

    root = ET.fromstring(r.content)

    urls = []
    seen = set()

    for elem in root.iter():
        if "loc" not in elem.tag:
            continue

        link = (elem.text or "").strip()
        if not link or link in seen:
            continue

        lower_link = link.lower()
        if any(token in lower_link for token in ["/startup", "/startups", "/investor", "/investors", "/news", "/article"]):
            urls.append(link)
            seen.add(link)

        if len(urls) >= limit:
            break

    time.sleep(1)
    return urls
# main.py

import asyncio
from datetime import datetime

from utils.url_loader import load_urls
from collectors.website_collector import scrape_url
from storage.file_storage import save_raw_content

async def process_url(url: str) -> dict:
    """
    Traite une URL :
    - scraping
    - sauvegarde
    - retour du résultat
    """

    try:

        print("\n" + "=" * 80)
        print(f"[START] {url}")

        content = await scrape_url(url)

        if not content:

            print("[WARNING] Aucun contenu récupéré")

            return {
                "url": url,
                "status": "empty",
                "content_length": 0
            }

        save_raw_content(
            url=url,
            content=content
        )

        print(
            f"[SUCCESS] {len(content)} caractères sauvegardés"
        )

        return {
            "url": url,
            "status": "success",
            "content_length": len(content)
        }

    except Exception as e:

        print(
            f"[ERROR] {url} -> {str(e)}"
        )

        return {
            "url": url,
            "status": "error",
            "error": str(e)
        }


async def main():

    print("\n")
    print("=" * 80)
    print("MULTI SOURCE DATA COLLECTOR")
    print("=" * 80)

    start_time = datetime.now()

    urls = load_urls(
        "data/sources.txt"
    )

    print(f"\n{len(urls)} URL(s) trouvée(s)\n")

    results = []

    for url in urls:

        result = await process_url(url)

        results.append(result)

    # -------------------------
    # Rapport final
    # -------------------------

    success_count = len(
        [
            r for r in results
            if r["status"] == "success"
        ]
    )

    error_count = len(
        [
            r for r in results
            if r["status"] == "error"
        ]
    )

    empty_count = len(
        [
            r for r in results
            if r["status"] == "empty"
        ]
    )

    elapsed = (
        datetime.now() - start_time
    ).total_seconds()

    print("\n")
    print("=" * 80)
    print("RAPPORT FINAL")
    print("=" * 80)

    print(f"Total URLs     : {len(results)}")
    print(f"Succès         : {success_count}")
    print(f"Erreurs        : {error_count}")
    print(f"Pages vides    : {empty_count}")
    print(f"Temps total    : {elapsed:.2f}s")

    print("\nDétails :\n")

    for result in results:

        if result["status"] == "success":

            print(
                f"[OK] "
                f"{result['url']} "
                f"({result['content_length']} caractères)"
            )

        elif result["status"] == "empty":

            print(
                f"[EMPTY] "
                f"{result['url']}"
            )

        else:

            print(
                f"[ERROR] "
                f"{result['url']} "
                f"-> {result['error']}"
            )

    print("\nFin du scraping.\n")


if __name__ == "__main__":
    asyncio.run(main())
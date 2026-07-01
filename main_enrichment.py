# main_enrichment.py

import asyncio
import json
import traceback

from pathlib import Path
from datetime import datetime

from enrichment.startup_enricher import (
    enrich_startup
)

from enrichment.investor_enricher import (
    enrich_investor
)


EXTRACTED_DIR = Path(
    "storage/extracted"
)

ENRICHED_DIR = Path(
    "storage/enriched"
)


def load_json(
    filepath: Path
):

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_json(
    data: dict,
    filepath: Path
):

    filepath.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


async def process_file(
    filepath: Path
) -> bool:

    print("\n" + "=" * 80)
    print(f"[FILE] {filepath.name}")

    try:

        data = load_json(
            filepath
        )

        entity_type = data.get(
            "entity_type",
            ""
        )

        print(
            f"[TYPE] {entity_type}"
        )

        # ==================================
        # STARTUP
        # ==================================

        if entity_type == "startup":

            enriched_data = (
                await enrich_startup(
                    data
                )
            )

        # ==================================
        # INVESTOR
        # ==================================

        elif entity_type in [
            "investor",
            "venture_capital_fund"
        ]:

            enriched_data = (
                await enrich_investor(
                    data
                )
            )

        # ==================================
        # SKIP
        # ==================================

        else:

            print(
                f"[SKIPPED] {entity_type}"
            )

            return False

        relative_path = (
            filepath.relative_to(
                EXTRACTED_DIR
            )
        )

        output_path = (
            ENRICHED_DIR /
            relative_path
        )

        save_json(
            enriched_data,
            output_path
        )

        print(
            f"[SAVED] {output_path}"
        )

        return True

    except Exception:

        print(
            f"[ERROR] {filepath.name}"
        )

        traceback.print_exc()

        return False


async def main():

    print("\n")
    print("=" * 80)
    print("DATA ENRICHMENT PIPELINE")
    print("=" * 80)

    start_time = datetime.now()

    if not EXTRACTED_DIR.exists():

        print(
            "storage/extracted not found"
        )

        return

    json_files = list(
        EXTRACTED_DIR.rglob(
            "*.json"
        )
    )

    print(
        f"\n{len(json_files)} fichier(s) trouvé(s)\n"
    )

    success_count = 0
    failed_count = 0

    for filepath in json_files:

        success = await process_file(
            filepath
        )

        if success:

            success_count += 1

        else:

            failed_count += 1

    elapsed = (
        datetime.now() - start_time
    ).total_seconds()

    print("\n")
    print("=" * 80)
    print("ENRICHMENT REPORT")
    print("=" * 80)

    print(
        f"Files processed : {len(json_files)}"
    )

    print(
        f"Success         : {success_count}"
    )

    print(
        f"Failed/Skipped  : {failed_count}"
    )

    print(
        f"Duration        : {elapsed:.2f}s"
    )

    print("\nDone.\n")


if __name__ == "__main__":

    asyncio.run(
        main()
    )

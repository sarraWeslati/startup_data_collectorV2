# main_investor_enrichment.py

import asyncio
import json
import traceback

from pathlib import Path
from datetime import datetime

from enrichment.investor_enricher import (
    enrich_investor
)

from utils.entity_loader import (
    load_best_entity
)

from utils.entity_merger import (
    merge_entities
)


EXTRACTED_DIR = Path(
    "storage/extracted/investors"
)

ENRICHED_DIR = Path(
    "storage/enriched/investors"
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

        # ==================================
        # Load extracted entity
        # ==================================

        extracted_data = load_json(
            filepath
        )

        entity_type = extracted_data.get(
            "entity_type",
            ""
        )

        if entity_type not in [
            "investor",
            "venture_capital_fund"
        ]:

            print(
                f"[SKIPPED] {entity_type}"
            )

            return False

        # ==================================
        # Load best available version
        # ==================================

        data = load_best_entity(
            filepath,
            extracted_data
        )

        print(
            f"[TYPE] {entity_type}"
        )

        # ==================================
        # Merge extracted data with existing
        # enriched entity
        # ==================================

        data = merge_entities(
            data,
            extracted_data
        )

        # ==================================
        # INVESTOR ENRICHMENT
        # ==================================

        enriched_data = await enrich_investor(
            data
        )

        relative_path = filepath.relative_to(
            EXTRACTED_DIR
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
    print("INVESTOR ENRICHMENT")
    print("=" * 80)

    start_time = datetime.now()

    if not EXTRACTED_DIR.exists():

        print(
            "storage/extracted/investors not found"
        )

        return

    json_files = list(
        EXTRACTED_DIR.rglob(
            "*.json"
        )
    )

    print(
        f"\n{len(json_files)} investor(s) trouvé(s)\n"
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
    print("INVESTOR ENRICHMENT REPORT")
    print("=" * 80)

    print(
        f"Files processed : {len(json_files)}"
    )

    print(
        f"Success         : {success_count}"
    )

    print(
        f"Failed          : {failed_count}"
    )

    print(
        f"Duration        : {elapsed:.2f}s"
    )

    print("\nDone.\n")


if __name__ == "__main__":

    asyncio.run(
        main()
    )
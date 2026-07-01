import json
import re
from pathlib import Path


# =====================================================
# PATHS
# =====================================================

INPUT_FILE = Path("csvBDD/startupsCSV.json")

EXTRACTED_DIR = Path("storage/extracted/startups")
ENRICHED_DIR = Path("storage/enriched/startups")


# =====================================================
# HELPERS
# =====================================================

def slugify(name: str) -> str:
    """
    Convertit le nom d'une startup en nom de fichier.
    """

    if not name:
        return "unknown"

    name = name.lower().strip()

    name = re.sub(r"[^\w\s-]", "", name)

    name = re.sub(r"[\s-]+", "_", name)

    name = re.sub(r"_+", "_", name)

    return name


def load_json(path: Path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_json(
    path: Path,
    data: dict
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


# =====================================================
# MAIN
# =====================================================

def main():

    if not INPUT_FILE.exists():

        print(f"[ERROR] {INPUT_FILE} introuvable.")

        return

    EXTRACTED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ENRICHED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    startups = load_json(INPUT_FILE)

    created = 0
    skipped = 0
    errors = 0

    print("\n")
    print("=" * 80)
    print("PREPARE STARTUP ENRICHMENT")
    print("=" * 80)

    for startup in startups:

        try:

            name = startup.get(
                "name",
                ""
            ).strip()

            if not name:

                print("[WARNING] Startup sans nom ignorée.")

                errors += 1

                continue

            filename = slugify(name) + ".json"

            extracted_file = (
                EXTRACTED_DIR / filename
            )

            enriched_file = (
                ENRICHED_DIR / filename
            )

            extracted_created = False
            enriched_created = False

            # ---------------------------------
            # storage/extracted
            # ---------------------------------

            if not extracted_file.exists():

                save_json(
                    extracted_file,
                    startup
                )

                extracted_created = True

            # ---------------------------------
            # storage/enriched
            # ---------------------------------

            if not enriched_file.exists():

                save_json(
                    enriched_file,
                    startup
                )

                enriched_created = True

            # ---------------------------------

            if extracted_created or enriched_created:

                print(f"✅ {name}")

                created += 1

            else:

                print(f"⏩ {name}")

                skipped += 1

        except Exception as e:

            print(
                f"❌ {startup.get('name', 'Unknown')} : {e}"
            )

            errors += 1

    print("\n")
    print("=" * 80)
    print("REPORT")
    print("=" * 80)

    print(f"Total startups : {len(startups)}")
    print(f"Created        : {created}")
    print(f"Skipped        : {skipped}")
    print(f"Errors         : {errors}")

    print("\nDone.\n")


if __name__ == "__main__":
    main()
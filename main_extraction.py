from pathlib import Path
from datetime import datetime

from extractors.entity_detector import detect_entity_type
from extractors.startup_extractor import extract_startup
from extractors.investor_extractor import extract_investor

from extractors.chunked_startup_directory_extractor import (
    extract_startup_directory_chunked
)

from extractors.chunked_investor_directory_extractor import (
    extract_investor_directory_chunked
)

from extractors.entity_splitter import (
    save_directory_result
)

from extractors.accelerator_extractor import (extract_accelerator)
from extractors.incubator_extractor import (extract_incubator)

from extractors.support_organization_extractor import extract_support_organization
from storage.entity_storage import save_entity

RAW_FOLDER = Path("storage/raw")


def read_markdown_file(filepath: Path) -> str:

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()


def process_file(filepath: Path):

    print("\n" + "=" * 80)
    print(f"[FILE] {filepath.name}")

    try:

        content = read_markdown_file(filepath)

        if not content.strip():

            print("[WARNING] Empty file")

            return False

        print(
            f"[CONTENT] {len(content)} caractères"
        )

        # -----------------------------------
        # Entity Detection
        # -----------------------------------

        detection = detect_entity_type(content)

        entity_type = detection.get(
            "entity_type",
            "other"
        )

        confidence = detection.get(
            "confidence",
            0
        )

        print(
            f"[DETECTED] {entity_type}"
        )

        print(
            f"[CONFIDENCE] {confidence}"
        )

        # -----------------------------------
        # STARTUP
        # -----------------------------------

        if entity_type == "startup":

            entity = extract_startup(content)

            save_entity(entity)

            print(
                "[SAVED] Startup"
            )

            return True

        # -----------------------------------
        # INVESTOR
        # -----------------------------------

        elif entity_type in [
            "investor",
            "venture_capital_fund"
        ]:

            entity = extract_investor(content)

            save_entity(entity)

            print(
                "[SAVED] Investor"
            )

            return True

        # -----------------------------------
        # STARTUP DIRECTORY
        # -----------------------------------

        elif entity_type == "startup_directory":

            directory_result = (
                extract_startup_directory_chunked(
                    content
                )
            )

            print("\n" + "=" * 80)
            print("[DIRECTORY RESULT]")
            print("=" * 80)
            print(directory_result)
            print("=" * 80 )

            files = save_directory_result(
                directory_result
            )

            print(
                f"[SAVED] {len(files)} startups"
            )

            return True
        
        # -----------------------------------
        # INVESTOR DIRECTORY
        # -----------------------------------

        elif entity_type == "investor_directory":

            directory_result = (
                extract_investor_directory_chunked(
                    content
                )
            )

            print("\n" + "=" * 80)
            print("[DIRECTORY RESULT]")
            print("=" * 80)
            print(directory_result)
            print("=" * 80)

            files = save_directory_result(
                directory_result
            )

            print(
                f"[SAVED] {len(files)} investors"
            )

            return True

        # -----------------------------------
        # SUPPORT ORGANIZATION
        # -----------------------------------

        elif entity_type == "support_organization":

            entity = extract_support_organization(
                content)

            save_entity(entity)
            print(
                "[SAVED] Support Organization")

            return True
        
        elif entity_type == "accelerator":

            entity = extract_accelerator(content)

            save_entity(entity)

            print(
                "[SAVED] Accelerator"
            )

            return True
        
        elif entity_type == "incubator":

            entity = extract_incubator(
                content
            )

            save_entity(entity)

            print(
                "[SAVED] Incubator"
            )

            return True

        # -----------------------------------
        # OTHER
        # -----------------------------------

        else:

            print(
                f"[SKIPPED] Unsupported type : {entity_type}"
            )

            return False

    except Exception as e:

        print(
            f"[ERROR] {filepath.name}"
        )

        print(str(e))

        return False

def count_extracted_entities():
    """
    Compte le nombre total d'entités extraites.
    """

    extracted_folder = Path("storage/extracted")

    startup_count = 0
    investor_count = 0

    startup_folder = extracted_folder / "startups"
    investor_folder = extracted_folder / "investors"

    if startup_folder.exists():

        startup_count = len(
            list(startup_folder.glob("*.json"))
        )

    if investor_folder.exists():

        investor_count = len(
            list(investor_folder.glob("*.json"))
        )

    return startup_count, investor_count


def main():

    print("\n")
    print("=" * 80)
    print("ENTITY EXTRACTION PIPELINE")
    print("=" * 80)

    start_time = datetime.now()

    if not RAW_FOLDER.exists():

        print(
            "storage/raw folder not found"
        )

        return

    markdown_files = list(
        RAW_FOLDER.glob("*.md")
    )

    print(
        f"\n{len(markdown_files)} fichier(s) trouvé(s)\n"
    )

    success_count = 0
    error_count = 0

    for filepath in markdown_files:

        success = process_file(
            filepath
        )

        if success:
            success_count += 1
        else:
            error_count += 1

    elapsed = (
        datetime.now() - start_time
    ).total_seconds()

    print("\n")
    print("=" * 80)
    print("EXTRACTION REPORT")
    print("=" * 80)

    print(
        f"Files processed : {len(markdown_files)}"
    )

    print(
        f"Success         : {success_count}"
    )

    print(
        f"Failed/Skipped  : {error_count}"
    )

    print(
        f"Duration        : {elapsed:.2f}s"
    )

    startup_count, investor_count = count_extracted_entities()

    print("\n")
    print("=" * 80)
    print("EXTRACTED ENTITIES")
    print("=" * 80)

    print(
        f"Total startups   : {startup_count}"
    )

    print(
        f"Total investors  : {investor_count}"
    )

    print(
        f"Total entities   : {startup_count + investor_count}"
    )

    print("\nDone.\n")


if __name__ == "__main__":
    main()

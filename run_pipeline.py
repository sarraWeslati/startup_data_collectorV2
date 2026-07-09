# run_pipeline.py

import subprocess
import sys
import time
from pathlib import Path


# =====================================================
# PROJECT ROOT
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parent

PYTHON = sys.executable


# =====================================================
# HELPERS
# =====================================================

def print_header(title: str):

    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)


def run_script(script_name: str):

    script = PROJECT_ROOT / script_name

    print_header(
        f"RUNNING : {script_name}"
    )

    start = time.time()

    try:

        subprocess.run(

            [PYTHON, str(script)],

            cwd=PROJECT_ROOT,

            check=True

        )

        elapsed = time.time() - start

        print(
            f"\n[SUCCESS] {script_name} ({elapsed:.2f}s)"
        )

    except subprocess.CalledProcessError as e:

        print(
            f"\n[FAILED] {script_name}"
        )

        raise e


def start_parallel(script_name: str):

    script = PROJECT_ROOT / script_name

    print(
        f"[START] {script_name}"
    )

    return subprocess.Popen(

        [PYTHON, str(script)],

        cwd=PROJECT_ROOT

    )


# =====================================================
# MAIN
# =====================================================

def main():

    pipeline_start = time.time()

    print_header(
        "DATA COLLECTION PIPELINE"
    )

    # ------------------------------------------
    # STEP 1
    # SCRAPING
    # ------------------------------------------

    run_script(
        "main.py"
    )

    # ------------------------------------------
    # STEP 2
    # EXTRACTION
    # ------------------------------------------

    run_script(
        "main_extraction.py"
    )

    # ------------------------------------------
    # STEP 3
    # ENRICHMENT
    # ------------------------------------------

    print_header(
        "PARALLEL ENRICHMENT"
    )

    startup_process = start_parallel(

        "main_startup_enrichment.py"

    )

    investor_process = start_parallel(

        "main_investor_enrichment.py"

    )

    startup_return = startup_process.wait()

    investor_return = investor_process.wait()

    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------

    total = time.time() - pipeline_start

    print("\n")
    print("=" * 80)
    print("PIPELINE FINISHED")
    print("=" * 80)

    print(
        f"Startup process  : {startup_return}"
    )

    print(
        f"Investor process : {investor_return}"
    )

    print(
        f"Total duration   : {total:.2f}s"
    )

    print("\nDone.\n")


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":

    main()
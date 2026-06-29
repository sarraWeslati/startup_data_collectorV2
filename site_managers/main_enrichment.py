import json
import asyncio
import time
from pathlib import Path

from enrichment.startup_enricher import enrich_startup
from enrichment.investor_enricher import enrich_investor

# =========================
# STORAGE
# =========================
Path("storage").mkdir(exist_ok=True)

STARTUPS_FILE = Path("storage/startups.json")
INVESTORS_FILE = Path("storage/investors.json")

OUT_STARTUPS = Path("storage/startups_enriched.json")
OUT_INVESTORS = Path("storage/investors_enriched.json")

# =========================
# CONFIG PERFORMANCE
# =========================
MAX_WORKERS = 10  # 🔥 increase speed
semaphore = asyncio.Semaphore(MAX_WORKERS)

# =========================
# LOAD / SAVE
# =========================
def load(p):
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

# =========================
# SAFE ENRICH FUNCTIONS
# =========================
async def safe_enrich_startup(item):
    async with semaphore:
        try:
            return await enrich_startup(item)
        except Exception as e:
            print(f"[STARTUP ERROR] {item.get('name')} -> {e}")
            return item

async def safe_enrich_investor(item):
    async with semaphore:
        try:
            return await enrich_investor(item)
        except Exception as e:
            print(f"[INVESTOR ERROR] {item.get('name')} -> {e}")
            return item

# =========================
# OPTIONAL: CHUNK PROCESSING (VERY IMPORTANT FOR SPEED)
# =========================
def chunk_list(data, size=20):
    for i in range(0, len(data), size):
        yield data[i:i+size]

# =========================
# PIPELINE
# =========================
async def process_startups(startups):
    results = []

    for chunk in chunk_list(startups, 20):
        tasks = [safe_enrich_startup(s) for s in chunk]

        enriched = await asyncio.gather(*tasks, return_exceptions=True)

        for item in enriched:
            if isinstance(item, Exception):
                continue
            results.append(item)

        print(f"✅ processed chunk: {len(results)}/{len(startups)}")

    return results


async def process_investors(investors):
    tasks = [safe_enrich_investor(i) for i in investors]
    return await asyncio.gather(*tasks, return_exceptions=True)

# =========================
# MAIN
# =========================
async def main():
    start_time = time.time()

    print("🔥 PIPELINE START")

    startups = load(STARTUPS_FILE)
    investors = load(INVESTORS_FILE)

    print(f"📊 Startups: {len(startups)}")
    print(f"📊 Investors: {len(investors)}")

    # =========================
    # ENRICHMENT
    # =========================
    startups_enriched = await process_startups(startups)
    investors_enriched = await process_investors(investors)

    # =========================
    # SAVE
    # =========================
    save(OUT_STARTUPS, startups_enriched)
    save(OUT_INVESTORS, investors_enriched)

    # =========================
    # TIME REPORT
    # =========================
    end_time = time.time()
    print("================================")
    print("✅ DONE")
    print(f"⏱ TIME: {round(end_time - start_time, 2)} sec")
    print("================================")


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    asyncio.run(main())
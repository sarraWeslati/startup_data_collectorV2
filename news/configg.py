from pathlib import Path


BASE_DIR = Path(__file__).parent


RAW_DIR = BASE_DIR 

MERGED_DIR = BASE_DIR 

CLEANED_DIR = BASE_DIR 


RAW_FILE = MERGED_DIR / "all_news_raw.json"

NORMALIZED_FILE = CLEANED_DIR / "news_normalized.json"

CLEAN_FILE = CLEANED_DIR / "news_clean.json"

FINAL_FILE = CLEANED_DIR / "news_final.json"

DOCUMENTS_FILE = CLEANED_DIR / "documents.json"



MERGED_DIR.mkdir(exist_ok=True)

CLEANED_DIR.mkdir(exist_ok=True)
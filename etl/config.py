# etl/config.py

from pathlib import Path


# =====================================================
# PROJECT
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# =====================================================
# STORAGE
# =====================================================

STORAGE_DIR = (
    PROJECT_ROOT /
    "storage"
)


# =====================================================
# INPUT
# =====================================================

ENRICHED_DIR = (
    STORAGE_DIR /
    "enriched"
)

STARTUPS_DIR = (
    ENRICHED_DIR /
    "startups"
)

INVESTORS_DIR = (
    ENRICHED_DIR /
    "investors"
)


# =====================================================
# ETL OUTPUT
# =====================================================

ETL_DIR = (
    PROJECT_ROOT /
    "etl"
)

TRANSFORMED_DIR = (
    ETL_DIR /
    "transformed"
)

VALIDATED_DIR = (
    ETL_DIR /
    "validated"
)

REJECTED_DIR = (
    ETL_DIR /
    "rejected"
)

DEDUPLICATED_DIR = (
    ETL_DIR /
    "deduplicated"
)

REPORTS_DIR = (
    ETL_DIR /
    "reports"
)


# =====================================================
# SUBDIRECTORIES
# =====================================================

TRANSFORMED_STARTUPS_DIR = (
    TRANSFORMED_DIR /
    "startups"
)

TRANSFORMED_INVESTORS_DIR = (
    TRANSFORMED_DIR /
    "investors"
)


VALIDATED_STARTUPS_DIR = (
    VALIDATED_DIR /
    "startups"
)

VALIDATED_INVESTORS_DIR = (
    VALIDATED_DIR /
    "investors"
)


REJECTED_STARTUPS_DIR = (
    REJECTED_DIR /
    "startups"
)

REJECTED_INVESTORS_DIR = (
    REJECTED_DIR /
    "investors"
)


DEDUPLICATED_STARTUPS_DIR = (
    DEDUPLICATED_DIR /
    "startups"
)

DEDUPLICATED_INVESTORS_DIR = (
    DEDUPLICATED_DIR /
    "investors"
)


# =====================================================
# MONGODB
# =====================================================

DATABASE_NAME = "startup_database"

STARTUPS_COLLECTION = "startups"

INVESTORS_COLLECTION = "investors"

NEWS_COLLECTION = "news"

MONGODB_URI = (
    "mongodb://localhost:27017/"
)

DATABASE_NAME = (
    "startup_database"
)

STARTUPS_COLLECTION = (
    "startups"
)

INVESTORS_COLLECTION = (
    "investors"
)

NEWS_COLLECTION = (
    "news"
)

# =====================================================
# JSON
# =====================================================

JSON_ENCODING = "utf-8"

JSON_INDENT = 4

JSON_ASCII = False
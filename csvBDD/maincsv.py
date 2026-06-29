import pandas as pd
import json
import re
from pathlib import Path


INPUT_CSV = "startupTunisia.csv"
OUTPUT_JSON = "startupsCSV.json"


def split_founders(founders_text):
    if not founders_text or pd.isna(founders_text):
        return []

    founders_text = str(founders_text).strip()

    founders = re.split(
        r'(?<=[a-zàâäéèêëîïôöùûü])(?=[A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜ])',
        founders_text
    )

    result = []

    for founder in founders:
        founder = founder.strip()

        if founder:
            result.append({
                "name": founder,
                "role": "",
                "linkedin": "",
                "bio": ""
            })

    return result


def clean_value(value):
    if pd.isna(value):
        return ""

    value = str(value).strip()

    if value.lower() in ["nan", "null", "none", "n.a.", "n/a"]:
        return ""

    return value


def create_startup(row):

    founders = split_founders(row.get("Founders"))

    emails = []
    email = clean_value(row.get("Courriel"))

    if email:
        emails.append(email)

    phones = []
    phone = clean_value(row.get("Téléphone"))

    if phone:
        phones.append(phone)

    website = clean_value(row.get("Site web"))

    startup = {
        "entity_type": "startup",

        "name": clean_value(row.get("Nom")),
        "description": clean_value(row.get("Résumé")),
        "tagline": "",

        "industry": clean_value(row.get("Secteur")),
        "keywords": [],

        "country": "",
        "city": "",
        "headquarters": "",

        "founded_year": clean_value(row.get("Année de création")),
        "startup_stage": "",

        "startup_label": bool(clean_value(row.get("Label Date"))),

        "website": website,
        "linkedin_url": "",

        "social_media": {
            "linkedin": "",
            "facebook": "",
            "instagram": "",
            "youtube": "",
            "github": ""
        },

        "contact": {
            "emails": emails,
            "phones": phones,
            "address": ""
        },

        "founders": founders,

        "leadership": [],

        "employee_count": None,
        "employee_range": "",
        "team_size": "",

        "products": [],
        "services": [],
        "technologies": [],

        "customer_segments": [],

        "target_market": "",

        "operating_countries": [],

        "languages_supported": [],

        "notable_customers": [],

        "partners": [],

        "accelerators": [],

        "incubators": [],

        "funding": {
            "total_raised": None,
            "currency": "",
            "stage": "",
            "rounds": []
        },

        "investors": [],

        "awards": [],
        "certifications": [],
        "patents": [],

        "business_metrics": {
            "users_count": None,
            "customers_count": None,
            "downloads": None,
            "monthly_transactions": None,
            "annual_revenue": None,
            "revenue_currency": ""
        },

        "recent_news": [],

        "events": [],

        "legal_info": {
            "company_type": "",
            "registration_number": ""
        },

        "extra_notes": "",

        "sources": [],

        "confidence": {
            "overall": 0.0,
            "description": 0.0,
            "founders": 0.0,
            "leadership": 0.0,
            "employees": 0.0,
            "funding": 0.0,
            "investors": 0.0,
            "products": 0.0,
            "technologies": 0.0
        },

        "enrichment": {
            "status": "csv_import",
            "sources_used": ["csv"],
            "collection_date": "",
            "last_updated": ""
        },

        "stats": {
            "has_website": bool(website),
            "has_linkedin": False,
            "founders_count": len(founders),
            "leadership_count": 0,
            "investors_count": 0,
            "products_count": 0,
            "services_count": 0,
            "technologies_count": 0,
            "news_count": 0
        },

        "others": {
            "logo": clean_value(row.get("Logo")),
            "label_date": clean_value(row.get("Label Date"))
        }
    }

    return startup


def main():

    csv_path = Path(INPUT_CSV)

    if not csv_path.exists():
        print(f"❌ Fichier introuvable : {INPUT_CSV}")
        return

    df = pd.read_csv(csv_path)

    startups = []

    for _, row in df.iterrows():
        startups.append(create_startup(row))

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(
            startups,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"✅ {len(startups)} startups exportées vers {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
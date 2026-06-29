# schemas/startup_schema.py

from copy import deepcopy


STARTUP_SCHEMA = {

    "entity_type": "startup",

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    "name": "",
    "description": "",
    "tagline": "",

    "industry": "",
    "sub_industry": "",
    "keywords": [],

    # =====================================================
    # LOCATION
    # =====================================================

    "country": "",
    "city": "",
    "headquarters": "",

    # =====================================================
    # COMPANY
    # =====================================================

    "founded_year": "",
    "startup_stage": "",
    "startup_label": False,

    "website": "",
    "linkedin_url": "",

    # =====================================================
    # SOCIAL MEDIA
    # =====================================================

    "social_media": {

        "linkedin": "",
        "facebook": "",
        "instagram": "",
        "twitter": "",
        "youtube": "",
        "github": ""
    },

    # =====================================================
    # CONTACT
    # =====================================================

    "contact": {

        "emails": [],
        "phones": [],
        "address": ""
    },

    # =====================================================
    # PEOPLE
    # =====================================================

    "founders": [],

    "leadership": [],

    # =====================================================
    # TEAM
    # =====================================================

    "employee_count": None,
    "employee_range": "",
    "team_size": "",

    # =====================================================
    # PRODUCTS
    # =====================================================

    "products": [],

    "services": [],

    "technologies": [],

    # =====================================================
    # MARKET
    # =====================================================

    "customer_segments": [],

    "target_market": "",

    "operating_countries": [],

    "languages_supported": [],

    "notable_customers": [],

    # =====================================================
    # ECOSYSTEM
    # =====================================================

    "partners": [],

    "accelerators": [],

    "incubators": [],

    # =====================================================
    # FUNDING
    # =====================================================

    "funding": {

        "total_raised": None,

        "currency": "",

        "stage": "",

        "rounds": []
    },

    "investors": [],

    # =====================================================
    # ACHIEVEMENTS
    # =====================================================

    "awards": [],

    "certifications": [],

    "patents": [],

    # =====================================================
    # BUSINESS METRICS
    # =====================================================

    "business_metrics": {

        "users_count": None,

        "customers_count": None,

        "downloads": None,

        "monthly_transactions": None,

        "annual_revenue": None,

        "revenue_currency": ""
    },

    # =====================================================
    # NEWS
    # =====================================================

    "recent_news": [],

    "events": [],

    # =====================================================
    # LEGAL
    # =====================================================

    "legal_info": {

        "company_type": "",

        "registration_number": ""
    },

    # =====================================================
    # NOTES
    # =====================================================

    "extra_notes": "",

    # =====================================================
    # SOURCES
    # =====================================================

    "sources": [],

    # =====================================================
    # CONFIDENCE
    # =====================================================

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

    # =====================================================
    # ENRICHMENT
    # =====================================================

    "enrichment": {

        "status": "pending",

        "sources_used": [],

        "collection_date": "",

        "last_updated": ""
    },

    # =====================================================
    # STATS
    # =====================================================

    "stats": {

        "has_website": False,

        "has_linkedin": False,

        "founders_count": 0,

        "leadership_count": 0,

        "investors_count": 0,

        "products_count": 0,

        "services_count": 0,

        "technologies_count": 0,

        "news_count": 0
    }
}


def get_empty_startup() -> dict:
    """
    Retourne une copie indépendante du schéma startup.
    """

    return deepcopy(STARTUP_SCHEMA)
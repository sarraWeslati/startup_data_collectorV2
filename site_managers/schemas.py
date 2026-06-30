from copy import deepcopy

STARTUP_TEMPLATE = {
    "entity_type": "startup",
    "name": "",
    "description": "",
    "tagline": "",
    "industry": "",
    "keywords": [],
    "country": "",
    "city": "",
    "headquarters": "",
    "founded_year": "",
    "startup_stage": "",
    "startup_label": False,
    "website": "",
    
    "social_media": {
        "linkedin": "",
        "facebook": "",
        "instagram": "",
        "youtube": "",
        "github": ""
    },
    "contact": {
        "emails": [],
        "phones": [],
        "address": ""
    },
    "founders": [],
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
    "funding": {},
    "investors": [],
    "awards": [],
    "certifications": [],
    "patents": [],
    "business_metrics": {},
    "recent_news": [],
    "events": [],
    "legal_info": {},
    "extra_notes": "",
    "sources": [],
    "confidence": {},
    "enrichment": {},
    "stats": {},
    "others": {}
}

INVESTOR_TEMPLATE = {
    "entity_type": "investor",
    "name": "",
    "description": "",
    "tagline": "",
    "investor_type": "",
    "country": "",
    "city": "",
    "headquarters": "",
    "founded_year": "",
    "website": "",
    "linkedin_url": "",
    "social_media": {},
    "contact": {},
    "leadership": [],
    "partners": [],
    "investment_focus": {},
    "geographic_focus": [],
    "investment_stages": [],
    "ticket_size": {},
    "assets_under_management": None,
    "funds": [],
    "portfolio": [],
    "successful_exits": [],
    "co_investors": [],
    "accelerator_programs": [],
    "incubator_programs": [],
    "awards": [],
    "certifications": [],
    "recent_investments": [],
    "recent_news": [],
    "extra_notes": "",
    "business_metrics": {},
    "sources": [],
    "confidence": {},
    "enrichment": {},
    "stats": {},
    "others": {}
}


def get_template(entity_type):
    if entity_type == "startup":
        return deepcopy(STARTUP_TEMPLATE)

    if entity_type == "investor":
        return deepcopy(INVESTOR_TEMPLATE)

    return {
        "entity_type": "other",
        "others": {}
    }
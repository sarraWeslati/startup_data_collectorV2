import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

REQUEST_TIMEOUT = 12
DISCOVERY_WORKERS = 8
PIPELINE_WORKERS = 4
MAX_LINKS_PER_SOURCE = 60
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", "0"))  # 0 = no limit

URLS = [
    # Tunisia / local ecosystem
    "https://smartcapital.tn/?page_id=428",
    "https://managers.tn/category/startup/",
    "https://managers.tn/category/banking/",
    "https://startup.gov.tn/en/news",
    "https://www.entreprises-magazine.com/category/startup/",
    "https://www.ilboursa.com/marches/actualites_bourse.aspx",
    "https://www.tustex.com/economie-actualites-economiques",
    "https://www.africanmanager.com/mots-cles/startup/",
    "https://kapitalis.com/tunisie/category/economie/",

    # Africa / MENA startup and investor news
    "https://disruptafrica.com/",
    "https://techcabal.com/",
    "https://techpoint.africa/",
    "https://benjamindada.com/",
    "https://weetracker.com/",
    "https://techmoran.com/",
    "https://techbuild.africa/",
    "https://ventureburn.com/",
    "https://www.wamda.com/news",
    "https://www.menabytes.com/startups/",
    "https://thebigdeal.substack.com/",
    "https://insights.techcabal.com/insights/",
    "https://partechpartners.com/africa-reports/2025-africa-tech-venture-capital-report",
    "https://www.avca.africa/news-insights/member-news/",
    "https://africa.businessinsider.com/",
    "https://www.africanews.com/business/",
]

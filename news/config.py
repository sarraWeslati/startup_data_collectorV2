import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

URLS = [
    # existing
    "https://smartcapital.tn/?page_id=428",
    "https://thebigdeal.substack.com/",
    "https://managers.tn/category/startup/",
    "https://managers.tn/category/banking/",
    "https://insights.techcabal.com/insights/",
    "https://disruptafrica.com/",
    "https://www.wamda.com/news",
    "https://startup.gov.tn/en/news",
    "https://partechpartners.com/africa-reports/2025-africa-tech-venture-capital-report",
    "https://www.avca.africa/news-insights/member-news/",

    # 🔥 NEW AFRICA SOURCES
    "https://techpoint.africa/",
    "https://techcabal.com/",
    "https://ventureburn.com/",
    "https://africa.businessinsider.com/",
    "https://www.africanews.com/business/",

    # 🔥 TUNISIA EXTRA
    "https://www.ilboursa.com/",
    "https://www.tustex.com/",
    "https://www.entreprises-magazine.com/"
]
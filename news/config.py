import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

REQUEST_TIMEOUT = 15
DISCOVERY_WORKERS = 10
PIPELINE_WORKERS = 8
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))

MAX_LINKS_PER_SOURCE = int(os.getenv("MAX_LINKS_PER_SOURCE", "0"))
MAX_PAGES_PER_SOURCE = int(os.getenv("MAX_PAGES_PER_SOURCE", "0"))
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", "0"))


URLS = [
    # 🇹🇳 Tunisia
    "https://startup.gov.tn/en/news",
    "https://www.entreprises-magazine.com",
    
    
    "https://www.ilboursa.com",
    "https://www.tustex.com",

    # 🌍 Africa / MENA
    "https://disruptafrica.com",
    "https://techcabal.com",
    "https://techpoint.africa",
    "https://weetracker.com",
    "https://techmoran.com",
    "https://techbuild.africa",
    "https://ventureburn.com",
    "https://www.wamda.com/news",
    "https://www.menabytes.com/startups",
    "https://www.wamda.com/"
]

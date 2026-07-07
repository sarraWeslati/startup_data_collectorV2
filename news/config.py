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
   
    "https://www.wamda.com/news"
]

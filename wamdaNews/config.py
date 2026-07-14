import os
from dotenv import load_dotenv


# ============================
# LOAD ENV
# ============================

load_dotenv()


# ============================
# WAMDA
# ============================

BASE_URL = "https://www.wamda.com"

WAMDA_NEWS_URL = (
    "https://www.wamda.com/news"
)

MAX_PAGES = 30

MAX_LINKS_PER_PAGE = 20



# ============================
# NVIDIA LLM
# ============================

NVIDIA_API_KEY = os.getenv(
    "NVIDIA_API_KEY"
)


if not NVIDIA_API_KEY:

    raise Exception(
        "❌ NVIDIA_API_KEY introuvable dans .env"
    )


print(
    "✅ NVIDIA KEY:",
    NVIDIA_API_KEY[:15] + "********"
)



NVIDIA_URL = (

    "https://integrate.api.nvidia.com/v1/chat/completions"

)


NVIDIA_MODEL = (

    "meta/llama-3.1-8b-instruct"

)


LLM_TIMEOUT = 120


MAX_TOKENS = 2500



# ============================
# OUTPUT
# ============================

OUTPUT_FILE = "news.json"



# ============================
# CATEGORIES
# ============================

VALID_CATEGORIES = [

    "startup",

    "funding",

    "investment",

    "investor",

    "acquisition",

    "report"

]



# ============================
# AFRICA KEYWORDS
# ============================

AFRICA_KEYWORDS = [

    "africa",

    "african",

    "tunisia",

    "tunisian",

    "egypt",

    "egyptian",

    "morocco",

    "moroccan",

    "algeria",

    "algerian",

    "nigeria",

    "nigerian",

    "kenya",

    "kenyan",

    "ghana",

    "senegal",

    "south africa",

    "rwanda",

    "ethiopia",

    "uganda",

    "cameroon",

    "ivory coast",

    "côte d'ivoire",

    "sub saharan",

    "pan african"

]



# ============================
# MENA KEYWORDS
# ============================

MENA_KEYWORDS = [

    "mena",

    "middle east",

    "uae",

    "dubai",

    "abu dhabi",

    "saudi",

    "riyadh",

    "qatar",

    "kuwait",

    "bahrain",

    "jordan",

    "lebanon",

    "oman",

    "gcc",

    "gulf",

    "israel"

]



# ============================
# STARTUP KEYWORDS
# ============================

STARTUP_KEYWORDS = [

    "startup",

    "startups",

    "founder",

    "founders",

    "entrepreneur",

    "entrepreneurship",

    "funding",

    "funded",

    "raised",

    "raises",

    "investment",

    "investor",

    "venture capital",

    "venture",

    "vc",

    "seed",

    "pre-seed",

    "series a",

    "series b",

    "series c",

    "series d",

    "million",

    "billion",

    "accelerator",

    "incubator",

    "innovation"

]
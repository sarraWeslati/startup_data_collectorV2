import threading
import time
import requests
from urllib.parse import urlparse
from config import REQUEST_TIMEOUT

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
}

thread_local = threading.local()
domain_locks = {}
lock = threading.Lock()


def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")


def get_lock(domain):
    with lock:
        if domain not in domain_locks:
            domain_locks[domain] = threading.Lock()
        return domain_locks[domain]


def get_session():
    if not hasattr(thread_local, "session"):
        s = requests.Session()
        s.headers.update(BROWSER_HEADERS)
        thread_local.session = s
    return thread_local.session


def fetch(url):
    session = get_session()

    try:
        r = session.get(
            url,
            timeout=(5, REQUEST_TIMEOUT)  # 🔥 CONNECT + READ timeout
        )

        if r.status_code in [403, 429, 500, 502, 503]:
            return None  # 🚀 skip direct

        r.raise_for_status()
        return r.text

    except:
        return None  # 🚀 NEVER block
def get_html(url):
    return fetch(url)
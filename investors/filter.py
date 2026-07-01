KEYWORDS = [
    "investor", "investment", "vc", "capital",
    "fund", "portfolio", "startup", "deal",
    "accelerator", "angel", "partners"
]


def is_investor_page(name, url):

    text = (name + " " + url).lower()

    return any(k in text for k in KEYWORDS)
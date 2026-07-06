def classify(text):

    text = text.lower()

    investor_kw = [
        "investor", "vc", "venture", "fund",
        "capital", "angel", "private equity"
    ]

    startup_kw = [
        "startup", "raised", "seed", "series a",
        "series b", "founder", "launched"
    ]

    news_kw = [
        "announced", "according", "report", "market"
    ]

    if any(k in text for k in investor_kw):
        return "investor"

    if any(k in text for k in startup_kw):
        return "startup"

    return "news"
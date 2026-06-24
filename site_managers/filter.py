def is_important_article(title: str, content: str) -> bool:

    keywords = [
        "startup", "levée", "million", "milliard",
        "funding", "investment", "investisseur",
        "financement", "AI", "fintech",
        "bank", "bourse", "croissance",
        "Tunisie", "Africa"
    ]

    text = (title + " " + content).lower()

    score = sum(1 for k in keywords if k.lower() in text)

    # 🔥 seuil intelligent (ajustable)
    return score >= 2
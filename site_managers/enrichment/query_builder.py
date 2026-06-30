def is_empty(v):
    return v in (None, "", [], {}, 0)


def get_missing_fields(entity: dict):
    """
    Detect missing useful fields
    """
    important_fields = [
        "website",
        "linkedin",
        "industry",
        "description",
        "founders",
        "funding",
        "headquarters",
        "products",
        "social_media"
    ]

    missing = []

    for f in important_fields:
        if is_empty(entity.get(f)):
            missing.append(f)

    return missing


def build_smart_query(entity: dict, entity_type: str = "startup") -> str:

    name = entity.get("name", "").strip()

    if not name:
        return ""

    missing = get_missing_fields(entity)

    base = [name]

    # =====================
    # TYPE BOOST
    # =====================
    if entity_type == "startup":
        base += [
            "startup company",
            "founders CEO funding investors website"
        ]
    else:
        base += [
            "venture capital investor fund portfolio companies"
        ]

    # =====================
    # SMART MISSING BOOST
    # =====================
    if "website" in missing:
        base.append("official website")

    if "linkedin" in missing:
        base.append("linkedin profile")

    if "industry" in missing:
        base.append("industry sector")

    if "funding" in missing:
        base.append("funding rounds raised")

    if "founders" in missing:
        base.append("founders CEO team")

    if "description" in missing:
        base.append("what does company do")

    # =====================
    # SEO BOOST (IMPORTANT)
    # =====================
    base.append(
        "site:crunchbase.com OR site:linkedin.com OR site:techcrunch.com"
    )

    return " ".join(base)
def build_multi_queries(name: str, entity_type="startup"):

    if not name:
        return []

    name = name.strip()

    return [
        f"{name} company overview",
        f"{name} startup what does it do",
        f"{name} founders CEO",
        f"{name} funding investors",
        f"{name} official website"
    ]

    if not name:
        return []

    name = name.strip()

    base = [
        f"{name}",
        f"{name} company",
        f"{name} startup",
        f"{name} what is it",
        f"{name} founders",
        f"{name} funding",
        f"{name} official website"
    ]

    if entity_type == "investor":
        base += [
            f"{name} VC",
            f"{name} portfolio",
            f"{name} investments"
        ]

    # 🔥 IMPORTANT: LIMIT TO AVOID 400 + RATE LIMIT
    return base[:4]
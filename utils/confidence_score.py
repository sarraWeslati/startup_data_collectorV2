from typing import Dict


def compute_confidence_score(
    entity: Dict
) -> Dict:
    """
    Calcule un score de confiance
    de l'entité enrichie.
    """

    score = 0

    # ===========================
    # Identity
    # ===========================

    if entity.get("name"):
        score += 10

    if entity.get("description"):
        score += 10

    # ===========================
    # Location
    # ===========================

    if entity.get("country"):
        score += 8

    if entity.get("city"):
        score += 5

    # ===========================
    # Website
    # ===========================

    if entity.get("website"):
        score += 15

    # ===========================
    # LinkedIn
    # ===========================

    if entity.get("linkedin"):
        score += 10

    # ===========================
    # Contacts
    # ===========================

    if entity.get("emails"):
        score += 8

    if entity.get("phones"):
        score += 8

    # ===========================
    # Team
    # ===========================

    if entity.get("founders"):
        score += 8

    if entity.get("team_members"):
        score += 5

    # ===========================
    # Business
    # ===========================

    if entity.get("products"):
        score += 4

    if entity.get("services"):
        score += 4

    if entity.get("technologies"):
        score += 4

    if entity.get("partners"):
        score += 3

    # ===========================
    # Metadata
    # ===========================

    enrichment = entity.get(
        "enrichment",
        {}
    )

    if enrichment.get(
        "website_enriched"
    ):
        score += 4

    if enrichment.get(
        "llm_enriched"
    ):
        score += 2

    if enrichment.get(
        "tavily_results",
        0
    ) > 0:
        score += 4

    score = min(
        score,
        100
    )

    if score >= 85:
        level = "High"

    elif score >= 60:
        level = "Medium"

    else:
        level = "Low"

    return {

        "score": score,

        "level": level
    }
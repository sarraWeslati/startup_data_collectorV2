from typing import Dict

from utils.url_normalizer import normalize_website

import json


def normalize_list(values):
    """
    Nettoie une liste en supprimant les doublons.

    Compatible avec :
    - chaînes
    - nombres
    - dictionnaires
    - listes
    """

    if not isinstance(values, list):
        return []

    unique = []
    seen = set()

    for value in values:

        if value in ("", None, [], {}):
            continue

        if isinstance(value, str):
            value = value.strip()

        # Cas dictionnaire
        if isinstance(value, dict):

            key = json.dumps(
                value,
                sort_keys=True,
                ensure_ascii=False
            )

        # Cas liste
        elif isinstance(value, list):

            key = json.dumps(
                value,
                sort_keys=True,
                ensure_ascii=False
            )

        else:

            key = str(value)

        if key not in seen:

            seen.add(key)

            unique.append(value)

    return unique


def normalize_social_media(
    social_media: Dict
) -> Dict:

    if not isinstance(
        social_media,
        dict
    ):
        return {}

    return {

        "linkedin":
        social_media.get(
            "linkedin",
            ""
        ),

        "facebook":
        social_media.get(
            "facebook",
            ""
        ),

        "twitter":
        social_media.get(
            "twitter",
            ""
        ),

        "instagram":
        social_media.get(
            "instagram",
            ""
        ),

        "youtube":
        social_media.get(
            "youtube",
            ""
        ),

        "github":
        social_media.get(
            "github",
            ""
        )
    }


def normalize_investor(
    investor: Dict
) -> Dict:
    """
    Normalise complètement
    un investisseur.
    """

    investor["website"] = normalize_website(
        investor.get(
            "website",
            ""
        )
    )

    if investor.get(
        "linkedin"
    ):
        investor["linkedin"] = investor[
            "linkedin"
        ].strip()

    investor["emails"] = normalize_list(
        investor.get(
            "emails",
            []
        )
    )

    investor["phones"] = normalize_list(
        investor.get(
            "phones",
            []
        )
    )

    investor["investment_focus"] = normalize_list(
        investor.get(
            "investment_focus",
            []
        )
    )

    investor["investment_stages"] = normalize_list(
        investor.get(
            "investment_stages",
            []
        )
    )

    investor["preferred_industries"] = normalize_list(
        investor.get(
            "preferred_industries",
            []
        )
    )

    investor["geographic_focus"] = normalize_list(
        investor.get(
            "geographic_focus",
            []
        )
    )

    investor["portfolio_startups"] = normalize_list(
        investor.get(
            "portfolio_startups",
            []
        )
    )

    investor["partners"] = normalize_list(
        investor.get(
            "partners",
            []
        )
    )

    investor["team_members"] = normalize_list(
        investor.get(
            "team_members",
            []
        )
    )

    investor["co_investors"] = normalize_list(
        investor.get(
            "co_investors",
            []
        )
    )

    investor["awards"] = normalize_list(
        investor.get(
            "awards",
            []
        )
    )

    investor["certifications"] = normalize_list(
        investor.get(
            "certifications",
            []
        )
    )

    investor["recent_news"] = normalize_list(
        investor.get(
            "recent_news",
            []
        )
    )

    investor["events"] = normalize_list(
        investor.get(
            "events",
            []
        )
    )

    investor["social_media"] = normalize_social_media(
        investor.get(
            "social_media",
            {}
        )
    )

    return investor
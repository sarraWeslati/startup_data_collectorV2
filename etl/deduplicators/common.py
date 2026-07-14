# etl/deduplicators/common.py

from typing import Dict

from utils.entity_merger import (
    merge_entities
)

from utils.company_matching import (
    is_matching_company
)

from utils.url_normalizer import (
    get_domain
)


# =====================================================
# SAME WEBSITE
# =====================================================

def same_website(
    entity1: Dict,
    entity2: Dict
) -> bool:

    website1 = entity1.get(
        "website",
        ""
    )

    website2 = entity2.get(
        "website",
        ""
    )

    if not website1 or not website2:

        return False

    return get_domain(
        website1
    ) == get_domain(
        website2
    )


# =====================================================
# SAME NAME
# =====================================================

def same_name(
    entity1: Dict,
    entity2: Dict
) -> bool:

    return is_matching_company(

        entity1.get(
            "name",
            ""
        ),

        entity2.get(
            "website",
            ""
        )

    ) or is_matching_company(

        entity2.get(
            "name",
            ""
        ),

        entity1.get(
            "website",
            ""
        )

    )


# =====================================================
# DUPLICATE
# =====================================================

def is_duplicate(
    entity1: Dict,
    entity2: Dict
) -> bool:

    if same_website(
        entity1,
        entity2
    ):

        return True

    if same_name(
        entity1,
        entity2
    ):

        return True

    return False


# =====================================================
# MERGE
# =====================================================

def merge_duplicate(
    entity1: Dict,
    entity2: Dict
) -> Dict:

    return merge_entities(

        entity1,

        entity2

    )
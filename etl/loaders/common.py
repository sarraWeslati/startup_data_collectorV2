# etl/loaders/common.py

from typing import Dict

from pymongo.collection import Collection

from utils.url_normalizer import (
    get_domain
)


# =====================================================
# BUILD FILTER
# =====================================================

def build_filter(
    entity: Dict
) -> Dict:
    """
    Construit le filtre MongoDB permettant
    d'identifier une entité existante.
    """

    normalized_name = entity.get(
        "normalized_name"
    )

    website = entity.get(
        "website"
    )

    if website:

        domain = get_domain(
            website
        )

    else:

        domain = None

    query = {}

    if normalized_name:

        query["normalized_name"] = (
            normalized_name
        )

    if domain:

        query["website_domain"] = (
            domain
        )

    return query


# =====================================================
# UPSERT
# =====================================================

def upsert_entity(
    collection: Collection,
    entity: Dict
) -> str:
    """
    Insère ou met à jour une entité.

    Retourne :

        inserted

        updated

        skipped
    """

    query = build_filter(
        entity
    )

    print("\n--------------------------------")

    print(
        f"Entity : {entity.get('name')}"
    )

    print(
        f"Query : {query}"
    )

    if not query:

        return "skipped"

    # -----------------------------------------
    # Store normalized website domain
    # -----------------------------------------

    domain = get_domain(

        entity.get(
            "website",
            ""
        )

    )

    if domain:

        entity["website_domain"] = domain

    # -----------------------------------------
    # MongoDB upsert
    # -----------------------------------------

    print(
        f"Loading : {entity.get('name')}"
    )

    print(
        f"Mongo filter : {query}"
    )

    result = collection.update_one(

        

        query,

        {

            "$set": entity

        },

        upsert=True

    )

    if result.upserted_id:

        return "inserted"

    if result.modified_count:

        return "updated"

    return "skipped"
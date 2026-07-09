from typing import Dict

from search.search_router import (
    search
)


# =====================================================
# GENERIC SEARCH
# =====================================================

def search_web(
    query: str,
    max_results: int = 10,
    search_depth: str = "advanced",
    topic: str = "general"
) -> Dict:
    """
    Generic web search.
    """

    return search(

        query=query,

        max_results=max_results,

        search_depth=search_depth,

        topic=topic

    )


# =====================================================
# COMPANY SEARCH
# =====================================================

def search_company(
    company_name: str,
    max_results: int = 10
) -> Dict:
    """
    Search information about a company.
    """

    return search(

        query=company_name,

        max_results=max_results,

        search_depth="advanced",

        topic="general"

    )


# =====================================================
# STARTUP SEARCH
# =====================================================

def search_startup(
    startup_name: str,
    max_results: int = 10
) -> Dict:
    """
    Search information about a startup.
    """

    return search(

        query=startup_name,

        max_results=max_results,

        search_depth="advanced",

        topic="general"

    )


# =====================================================
# INVESTOR SEARCH
# =====================================================

def search_investor(
    investor_name: str,
    max_results: int = 10
) -> Dict:
    """
    Search information about an investor.
    """

    return search(

        query=investor_name,

        max_results=max_results,

        search_depth="advanced",

        topic="general"

    )
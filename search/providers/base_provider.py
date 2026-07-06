from abc import ABC, abstractmethod
from typing import Dict


class BaseSearchProvider(ABC):

    NAME = "Base"

    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced",
        topic: str = "general"
    ) -> Dict:
        """
        Execute a web search.
        """
        pass
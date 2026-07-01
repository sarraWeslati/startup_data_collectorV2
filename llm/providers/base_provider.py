from abc import ABC, abstractmethod
from typing import Optional


class BaseProvider(ABC):

    NAME = ""

    DEFAULT_MODEL = ""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 3500,
        temperature: float = 0.0
    ):
        pass
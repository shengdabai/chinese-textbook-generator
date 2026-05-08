from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Replacement:
    original: str
    replacement: str
    tag: str


class BaseRule(ABC):
    @abstractmethod
    def apply(self, text: str, dry_run: bool = False) -> tuple[str, list[Replacement]]:
        ...

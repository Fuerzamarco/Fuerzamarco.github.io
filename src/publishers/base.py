from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Article:
    title: str
    slug: str
    markdown: str
    meta_description: str
    primary_keyword: str
    secondary_keywords: tuple[str, ...] = ()
    language: str = "es"


@dataclass(frozen=True)
class PublishResult:
    ok: bool
    location: str | Path
    detail: str = ""


class Publisher(ABC):
    @abstractmethod
    def publish(self, article: Article) -> PublishResult:
        ...

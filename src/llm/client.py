from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMRequest:
    prompt: str
    system: str | None = None
    max_tokens: int | None = None


@dataclass(frozen=True)
class LLMResponse:
    text: str
    raw: object | None = None


class LLMClient(ABC):
    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        ...

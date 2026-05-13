from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

from .paths import CONFIG_DIR, PROJECT_ROOT


@dataclass(frozen=True)
class SiteConfig:
    name: str
    base_url: str
    language: str
    locale: str


@dataclass(frozen=True)
class EditorialConfig:
    niche: str
    audience: str
    tone: str
    reading_level: str
    voice: str = "editorial-expert"
    length_strategy: str = "adaptive-by-intent"
    forbidden_phrases: tuple[str, ...] = ()
    eeat_emphasis: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()


@dataclass(frozen=True)
class ArticleDefaults:
    min_words: int
    max_words: int
    headings_style: str
    include_toc: bool
    include_meta_description: bool
    include_faq: bool


@dataclass(frozen=True)
class Settings:
    site: SiteConfig
    editorial: EditorialConfig
    article_defaults: ArticleDefaults
    raw: dict


def load_settings(path: Path | None = None) -> Settings:
    load_dotenv(PROJECT_ROOT / ".env")
    settings_path = path or (CONFIG_DIR / "settings.yaml")
    raw = yaml.safe_load(settings_path.read_text(encoding="utf-8"))

    editorial_raw = raw["editorial"]
    editorial = EditorialConfig(
        niche=editorial_raw["niche"],
        audience=editorial_raw["audience"],
        tone=editorial_raw["tone"],
        reading_level=editorial_raw["reading_level"],
        voice=editorial_raw.get("voice", "editorial-expert"),
        length_strategy=editorial_raw.get("length_strategy", "adaptive-by-intent"),
        forbidden_phrases=tuple(editorial_raw.get("forbidden_phrases", [])),
        eeat_emphasis=tuple(editorial_raw.get("eeat_emphasis", [])),
        categories=tuple(editorial_raw.get("categories", [])),
    )

    return Settings(
        site=SiteConfig(**raw["site"]),
        editorial=editorial,
        article_defaults=ArticleDefaults(**raw["article_defaults"]),
        raw=raw,
    )

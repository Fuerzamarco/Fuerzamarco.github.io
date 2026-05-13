from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CONFIG_DIR = PROJECT_ROOT / "config"
PROMPTS_DIR = CONFIG_DIR / "prompts"

DATA_DIR = PROJECT_ROOT / "data"
ARTICLES_DIR = DATA_DIR / "articles"
KEYWORDS_DIR = DATA_DIR / "keywords"
CACHE_DIR = DATA_DIR / "cache"
BATCHES_DIR = DATA_DIR / "batches"

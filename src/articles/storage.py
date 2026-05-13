from __future__ import annotations

from datetime import date

import frontmatter
from slugify import slugify

from ..publishers.base import Article


def parse_article(markdown_text: str, fallback_language: str = "es") -> Article:
    """Convierte el markdown generado por el LLM (con frontmatter YAML) en un `Article`.

    Si falta `slug` o `title`, los deriva de la primary keyword o del propio H1.
    """
    post = frontmatter.loads(markdown_text)
    meta = post.metadata or {}

    title = str(meta.get("title") or "").strip()
    if not title:
        for line in post.content.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break

    primary_keyword = str(meta.get("primary_keyword") or "").strip()

    slug = str(meta.get("slug") or "").strip()
    if not slug:
        seed = title or primary_keyword or "articulo"
        slug = slugify(seed)

    if "created_at" not in meta:
        meta["created_at"] = date.today().isoformat()
        post.metadata = meta
        markdown_text = frontmatter.dumps(post)

    secondary = meta.get("secondary_keywords") or []
    if isinstance(secondary, str):
        secondary = [s.strip() for s in secondary.split(",") if s.strip()]

    return Article(
        title=title,
        slug=slug,
        markdown=markdown_text,
        meta_description=str(meta.get("meta_description") or "").strip(),
        primary_keyword=primary_keyword,
        secondary_keywords=tuple(secondary),
        language=str(meta.get("language") or fallback_language),
    )

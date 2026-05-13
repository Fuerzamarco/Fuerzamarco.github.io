"""Post-procesado del markdown generado: overrides editoriales + validación."""
from __future__ import annotations

import frontmatter

MIN_BODY_WORDS = 800


class ValidationError(Exception):
    """El artículo no pasa los checks básicos."""


def inject_overrides(
    markdown_text: str,
    *,
    category: str | None = None,
    slug: str | None = None,
) -> str:
    """Sobrescribe campos editoriales del frontmatter con valores del CSV.

    La decisión editorial (CSV) gana sobre la improvisación del LLM.
    Si un valor es None o vacío, no se toca el campo correspondiente.
    """
    post = frontmatter.loads(markdown_text)
    if category:
        post.metadata["category"] = category
    if slug:
        post.metadata["slug"] = slug
    return frontmatter.dumps(post)


def validate(markdown_text: str, *, min_body_words: int = MIN_BODY_WORDS) -> None:
    """Lanza ValidationError si el artículo no pasa los checks mínimos.

    Checks H.2 (H.3 los extenderá):
      - title presente
      - meta_description presente
      - category presente
      - cuerpo con >= min_body_words palabras
    """
    post = frontmatter.loads(markdown_text)
    meta = post.metadata or {}

    if not str(meta.get("title", "")).strip():
        raise ValidationError("title vacío en frontmatter")
    if not str(meta.get("meta_description", "")).strip():
        raise ValidationError("meta_description vacío en frontmatter")
    if not str(meta.get("category", "")).strip():
        raise ValidationError("category vacía en frontmatter")

    word_count = len((post.content or "").split())
    if word_count < min_body_words:
        raise ValidationError(
            f"cuerpo de {word_count} palabras < mínimo {min_body_words}"
        )

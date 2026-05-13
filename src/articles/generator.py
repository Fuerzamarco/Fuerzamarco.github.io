from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter

from ..core.config import Settings
from ..core.paths import ARTICLES_DIR, PROMPTS_DIR
from ..llm.client import LLMClient, LLMRequest


@dataclass(frozen=True)
class KeywordPlan:
    primary_keyword: str
    secondary_keywords: list[str] = field(default_factory=list)
    long_tail: list[str] = field(default_factory=list)
    search_intent: str = ""
    rationale: str = ""
    related_entities: list[str] = field(default_factory=list)
    differentiators: list[str] = field(default_factory=list)
    faq_candidates: list[str] = field(default_factory=list)
    monetization_angle: str | None = None


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def list_internal_link_inventory(articles_dir: Path | None = None) -> list[dict]:
    """Lee los artículos previos y devuelve [{slug, title, primary_keyword}].

    Sirve para que el redactor pueda enlazar internamente con contexto real.
    Si el directorio no existe o está vacío, devuelve [].
    """
    target = Path(articles_dir) if articles_dir is not None else ARTICLES_DIR
    if not target.exists():
        return []
    out: list[dict] = []
    for path in sorted(target.glob("*.md")):
        try:
            post = frontmatter.load(path)
        except Exception:
            continue
        meta = post.metadata or {}
        slug = str(meta.get("slug") or path.stem).strip()
        title = str(meta.get("title") or "").strip()
        primary = str(meta.get("primary_keyword") or "").strip()
        if not slug or not (title or primary):
            continue
        out.append({"slug": slug, "title": title, "primary_keyword": primary})
    return out


def research_keywords(
    seed: str,
    raw_suggestions: list[str],
    settings: Settings,
    llm: LLMClient,
) -> KeywordPlan:
    template = (PROMPTS_DIR / "keyword_research.md").read_text(encoding="utf-8")
    inputs = {
        "seed": seed,
        "language": settings.site.language,
        "niche": settings.editorial.niche,
        "raw_suggestions": raw_suggestions,
    }
    user_prompt = (
        f"{template}\n\n"
        f"## Inputs reales\n\n"
        f"```json\n{json.dumps(inputs, ensure_ascii=False, indent=2)}\n```\n"
    )
    response = llm.complete(LLMRequest(prompt=user_prompt))
    payload = json.loads(_strip_code_fences(response.text))
    return KeywordPlan(
        primary_keyword=payload["primary_keyword"],
        secondary_keywords=list(payload.get("secondary_keywords", [])),
        long_tail=list(payload.get("long_tail", [])),
        search_intent=payload.get("search_intent", ""),
        rationale=payload.get("rationale", ""),
        related_entities=list(payload.get("related_entities", [])),
        differentiators=list(payload.get("differentiators", [])),
        faq_candidates=list(payload.get("faq_candidates", [])),
        monetization_angle=payload.get("monetization_angle"),
    )


def generate_article(
    plan: KeywordPlan,
    settings: Settings,
    llm: LLMClient,
    *,
    internal_link_inventory: list[dict] | None = None,
) -> str:
    template = (PROMPTS_DIR / "article_writer.md").read_text(encoding="utf-8")

    if internal_link_inventory is None:
        internal_link_inventory = list_internal_link_inventory()

    inputs = {
        "primary_keyword": plan.primary_keyword,
        "secondary_keywords": plan.secondary_keywords,
        "long_tail": plan.long_tail,
        "search_intent": plan.search_intent,
        "related_entities": plan.related_entities,
        "differentiators": plan.differentiators,
        "faq_candidates": plan.faq_candidates,
        "monetization_angle": plan.monetization_angle,
        "language": settings.site.language,
        "tone": settings.editorial.tone,
        "audience": settings.editorial.audience,
        "reading_level": settings.editorial.reading_level,
        "voice": settings.editorial.voice,
        "length_strategy": settings.editorial.length_strategy,
        "forbidden_phrases": list(settings.editorial.forbidden_phrases),
        "eeat_emphasis": list(settings.editorial.eeat_emphasis),
        "min_words_fallback": settings.article_defaults.min_words,
        "max_words_fallback": settings.article_defaults.max_words,
        "internal_link_inventory": internal_link_inventory,
        "internal_link_url_prefix": "/articulos",
        "allowed_categories": list(settings.editorial.categories),
    }
    user_prompt = (
        f"{template}\n\n"
        f"## Inputs reales\n\n"
        f"```json\n{json.dumps(inputs, ensure_ascii=False, indent=2)}\n```\n"
    )
    response = llm.complete(LLMRequest(prompt=user_prompt))
    return _strip_code_fences(response.text)

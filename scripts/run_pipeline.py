"""Pipeline SEO end-to-end (MVP Fase 1).

Uso:
    python scripts/run_pipeline.py --topic "café de especialidad"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.articles.generator import generate_article, research_keywords
from src.articles.storage import parse_article
from src.core.config import load_settings
from src.core.paths import ARTICLES_DIR
from src.keywords.sources.google_suggest import expand
from src.llm.claude_agent_client import ClaudeAgentClient
from src.publishers.markdown import MarkdownPublisher


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline SEO end-to-end.")
    parser.add_argument("--topic", required=True, help="Tema semilla en lenguaje natural.")
    parser.add_argument(
        "--max-keywords",
        type=int,
        default=80,
        help="Máximo de sugerencias a recolectar de Google Suggest.",
    )
    args = parser.parse_args()

    settings = load_settings()
    llm = ClaudeAgentClient()

    print(f"[1/4] Buscando sugerencias para: {args.topic!r}")
    raw = expand(args.topic, lang=settings.site.language, max_total=args.max_keywords)
    print(f"      -> {len(raw)} sugerencias")
    if not raw:
        print("ERROR: no se obtuvieron sugerencias de Google Suggest.", file=sys.stderr)
        return 1

    print("[2/4] Pidiendo a Claude el plan de keywords...")
    plan = research_keywords(args.topic, raw, settings, llm)
    print(f"      -> primary: {plan.primary_keyword}")
    if plan.secondary_keywords:
        preview = ", ".join(plan.secondary_keywords[:5])
        print(f"      -> secondary: {preview}")
    print(f"      -> intent: {plan.search_intent}")

    print("[3/4] Generando artículo (puede tardar)...")
    markdown_text = generate_article(plan, settings, llm)
    article = parse_article(markdown_text, fallback_language=settings.site.language)
    print(f"      -> {article.title}")

    print("[4/4] Guardando markdown...")
    publisher = MarkdownPublisher(ARTICLES_DIR)
    result = publisher.publish(article)
    if result.ok:
        print(f"\nOK: artículo guardado en {result.location}")
        return 0
    print(f"\nERROR al publicar: {result.detail}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

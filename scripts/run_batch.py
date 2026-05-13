"""Generación de artículos en batch (Fase H.2).

Uso:
    python scripts/run_batch.py --input data/keywords/backlog-001.csv [opciones]
    python scripts/run_batch.py --resume 2026-05-13T013000Z

Ejemplos:
    # Dry-run: muestra qué seleccionaría, no llama LLM
    python scripts/run_batch.py --input data/keywords/backlog-001.csv --tier 1 --dry-run

    # Una keyword específica para test
    python scripts/run_batch.py --input data/keywords/backlog-001.csv \\
        --keyword "Riesgos de usar IA para estudiar" --limit 1

    # Todo el tier 1 (10 artículos) con research completo
    python scripts/run_batch.py --input data/keywords/backlog-001.csv --tier 1

    # Modo rápido sin research previo
    python scripts/run_batch.py --input data/keywords/backlog-001.csv --tier 2 --no-research
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.articles.batch import load_manifest, run_batch
from src.core.config import load_settings
from src.keywords.sources.manual_csv import filter_rows, load_csv
from src.llm.claude_agent_client import ClaudeAgentClient


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generación de artículos en batch.")

    g_input = p.add_argument_group("Input")
    g_input.add_argument("--input", help="Ruta al CSV de keywords.")
    g_input.add_argument("--resume", help="ID de batch a continuar.")

    g_filter = p.add_argument_group("Filtros de selección (AND)")
    g_filter.add_argument("--tier", type=int, help="Solo filas con tier=N.")
    g_filter.add_argument("--cluster", help="Solo filas con cluster=X.")
    g_filter.add_argument("--intent", help="Solo filas con intent=X.")
    g_filter.add_argument("--keyword", help="Match exacto por keyword o slug.")
    g_filter.add_argument("--limit", type=int, help="Máximo N artículos.")

    g_run = p.add_argument_group("Comportamiento")
    g_run.add_argument(
        "--force", action="store_true",
        help="Regenerar aunque ya exista el .md.",
    )
    g_run.add_argument(
        "--no-research", action="store_true",
        help="1 LLM call por artículo (sin research previo).",
    )
    g_run.add_argument(
        "--dry-run", action="store_true",
        help="Solo imprime la selección, no llama LLM.",
    )
    g_run.add_argument(
        "--sleep-seconds", type=float, default=3.0,
        help="Pausa entre artículos (default 3).",
    )

    g_log = p.add_argument_group("Logging")
    g_log.add_argument("--quiet", action="store_true", help="Solo errores.")

    return p


def main() -> int:
    args = _build_parser().parse_args()

    manifest_to_resume = None
    if args.resume:
        manifest_to_resume = load_manifest(args.resume)
        rows = load_csv(manifest_to_resume.input)
        f = manifest_to_resume.filters
        rows = filter_rows(
            rows,
            tier=f.get("tier"),
            cluster=f.get("cluster"),
            intent=f.get("intent"),
            keyword=f.get("keyword"),
            limit=f.get("limit"),
        )
        with_research = manifest_to_resume.options.get("with_research", True)
        force = manifest_to_resume.options.get("force", False)
        sleep_seconds = manifest_to_resume.options.get("sleep_seconds", 3.0)
        input_path = manifest_to_resume.input
        filters = manifest_to_resume.filters
    else:
        if not args.input:
            print("ERROR: --input o --resume es requerido.", file=sys.stderr)
            return 2
        rows = load_csv(args.input)
        rows = filter_rows(
            rows,
            tier=args.tier,
            cluster=args.cluster,
            intent=args.intent,
            keyword=args.keyword,
            limit=args.limit,
        )
        with_research = not args.no_research
        force = args.force
        sleep_seconds = args.sleep_seconds
        input_path = args.input
        filters = {
            "tier": args.tier,
            "cluster": args.cluster,
            "intent": args.intent,
            "keyword": args.keyword,
            "limit": args.limit,
        }

    if not rows:
        print("No hay filas que procesar tras filtros.", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Selección ({len(rows)} filas):")
        for i, r in enumerate(rows, 1):
            print(
                f"  [{i}] tier={r.tier} cluster={r.cluster} intent={r.intent} "
                f"-> {r.keyword!r} ({r.slug})"
            )
        mode_label = "with-research (2 LLM calls/articulo)" if with_research else "no-research (1 LLM call/articulo)"
        print(f"\nModo: {mode_label}")
        print(f"Total estimado de LLM calls: {len(rows) * (2 if with_research else 1)}")
        print("--dry-run: no se llamó al LLM, no se escribió nada.")
        return 0

    print(f"Procesando {len(rows)} fila(s). Modo: {'with-research' if with_research else 'no-research'}")
    settings = load_settings()
    llm = ClaudeAgentClient()

    manifest = run_batch(
        rows,
        settings,
        llm,
        input_path=input_path,
        filters=filters,
        with_research=with_research,
        force=force,
        sleep_seconds=sleep_seconds,
        resume=manifest_to_resume,
        quiet=args.quiet,
    )

    s = manifest.summary()
    print(
        f"\nResumen: total={s['total']} success={s['success']} "
        f"skipped={s['skipped']} failed={s['failed']} "
        f"validation_failed={s['validation_failed']}"
    )
    print(f"Manifest: data/batches/{manifest.batch_id}.json")
    return 0 if s["failed"] == 0 and s["validation_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

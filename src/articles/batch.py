"""Orquestador de generación de artículos en batch (Fase H.2).

Procesa una lista de KeywordRow (típicamente desde un CSV), genera cada
artículo con el pipeline existente, aplica overrides editoriales (category/
slug del CSV) y validación mínima, y emite un manifest JSON por batch en
data/batches/ para soportar resume e idempotencia.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ..core.config import Settings
from ..core.paths import ARTICLES_DIR, BATCHES_DIR
from ..keywords.sources.manual_csv import KeywordRow
from ..llm.client import LLMClient
from ..publishers.markdown import MarkdownPublisher
from .generator import (
    KeywordPlan,
    generate_article,
    list_internal_link_inventory,
    research_keywords,
)
from .post_process import ValidationError, inject_overrides, validate
from .storage import parse_article


@dataclass
class RowResult:
    keyword: str
    slug: str
    cluster: str
    tier: int
    status: str  # success | skipped | failed | validation_failed
    duration_seconds: float = 0.0
    llm_calls: int = 0
    written_at: str | None = None
    error: str | None = None


@dataclass
class BatchManifest:
    batch_id: str
    input: str
    filters: dict
    options: dict
    started_at: str
    ended_at: str | None = None
    results: list[RowResult] = field(default_factory=list)

    def summary(self) -> dict:
        s = {
            "total": len(self.results),
            "success": 0,
            "skipped": 0,
            "failed": 0,
            "validation_failed": 0,
        }
        for r in self.results:
            s[r.status] = s.get(r.status, 0) + 1
        return s

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "input": self.input,
            "filters": self.filters,
            "options": self.options,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "results": [asdict(r) for r in self.results],
            "summary": self.summary(),
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_batch_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def save_manifest(manifest: BatchManifest) -> Path:
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    target = BATCHES_DIR / f"{manifest.batch_id}.json"
    target.write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return target


def load_manifest(batch_id: str) -> BatchManifest:
    path = BATCHES_DIR / f"{batch_id}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    m = BatchManifest(
        batch_id=data["batch_id"],
        input=data["input"],
        filters=data.get("filters", {}),
        options=data.get("options", {}),
        started_at=data["started_at"],
        ended_at=data.get("ended_at"),
    )
    for r in data.get("results", []):
        m.results.append(
            RowResult(
                keyword=r["keyword"],
                slug=r["slug"],
                cluster=r.get("cluster", ""),
                tier=r.get("tier", 0),
                status=r["status"],
                duration_seconds=r.get("duration_seconds", 0.0),
                llm_calls=r.get("llm_calls", 0),
                written_at=r.get("written_at"),
                error=r.get("error"),
            )
        )
    return m


def keyword_plan_from_row(row: KeywordRow) -> KeywordPlan:
    """Plan mínimo derivado del CSV (sin LLM). Para el modo --no-research."""
    return KeywordPlan(
        primary_keyword=row.keyword,
        secondary_keywords=[],
        long_tail=[],
        search_intent=row.intent,
        rationale=row.notes,
        related_entities=[],
        differentiators=[],
        faq_candidates=[],
        monetization_angle=None,
    )


def _result(row: KeywordRow, status: str, *, started: float, llm_calls: int = 0,
            error: str | None = None, written_at: str | None = None) -> RowResult:
    return RowResult(
        keyword=row.keyword,
        slug=row.slug,
        cluster=row.cluster,
        tier=row.tier,
        status=status,
        duration_seconds=time.monotonic() - started,
        llm_calls=llm_calls,
        written_at=written_at,
        error=error,
    )


def generate_one(
    row: KeywordRow,
    settings: Settings,
    llm: LLMClient,
    *,
    with_research: bool,
    force: bool,
) -> RowResult:
    """Genera un artículo. Maneja idempotencia, overrides editoriales y validación."""
    started = time.monotonic()
    target_path = ARTICLES_DIR / f"{row.slug}.md"

    if target_path.exists() and not force:
        return _result(row, "skipped", started=started)

    llm_calls = 0
    inventory = list_internal_link_inventory()

    try:
        if with_research:
            plan = research_keywords(row.keyword, [], settings, llm)
            llm_calls += 1
        else:
            plan = keyword_plan_from_row(row)
        markdown = generate_article(
            plan, settings, llm, internal_link_inventory=inventory
        )
        llm_calls += 1
    except Exception as exc:  # noqa: BLE001 — el LLM puede fallar de mil formas
        return _result(
            row, "failed",
            started=started, llm_calls=llm_calls,
            error=f"{type(exc).__name__}: {exc}",
        )

    # Overrides editoriales: CSV gana sobre LLM
    markdown = inject_overrides(markdown, category=row.category, slug=row.slug)

    # Validación mínima
    try:
        validate(markdown)
    except ValidationError as exc:
        return _result(
            row, "validation_failed",
            started=started, llm_calls=llm_calls,
            error=str(exc),
        )

    # Parse + publicar
    try:
        article = parse_article(markdown, fallback_language=settings.site.language)
        publisher = MarkdownPublisher(ARTICLES_DIR)
        result = publisher.publish(article)
        if not result.ok:
            return _result(
                row, "failed",
                started=started, llm_calls=llm_calls,
                error=f"publish failed: {result.detail}",
            )
    except Exception as exc:  # noqa: BLE001
        return _result(
            row, "failed",
            started=started, llm_calls=llm_calls,
            error=f"{type(exc).__name__}: {exc}",
        )

    return _result(
        row, "success",
        started=started, llm_calls=llm_calls,
        written_at=_now_iso(),
    )


def run_batch(
    rows: list[KeywordRow],
    settings: Settings,
    llm: LLMClient,
    *,
    input_path: str,
    filters: dict,
    with_research: bool = True,
    force: bool = False,
    sleep_seconds: float = 3.0,
    resume: BatchManifest | None = None,
    quiet: bool = False,
) -> BatchManifest:
    """Ejecuta el batch. Imprime progreso y persiste el manifest tras cada fila."""

    if resume is not None:
        manifest = resume
        done_slugs = {r.slug for r in manifest.results if r.status == "success"}
        before = len(rows)
        rows = [r for r in rows if r.slug not in done_slugs]
        if not quiet:
            print(
                f"Resuming batch {manifest.batch_id}: "
                f"{before - len(rows)} ya hechos, {len(rows)} pendientes."
            )
    else:
        manifest = BatchManifest(
            batch_id=_new_batch_id(),
            input=input_path,
            filters=filters,
            options={
                "with_research": with_research,
                "force": force,
                "sleep_seconds": sleep_seconds,
            },
            started_at=_now_iso(),
        )

    total = len(rows)
    status_symbol = {
        "success": "OK",
        "skipped": "SKIP",
        "failed": "FAIL",
        "validation_failed": "VFAIL",
    }

    for i, row in enumerate(rows, 1):
        if not quiet:
            print(
                f"[{i}/{total}] tier {row.tier} cluster {row.cluster} :: {row.keyword!r}"
            )

        result = generate_one(
            row, settings, llm,
            with_research=with_research,
            force=force,
        )
        manifest.results.append(result)
        save_manifest(manifest)  # persistencia incremental: cada fila se guarda

        if not quiet:
            symbol = status_symbol.get(result.status, "?")
            tail = f" — {result.error}" if result.error else ""
            print(
                f"      -> {symbol} "
                f"({result.duration_seconds:.1f}s, llm={result.llm_calls}){tail}"
            )

        if i < total and result.status != "skipped" and sleep_seconds > 0:
            time.sleep(sleep_seconds)

    manifest.ended_at = _now_iso()
    save_manifest(manifest)
    return manifest

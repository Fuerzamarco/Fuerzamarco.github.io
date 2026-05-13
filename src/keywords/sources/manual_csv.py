"""Fuente de keywords desde un CSV curado manualmente.

Columnas esperadas: keyword, slug, category, cluster, intent, tier, notes.
Las dos últimas son opcionales (cluster + notes) para futuros backlogs.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KeywordRow:
    keyword: str
    slug: str
    category: str
    cluster: str
    intent: str
    tier: int
    notes: str


def load_csv(path: Path | str) -> list[KeywordRow]:
    """Lee un CSV y devuelve las filas tipadas. No filtra ni valida fuertemente.

    Falla con KeyError si faltan columnas obligatorias (keyword, slug, category).
    """
    rows: list[KeywordRow] = []
    with Path(path).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            keyword = (raw.get("keyword") or "").strip()
            slug = (raw.get("slug") or "").strip()
            category = (raw.get("category") or "").strip()
            if not keyword or not slug:
                # filas vacías o malformadas: las saltamos en silencio
                continue
            try:
                tier = int((raw.get("tier") or "0").strip() or "0")
            except ValueError:
                tier = 0
            rows.append(
                KeywordRow(
                    keyword=keyword,
                    slug=slug,
                    category=category,
                    cluster=(raw.get("cluster") or "").strip(),
                    intent=(raw.get("intent") or "").strip(),
                    tier=tier,
                    notes=(raw.get("notes") or "").strip(),
                )
            )
    return rows


def filter_rows(
    rows: list[KeywordRow],
    *,
    tier: int | None = None,
    cluster: str | None = None,
    intent: str | None = None,
    keyword: str | None = None,
    limit: int | None = None,
) -> list[KeywordRow]:
    """Aplica filtros AND. Cualquiera de los parámetros puede ser None (no filtra)."""
    out = list(rows)
    if tier is not None:
        out = [r for r in out if r.tier == tier]
    if cluster is not None:
        c = cluster.strip().lower()
        out = [r for r in out if r.cluster.lower() == c]
    if intent is not None:
        i = intent.strip().lower()
        out = [r for r in out if r.intent.lower() == i]
    if keyword is not None:
        kw = keyword.strip().lower()
        out = [r for r in out if r.keyword.lower() == kw or r.slug.lower() == kw]
    if limit is not None and limit > 0:
        out = out[:limit]
    return out

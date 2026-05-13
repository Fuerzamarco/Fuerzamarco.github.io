from __future__ import annotations

import string
import time

import requests

ENDPOINT = "https://suggestqueries.google.com/complete/search"
USER_AGENT = "Mozilla/5.0 (compatible; AI-SEO-SYSTEM/0.1)"


def fetch(query: str, lang: str = "es", timeout: int = 10) -> list[str]:
    """Obtiene sugerencias para una sola consulta."""
    response = requests.get(
        ENDPOINT,
        params={"client": "firefox", "q": query, "hl": lang},
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
        return [str(s) for s in data[1]]
    return []


def expand(
    seed: str,
    lang: str = "es",
    max_total: int = 100,
    delay_seconds: float = 0.25,
) -> list[str]:
    """Devuelve sugerencias del seed más expansiones `seed + letra`.

    Ignora errores individuales (rate limits ocasionales) y deduplica preservando orden.
    """
    seen: set[str] = set()
    out: list[str] = []
    queries = [seed] + [f"{seed} {ch}" for ch in string.ascii_lowercase]

    for q in queries:
        try:
            for s in fetch(q, lang=lang):
                key = s.lower().strip()
                if key and key not in seen:
                    seen.add(key)
                    out.append(s)
                    if len(out) >= max_total:
                        return out
        except requests.RequestException:
            continue
        time.sleep(delay_seconds)

    return out

# AI-SEO-SYSTEM

Sistema local de automatización SEO en Python. Genera keywords desde fuentes gratuitas, redacta artículos optimizados con Claude (vía Claude Agent SDK + suscripción Max), guarda en markdown y prepara publicación en WordPress self-hosted.

## Principios

- **100% local y gratuito.** Sin APIs de pago, sin SaaS premium.
- **Modular.** Cada etapa del pipeline (keywords, artículos, publicación) está detrás de una interfaz.
- **Simple primero.** El MVP hace una cosa de punta a punta antes de añadir nada.

## Stack

- Python 3.11+ en Windows 11
- Claude Agent SDK (Python) → suscripción Claude Max
- Fuentes de keywords: Google Suggest, pytrends, Wikipedia (todas gratis)
- Storage: markdown + SQLite (cuando haga falta)
- Publisher: WordPress REST API + Application Passwords

## Estructura

```
AI-SEO-SYSTEM/
├── config/          # settings.yaml + prompts versionados
├── src/
│   ├── core/        # config, paths, logger
│   ├── llm/         # cliente abstracto + Claude Agent SDK
│   ├── keywords/    # fuentes + scoring
│   ├── articles/    # generador + SEO checks + storage
│   └── publishers/  # base.py + markdown.py + wordpress.py
├── data/            # keywords/, articles/, cache/
├── scripts/         # entrypoints CLI
└── tests/
```

## Estado actual

**Fase 0 — Scaffolding** (en curso). Ver [`ROADMAP.md`](ROADMAP.md).

## Quick start

Ver [`ROADMAP.md`](ROADMAP.md) para el plan por fases. Aún no hay funcionalidad ejecutable; este commit solo crea la estructura.

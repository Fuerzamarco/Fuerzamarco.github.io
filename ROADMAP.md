# Roadmap

Construcción incremental por fases. Cada fase produce algo ejecutable y revisable antes de pasar a la siguiente.

---

## Fase 0 — Scaffolding ✅

- [x] Estructura de carpetas
- [x] README + ROADMAP
- [x] `requirements.txt`, `.env.example`, `.gitignore`
- [x] `config/settings.yaml` (template)
- [x] Plantillas de prompt en `config/prompts/`
- [x] Interfaces abstractas: `llm/client.py`, `publishers/base.py`
- [ ] `git init` (cuando el usuario lo pida)

**Salida:** repo navegable, sin lógica todavía.

---

## Fase 1 — MVP de punta a punta ✅ (pendiente verificación)

Una sola fuente de keywords + un solo generador de artículos + storage markdown.

- [x] `src/core/config.py` — carga `settings.yaml` + `.env`
- [x] `src/core/paths.py` — rutas absolutas a `data/`, `config/`
- [x] `src/llm/claude_agent_client.py` — implementación Claude Agent SDK
- [x] `src/keywords/sources/google_suggest.py` — autocomplete de Google
- [x] `src/articles/generator.py` — prompt + LLM → markdown con frontmatter
- [x] `src/articles/storage.py` — parsea frontmatter y crea `Article`
- [x] `src/publishers/markdown.py` — implementa `Publisher.publish()`
- [x] `scripts/check_llm.py` — smoke test del LLM
- [x] `scripts/run_pipeline.py` — CLI que ejecuta todo end-to-end
- [ ] **Verificación end-to-end por el usuario** (instalar deps + ejecutar)

**Salida:** `python scripts/run_pipeline.py --topic "café de especialidad"` produce 1 artículo `.md`.

---

## Fase 2 — Investigación de keywords seria

- [ ] Fuente: pytrends (Google Trends sin API key)
- [ ] Fuente: Wikipedia (títulos relacionados, "see also")
- [ ] Fuente: Reddit JSON público
- [ ] Deduplicación + scoring básico (longitud, relevancia, frecuencia)
- [ ] Caché en `data/cache/` con TTL
- [ ] Export a CSV en `data/keywords/`

---

## Fase 3 — Optimización SEO real

- [ ] Checks: longitud, densidad de keyword, estructura H1/H2/H3, meta description, slug
- [ ] Generación de meta description y title tag
- [ ] Detección de keyword stuffing y sub-secciones débiles
- [ ] Reporte de calidad por artículo

---

## Fase 4 — Publicación en WordPress (aplazada — ver pivote a Astro)

- [ ] `src/publishers/wordpress.py` — REST API + Application Passwords
- [ ] Subida de imágenes (si las hay)
- [ ] Categorías y tags
- [ ] Modo `--dry-run` y `--draft`
- [ ] Idempotencia (no duplicar al re-ejecutar)

> **Nota 2026-05-07:** el publisher de WordPress queda aplazado. El proyecto pivota a un site estático con Astro (ver Fases A-G). Si más adelante se necesita publicar también en WordPress, se reactiva esta fase como un publisher adicional al markdown.

---

# Pivote a sitio estático con Astro (2026-05-07)

El sistema añade un frontend estático que consume `data/articles/*.md` y los publica como sitio web SEO-optimizado.
Arquitectura: **monorepo**, Astro vive en `web/` y lee con `glob()` desde `../data/articles`. Cero copias, cero sync.

## Fase A — Fundación Astro

- [ ] `web/` inicializado con Astro 5 + Tailwind v4 (`@tailwindcss/vite`)
- [ ] `web/src/content.config.ts` — Zod schema + glob loader sobre `../data/articles`
- [ ] `web/src/layouts/Base.astro` y `Article.astro`
- [ ] `web/src/pages/articulos/[slug].astro` renderiza un `.md` end-to-end
- [ ] `npm run build` produce HTML válido sin errores

**Salida:** un artículo se ve en `localhost:4321/articulos/<slug>/`.

## Fase B — Navegación e índices

- [ ] Home `/` con últimos artículos
- [ ] `/articulos/` index paginado
- [ ] Header + Footer compartidos

## Fase C — Categorías y links internos limpios ✅ (pendiente verificación)

- [x] Update prompt: `category` (obligatorio si `allowed_categories` no vacío) + `tags` opcional en frontmatter
- [x] Update prompt: internal links con prefijo `/articulos/<slug>/`
- [x] Ruta `/categorias/[category]/` con paths estáticos derivados de `data.category`
- [x] Componente `Breadcrumb` reutilizable
- [x] `ArticleCard` con eyebrow clicable hacia su categoría (vía pseudo `before:absolute`)
- [x] `Article.astro` con breadcrumb arriba del header
- [x] `slugify` util para mapear "Tecnología" → "tecnologia"
- [x] `settings.yaml` con lista de categorías editable + `EditorialConfig.categories`
- [ ] **Verificación end-to-end**: generar un artículo nuevo y confirmar que `category` aparece, el card linkea a `/categorias/<slug>/`, y la página de categoría renderiza.

## Fase D — SEO técnica completa ✅ (pendiente verificación)

- [x] Sitemap XML — endpoint propio (cero deps), incluye home/index/articulos/categorías; excluye paginación
- [x] RSS 2.0 — endpoint propio con escape XML manual; últimos 20 artículos
- [x] `robots.txt` dinámico vía endpoint (con `Sitemap:` absoluta)
- [x] JSON-LD: Article, BreadcrumbList, FAQPage (condicional), Organization, WebSite — sin HowTo/Speakable/Person
- [x] FAQ parser: detecta `## Preguntas frecuentes` (y variantes) en `article.body`; sólo emite schema con ≥2 preguntas
- [x] Meta canonical absoluta (ya existía)
- [x] `hreflang="es"` + `hreflang="x-default"`
- [x] `<link rel="alternate" type="application/rss+xml">` en cada página
- [x] Prop `noindex` en Base para 404 y futuras páginas privadas
- [x] Página `404.astro` limpia con `noindex` y links a home/articulos
- [ ] **Verificación**: `npm run build` produce dist/sitemap.xml, dist/rss.xml, dist/robots.txt válidos; rich-results.test.google.com sin errores en un detalle de artículo.

## Fase E — Performance & Core Web Vitals ✅ (pendiente verificación)

- [x] **Inter Variable self-hosted** vía `@fontsource-variable/inter` — un solo woff2 con todos los pesos, cero conexiones externas
- [x] **Favicon SVG** en `public/favicon.svg` (slate-950 + barra indigo-500, coherente con el brand mark del header)
- [x] **`color-scheme: light`** + **`theme-color: #ffffff`** meta tags
- [x] **`font-mono` system stack** para `code`/`pre` en article-body
- [x] **Critical CSS** ya inline por defecto en Astro static
- [x] **0 KB JS** runtime ya cumplido desde Phase A
- [ ] **(Aplazado) Imágenes vía `astro:assets`** — sin artículos con `cover_image` todavía; activar cuando se necesite
- [ ] **(Aplazado) Manual font preload** — `font-display: swap` evita FOIT; preload añadiría LCP marginal a costa de path fragility
- [ ] Verificación: `npm install && npm run build && npm run preview`, abrir DevTools → Lighthouse, target 95+ en Performance/SEO/Accessibility/Best Practices

## Fase F — AdSense + páginas legales ✅ (pendiente verificación)

- [x] **`<AdSlot />`** no-op cuando `PUBLIC_ADSENSE_PUBLISHER_ID` está vacío. Cuando se establece, renderiza `<ins class="adsbygoogle">` + push inline. Documentación de placements en el archivo.
- [x] **adsbygoogle.js global condicional** en `Base.astro` — sólo carga cuando hay publisher ID
- [x] **`/politica-privacidad/`**, **`/aviso-legal/`**, **`/cookies/`** — mismo layout editorial, eyebrow "Legal", H1 grande, fecha de actualización, contenido en `.article-body`. Texto real con placeholders `[NOMBRE TITULAR]` / `[EMAIL]` / `[NIF]` / `[DIRECCIÓN]` / `[NOMBRE PROVEEDOR HOSTING]` para rellenar.
- [x] **Footer** con 3 links legales (Privacidad / Aviso / Cookies)
- [x] **`<CookieBanner />`** — barra inferior light, hairline border, texto + botón Aceptar, ~15 líneas vanilla JS inline, localStorage `cookie-consent-accepted`. Cero modal, cero overlay, cero animaciones de aparición.
- [x] **`/ads.txt`** dinámico vía endpoint — placeholder comentado sin publisher ID, línea válida cuando se establece
- [x] **`web/.env.example`** documenta `PUBLIC_SITE_URL` y `PUBLIC_ADSENSE_PUBLISHER_ID`
- [ ] **Aviso GDPR**: el flujo es "consentimiento informativo", no CMP estricta IAB TCF. Para sitios EEA con tráfico significativo, considerar CMP real (degrada CWV).
- [ ] Verificación: `npm run build` sin errores, banner aparece y desaparece, /ads.txt + 3 páginas legales accesibles, AdSlot no inserto en ningún template (insertar a mano cuando actives).

## Fase G — Deploy

- [ ] GitHub Actions: build + cache
- [ ] Deploy a GitHub Pages (staging) y/o Hostinger (FTP/SSH)
- [ ] Configurar dominio + HTTPS

---

## Decisiones tomadas

- **2026-05-07** LLM = Claude Agent SDK (Python) sobre Claude Max. No se usa la API facturable.
- **2026-05-07** Publisher target inicial = WordPress self-hosted con REST API + Application Passwords. **APLAZADO** (ver siguiente).
- **2026-05-07** Pivote: el sistema produce un sitio estático con Astro (monorepo, `web/`, glob loader sobre `../data/articles`). WordPress aplazado o adicional, no primario.
- **2026-05-07** Stack web: Astro 5, Tailwind v4, TypeScript estricto. Rutas en español: `/articulos/`, `/categorias/`.

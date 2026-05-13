# AI-SEO-SYSTEM — Web (Astro)

Sitio estático que consume `../data/articles/*.md` (markdown generado por la pipeline Python) y los publica como páginas SEO.

## Stack

- Astro 5 (output estático)
- Tailwind CSS v4 (vía `@tailwindcss/vite`, configuración CSS-first)
- TypeScript estricto
- Content collections con `glob()` loader sobre `../data/articles`

## Quick start

```powershell
cd D:\AI-SEO-SYSTEM\web
npm install
npm run dev
```

Abre `http://localhost:4321/articulos/<slug>/` reemplazando `<slug>` por el nombre de un archivo en `../data/articles/` (sin la extensión `.md`).

Si `../data/articles/` está vacío, no habrá rutas que renderizar. Genera primero al menos un artículo con la pipeline Python:

```powershell
cd ..
python scripts/run_pipeline.py --topic "tu tema"
cd web
npm run dev
```

## Build

```powershell
npm run build       # genera ./dist
npm run preview     # sirve ./dist localmente
```

## URL pública

Por defecto, `astro.config.mjs` usa `http://localhost:4321`. En producción, define `PUBLIC_SITE_URL` antes del build:

```powershell
$env:PUBLIC_SITE_URL = "https://tu-sitio.com"
npm run build
```

Esto afecta a `<link rel="canonical">`, `og:url`, y al sitemap (cuando exista).

## Estado actual

**Fase A — Fundación.** Solo está disponible la ruta de detalle de artículo: `/articulos/[slug]/`.

Vienen en fases posteriores (ver `../ROADMAP.md`):

- **B** — Home `/`, índice `/articulos/`, header/footer
- **C** — Categorías + breadcrumb + `category` requerido en frontmatter
- **D** — Sitemap, RSS, robots, JSON-LD (Article, Breadcrumb, FAQ)
- **E** — Performance (imágenes, fuentes, audit)
- **F** — AdSense + páginas legales + cookie consent
- **G** — Deploy a GitHub Pages / Hostinger

## Validación de frontmatter

Los `.md` se validan contra el schema en `src/content.config.ts`. Si el frontmatter no cumple, **el build falla**. Esto es intencional: evita publicar artículos rotos.

Campos opcionales en Fase A que pasan a obligatorios después: `category`, `tags`.

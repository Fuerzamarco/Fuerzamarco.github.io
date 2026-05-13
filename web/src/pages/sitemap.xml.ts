import { getCollection } from 'astro:content';
import type { APIRoute } from 'astro';
import { slugify } from '../lib/slugify';

function escapeXml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

interface UrlEntry {
  loc: string;
  lastmod?: string;
  priority: string;
}

export const GET: APIRoute = async ({ site }) => {
  if (!site) {
    return new Response('site URL not configured in astro.config.mjs', {
      status: 500,
    });
  }
  const siteUrl = site.toString().replace(/\/$/, '');

  const articles = await getCollection('articles');
  const sorted = [...articles].sort(
    (a, b) => b.data.created_at.valueOf() - a.data.created_at.valueOf()
  );

  const urls: UrlEntry[] = [
    { loc: `${siteUrl}/`, priority: '1.0' },
    { loc: `${siteUrl}/articulos/`, priority: '0.9' },
  ];

  for (const article of sorted) {
    const lastmod = (
      article.data.updated_at ?? article.data.created_at
    ).toISOString();
    urls.push({
      loc: `${siteUrl}/articulos/${article.id}/`,
      lastmod,
      priority: '0.8',
    });
  }

  // Categorías (lastmod = artículo más reciente de la categoría).
  const categoryLastmod = new Map<string, { label: string; lastmod: Date }>();
  for (const article of articles) {
    const cat = article.data.category;
    if (!cat) continue;
    const slug = slugify(cat);
    const d = article.data.updated_at ?? article.data.created_at;
    const existing = categoryLastmod.get(slug);
    if (!existing || d > existing.lastmod) {
      categoryLastmod.set(slug, { label: cat, lastmod: d });
    }
  }
  for (const [slug, { lastmod }] of categoryLastmod) {
    urls.push({
      loc: `${siteUrl}/categorias/${slug}/`,
      lastmod: lastmod.toISOString(),
      priority: '0.7',
    });
  }

  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
  .map(
    (u) =>
      `  <url>
    <loc>${escapeXml(u.loc)}</loc>${u.lastmod ? `\n    <lastmod>${u.lastmod}</lastmod>` : ''}
    <priority>${u.priority}</priority>
  </url>`
  )
  .join('\n')}
</urlset>
`;

  return new Response(body, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};

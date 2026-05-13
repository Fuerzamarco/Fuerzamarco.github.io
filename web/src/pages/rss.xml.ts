import { getCollection } from 'astro:content';
import type { APIRoute } from 'astro';
import { SITE_NAME, SITE_DESCRIPTION } from '../config/site';

function escapeXml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

const RFC_822 = (d: Date): string => d.toUTCString();
const MAX_ITEMS = 20;

export const GET: APIRoute = async ({ site }) => {
  if (!site) {
    return new Response('site URL not configured in astro.config.mjs', {
      status: 500,
    });
  }
  const siteUrl = site.toString().replace(/\/$/, '');

  const articles = await getCollection('articles');
  const sorted = [...articles]
    .sort((a, b) => b.data.created_at.valueOf() - a.data.created_at.valueOf())
    .slice(0, MAX_ITEMS);

  const lastBuildDate = sorted[0]?.data.created_at ?? new Date();

  const items = sorted
    .map((a) => {
      const url = `${siteUrl}/articulos/${a.id}/`;
      const cat = a.data.category;
      return `    <item>
      <title>${escapeXml(a.data.title)}</title>
      <link>${escapeXml(url)}</link>
      <guid isPermaLink="true">${escapeXml(url)}</guid>
      <pubDate>${RFC_822(a.data.created_at)}</pubDate>
      <description>${escapeXml(a.data.meta_description)}</description>${cat ? `\n      <category>${escapeXml(cat)}</category>` : ''}
    </item>`;
    })
    .join('\n');

  const body = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${escapeXml(SITE_NAME)}</title>
    <link>${escapeXml(siteUrl + '/')}</link>
    <description>${escapeXml(SITE_DESCRIPTION)}</description>
    <language>es-ES</language>
    <lastBuildDate>${RFC_822(lastBuildDate)}</lastBuildDate>
    <atom:link href="${escapeXml(siteUrl + '/rss.xml')}" rel="self" type="application/rss+xml" />
${items}
  </channel>
</rss>
`;

  return new Response(body, {
    headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' },
  });
};

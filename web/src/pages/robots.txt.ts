import type { APIRoute } from 'astro';

export const GET: APIRoute = async ({ site }) => {
  if (!site) {
    return new Response('site URL not configured in astro.config.mjs', {
      status: 500,
    });
  }
  const siteUrl = site.toString().replace(/\/$/, '');
  const body = `User-agent: *
Allow: /

Sitemap: ${siteUrl}/sitemap.xml
`;
  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};

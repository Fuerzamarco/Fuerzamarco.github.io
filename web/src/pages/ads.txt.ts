import type { APIRoute } from 'astro';

/**
 * /ads.txt — declaración de vendors autorizados (formato AdSense).
 *
 * - Si PUBLIC_ADSENSE_PUBLISHER_ID está set: emite la línea válida.
 * - Si no: emite un placeholder comentado (el bot de Google no devuelve 404).
 *
 * El valor `f08c47fec0942fa0` es el CertificationAuthorityID estándar de Google.
 */
export const GET: APIRoute = async () => {
  const PUB_ID = import.meta.env.PUBLIC_ADSENSE_PUBLISHER_ID || '';
  const body = PUB_ID
    ? `google.com, pub-${PUB_ID}, DIRECT, f08c47fec0942fa0\n`
    : `# ads.txt placeholder. Añade tu publisher ID en PUBLIC_ADSENSE_PUBLISHER_ID\n# y este endpoint emitirá automáticamente la línea válida.\n`;
  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};

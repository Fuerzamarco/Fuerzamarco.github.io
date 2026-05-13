/**
 * Convierte un string a slug URL-safe en kebab-case.
 * Maneja acentos del espanol (a->a, n->n, u->u) via NFD + diacritic strip.
 */
export function slugify(str: string): string {
  return str
    .toLowerCase()
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

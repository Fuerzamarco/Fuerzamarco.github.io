import type { CollectionEntry } from 'astro:content';
import { stripMarkdown, type FaqItem } from './faq-parser';

export interface SchemaContext {
  siteUrl: string;   // sin barra final
  siteName: string;
}

export function buildOrganizationSchema(ctx: SchemaContext) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: ctx.siteName,
    url: `${ctx.siteUrl}/`,
  };
}

export function buildWebsiteSchema(ctx: SchemaContext) {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: ctx.siteName,
    url: `${ctx.siteUrl}/`,
    inLanguage: 'es-ES',
  };
}

export function buildArticleSchema(
  article: CollectionEntry<'articles'>,
  ctx: SchemaContext
) {
  const url = `${ctx.siteUrl}/articulos/${article.id}/`;
  const datePublished = article.data.created_at.toISOString();
  const dateModified = (
    article.data.updated_at ?? article.data.created_at
  ).toISOString();
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: article.data.title,
    description: article.data.meta_description,
    inLanguage: article.data.language || 'es',
    datePublished,
    dateModified,
    author: {
      '@type': 'Organization',
      name: ctx.siteName,
      url: `${ctx.siteUrl}/`,
    },
    publisher: {
      '@type': 'Organization',
      name: ctx.siteName,
      url: `${ctx.siteUrl}/`,
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': url,
    },
  };
}

export interface BreadcrumbSchemaItem {
  label: string;
  url: string; // absoluta
}

export function buildBreadcrumbSchema(items: BreadcrumbSchemaItem[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: item.label,
      item: item.url,
    })),
  };
}

/**
 * Returns null if there are < 2 FAQs (filtra spam-like single-Q schemas).
 */
export function buildFaqSchema(faqs: FaqItem[]): Record<string, unknown> | null {
  if (faqs.length < 2) return null;
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: stripMarkdown(faq.answer),
      },
    })),
  };
}

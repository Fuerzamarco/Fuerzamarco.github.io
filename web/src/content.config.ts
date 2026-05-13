import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const articles = defineCollection({
  loader: glob({
    pattern: '**/*.md',
    base: '../data/articles',
  }),
  schema: z.object({
    title: z.string().max(120),
    slug: z.string().optional(),
    meta_description: z.string(),
    primary_keyword: z.string(),
    secondary_keywords: z.array(z.string()).default([]),
    language: z.string().default('es'),
    search_intent: z
      .enum(['informational', 'commercial', 'transactional', 'navigational'])
      .optional(),
    category: z.string().optional(),
    tags: z.array(z.string()).default([]),
    created_at: z.coerce.date(),
    updated_at: z.coerce.date().optional(),
    internal_links_used: z.array(z.string()).default([]),
    cover_image: z.string().optional(),
  }),
});

export const collections = { articles };

// Astro content collections — defines the shape of /src/content/pages/*.md
import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const pages = defineCollection({
  loader: glob({
    pattern: "**/*.md",
    base: "./src/content/pages",
    // Preserve the full relative path as the id (don't strip trailing /index)
    // so /index.md and /key-concepts/index.md don't collide.
    generateId: ({ entry }) => entry.replace(/\.md$/, ""),
  }),
  schema: z.object({
    title: z.string(),
    // Pretty name shown in nav. Defaults to title if absent.
    navLabel: z.string().optional(),
    // Slug override; otherwise derived from file path.
    slug: z.string().optional(),
    // Group key used by the nav builder (e.g. "key-concepts").
    section: z.string().optional(),
    // Order within its section.
    order: z.number().default(100),
    // Optional short summary, used for description meta tag + index pages.
    summary: z.string().optional(),
    // Hide from nav (still routable).
    hidden: z.boolean().default(false),
  }),
});

export const collections = { pages };

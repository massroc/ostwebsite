// Builds the site navigation by grouping pages by their `section` frontmatter.
// Hidden pages and the homepage are excluded from the nav.
import { getCollection, type CollectionEntry } from "astro:content";

export type NavSection = {
  key: string;
  label: string;
  href: string;
  items: { label: string; href: string }[];
};

// Section ordering + display labels. Anything not in this map is appended A→Z.
const SECTIONS: Record<string, { label: string; order: number }> = {
  "key-concepts":   { label: "Key Concepts",  order: 1 },
  "tools-of-ost":   { label: "Tools of OST",  order: 2 },
  "resources":      { label: "Resources",     order: 3 },
  "about":          { label: "About",         order: 4 },
  "contact":        { label: "Contact",       order: 5 },
};

export function pageHref(entry: CollectionEntry<"pages">): string {
  // The collection `id` is the file path relative to src/content/pages
  // without extension, e.g. "key-concepts/the-six-criteria". The homepage
  // file is "index.md".
  if (entry.id === "index") return "/";
  return `/${entry.id}/`;
}

export async function buildNav(): Promise<NavSection[]> {
  const entries = await getCollection("pages", (p) => !p.data.hidden && p.id !== "index");

  // Group by section.
  const groups = new Map<string, CollectionEntry<"pages">[]>();
  for (const e of entries) {
    const key = e.data.section ?? "misc";
    const arr = groups.get(key) ?? [];
    arr.push(e);
    groups.set(key, arr);
  }

  const sections: NavSection[] = [];
  for (const [key, items] of groups) {
    items.sort((a, b) => (a.data.order ?? 100) - (b.data.order ?? 100));
    const meta = SECTIONS[key];
    // The section landing page is the entry whose slug equals the section key,
    // e.g. "key-concepts/index" or "key-concepts" (collection id without trailing /index).
    const landing = items.find((i) => i.id === key || i.id === `${key}/index`) ?? items[0];
    sections.push({
      key,
      label: meta?.label ?? toTitle(key),
      href: pageHref(landing),
      items: items
        .filter((i) => i.id !== landing.id)
        .map((i) => ({ label: i.data.navLabel ?? i.data.title, href: pageHref(i) })),
    });
  }

  sections.sort((a, b) => (SECTIONS[a.key]?.order ?? 99) - (SECTIONS[b.key]?.order ?? 99));
  return sections;
}

function toTitle(key: string): string {
  return key.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

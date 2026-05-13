# ostwebsite

Source for [opensystemstheory.org](https://opensystemstheory.org) — a learning resource for those interested in Open Systems Theory (OST).

## Stack

- [Astro](https://astro.build/) 5 — static site, file-based routing, content collections
- [Tailwind CSS](https://tailwindcss.com/) 4 (via `@tailwindcss/vite`)
- Roboto / Roboto Slab via `@fontsource`
- Deployed to **Cloudflare Pages** by GitHub Actions on push to `main`

## Layout

```
src/
  content/pages/      Markdown content, one file per page
                      (section folder + index.md = section landing)
  pages/              Astro routes (index.astro + [...slug].astro)
  layouts/            BaseLayout (header + footer + slot)
  components/         Header, Footer
  lib/nav.ts          Builds nav from content collection frontmatter
  styles/global.css   Tailwind import + brand tokens + .prose rules
public/
  images/             Static images referenced from content
  _redirects          Cloudflare Pages redirects (legacy WP URLs → new)
scripts/
  extract_content.py  One-off importer: _legacy/ HTML → content/pages/*.md
_legacy/              wget mirror of the old WP site, kept for reference;
                      delete once we're confident nothing else needs porting
```

## Develop

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # writes ./dist
npm run preview      # serve ./dist
```

## Add a page

1. Create `src/content/pages/<section>/<slug>.md` with frontmatter:
   ```yaml
   ---
   title: My Page
   section: key-concepts     # group in nav
   order: 2                  # within section
   navLabel: Short label     # optional; defaults to title
   summary: Optional one-line description
   ---
   ```
2. `git push` to `main` — live in ~60s.

## Deploy

GitHub Actions builds and runs `wrangler pages deploy ./dist` against the Cloudflare Pages project `ostwebsite`. `--branch=production` on `main` → live site; PRs and other branches → preview URLs.

Secrets in GitHub: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`.

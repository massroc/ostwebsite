# Notes for Claude (and Ross)

Quick reference for working on this repo. See `README.md` for the bigger picture and `ROADMAP.md` for what's planned.

## Adding a page

1. Drop a Markdown file in `src/content/pages/<section>/<slug>.md`.
2. Required frontmatter:
   ```yaml
   ---
   title: My Page Title
   section: key-concepts      # one of: key-concepts | tools-of-ost | resources | about | contact
   order: 5                   # position within the section (lower first)
   ---
   ```
3. Optional frontmatter:
   ```yaml
   navLabel: Short Label      # what shows in nav; defaults to title
   summary: One-line description used in <meta description> and intro
   slug: custom-url-segment   # override the filename-derived slug
   hidden: true               # routable but excluded from nav
   ```
4. Section landing page is `<section>/index.md` (e.g. `key-concepts/index.md`); use `navLabel: Overview` and `order: 1` by convention.
5. Push to `main` → live on opensystemstheory.org in ~60 seconds (GitHub Actions builds and deploys).

## Adding a new section

1. Pick a section key (kebab-case, used in the URL and in `section:` frontmatter).
2. Add it to the `SECTIONS` map in `src/lib/nav.ts` with its display label and `order` (controls nav position).
3. Create `src/content/pages/<section>/index.md` with `navLabel: Overview`, `order: 1`, and at least placeholder content.

## When Ross says "push this content"

He'll typically hand over a `.md` file (or pasted Markdown) that came out of his LLM-generated OST wiki elsewhere. Workflow:

1. Confirm or infer: target `section`, filename slug, `order` (next available in that section).
2. Make sure frontmatter is complete and well-formed (the schema is in `src/content.config.ts`).
3. If anything's ambiguous (which section? new section?), ask before guessing.
4. Run `npm run build` locally to catch frontmatter / link errors before pushing.
5. Commit with a descriptive message, push to `main`. Production deploy fires automatically; watch with `gh run watch`.

If the content references images, drop them into `public/images/` and use root-relative URLs (`/images/...`) in the Markdown.

## Don't

- Don't edit files via the Cloudflare dashboard — GitHub is the source of truth, and the next push would overwrite dashboard changes.
- Don't add Workers/KV/R2/etc. without updating the API token's scopes (currently Pages-only by design — see project memory).
- Don't reintroduce the `/home/` URL prefix; legacy paths are 301'd via `public/_redirects` and shouldn't recur.

## Useful commands

```bash
npm run dev          # local preview at http://localhost:4321
npm run build        # build to ./dist
gh run list          # see recent CI runs
gh run watch         # tail the active CI run
wrangler pages deployment list --project-name=ostwebsite
```

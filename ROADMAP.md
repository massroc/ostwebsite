# Roadmap

Planned changes for opensystemstheory.org, in rough priority order. Not a commitment — a working note.

## In flight (elsewhere)

- **LLM-generated OST wiki.** Building out substantial new content in a separate workspace. Output will land here as Markdown files dropped into `src/content/pages/`. Will likely shape what the schema and nav need to look like.

## Deferred

- **Design refactor.** Current visual is functional but unrefined ("looks terrible" — accurate). Deferred until content stabilises so the design can follow content shape rather than the other way around. When picked up: likely a richer landing page, better typography rhythm, possibly a sidebar TOC for long pages, hero treatments for section landings.

## Likely needed once wiki content lands

- **Schema extensions.** `src/content.config.ts` currently has `title / navLabel / slug / section / order / summary / hidden`. Probable additions once content scales: `tags`, `lastUpdated`, `authors`, `sources` (for citations), `aiGenerated` flag.
- **Nav rethink.** Flat dropdown nav works for ~20 pages. With 50+ it'll need a different structure — sidebar, section landing pages with their own indices, or a search affordance.
- **Search.** Pagefind is the obvious choice for static sites (build-time index, client-side search, zero infra).
- **Section landings.** Currently each section's `index.md` is sparse. Once we have many child pages per section, the landing should auto-list them with summaries.

## Smaller follow-ups

- Flesh out thin pages: `/tools-of-ost/participative-design-workshop/`, `/tools-of-ost/unique-design/` (near-empty on old site too).
- Decide fate of `/about/` section — created during the refactor to surface buried pages (History + Primer); review when overall structure is reconsidered.
- External links lost in migration on `/resources/practitioners/` (Desirable Futures, ReBoot Co., AMERIN, etc.) — restore manually if/when URLs are known. Declined as not worth the time right now.
- Drop `scripts/extract_content.py`. Migration is done; the script no longer runs (the `_legacy/` directory it reads from has been deleted). Kept for now as a record.

## Done

- 2026-05-14 — Mirrored WP-on-Cloudflare site to GitHub.
- 2026-05-14 — Set up GitHub Actions → Cloudflare Pages deploy (Direct Upload origin prevented native Git integration).
- 2026-05-14 — Refactored to Astro 5 + Tailwind 4. 20 pages extracted from WP export to Markdown. Legacy URLs 301-redirected. `_legacy/` mirror deleted.

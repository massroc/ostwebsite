#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4", "markdownify", "lxml"]
# ///
"""
Extract canonical content pages from _legacy/ (a wget mirror of the old
WordPress site) and write them as Markdown into src/content/pages/.

Mapping (legacy URL → new slug):
  /                                           → index
  /home/key-concepts/                         → key-concepts/index
  /home/key-concepts/design-principles/       → key-concepts/design-principles
  /home/key-concepts/the-six-criteria/        → key-concepts/the-six-criteria
  /the-system-and-the-environment/            → key-concepts/the-system-and-the-environment
  /home/tools-of-ost/                         → tools-of-ost/index
  /home/tools-of-ost/search-conference/       → tools-of-ost/search-conference
  /home/tools-of-ost/participative-design-workshop/ → tools-of-ost/participative-design-workshop
  /home/tools-of-ost/unique-design/           → tools-of-ost/unique-design
  /home/learning/                             → resources/index
  /home/learning/case-studies/                → resources/case-studies
  /home/learning/further-reading/             → resources/further-reading
  /home/learning/origins_of_our_group/        → resources/origins-of-our-group
  /home/learning/ost-talks/                   → resources/ost-talks
  /home/learning/practitioners/               → resources/practitioners
  /home/learning/qa-with-ost-co-creator-dr-merrelyn-emery/ → resources/qa-with-merrelyn-emery
  /home/a-history-of-ost/                     → about/history
  /home/ost-primer/                           → about/ost-primer
  /home/contact/                              → contact/index
  /home/contact/services/                     → contact/services
"""

from __future__ import annotations
import re
import sys
from pathlib import Path
from textwrap import dedent

from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import markdownify as md

ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / "_legacy"
OUT = ROOT / "src" / "content" / "pages"

# (legacy_dir, new_slug, section, order, nav_label)
PAGES = [
    ("",                                                "index",                                    None,           0,   None),
    ("home/key-concepts",                               "key-concepts/index",                       "key-concepts", 1,   "Overview"),
    ("home/key-concepts/design-principles",             "key-concepts/design-principles",           "key-concepts", 2,   None),
    ("home/key-concepts/the-six-criteria",              "key-concepts/the-six-criteria",            "key-concepts", 3,   None),
    ("the-system-and-the-environment",                  "key-concepts/the-system-and-the-environment","key-concepts", 4, "The System and the Environment"),
    ("home/tools-of-ost",                               "tools-of-ost/index",                       "tools-of-ost", 1,   "Overview"),
    ("home/tools-of-ost/search-conference",             "tools-of-ost/search-conference",           "tools-of-ost", 2,   None),
    ("home/tools-of-ost/participative-design-workshop", "tools-of-ost/participative-design-workshop","tools-of-ost", 3,  None),
    ("home/tools-of-ost/unique-design",                 "tools-of-ost/unique-design",               "tools-of-ost", 4,   None),
    ("home/learning",                                   "resources/index",                          "resources",    1,   "Overview"),
    ("home/learning/case-studies",                      "resources/case-studies",                   "resources",    2,   None),
    ("home/learning/practitioners",                     "resources/practitioners",                  "resources",    3,   None),
    ("home/learning/ost-talks",                         "resources/ost-talks",                      "resources",    4,   "OST Talks"),
    ("home/learning/further-reading",                   "resources/further-reading",                "resources",    5,   None),
    ("home/learning/qa-with-ost-co-creator-dr-merrelyn-emery", "resources/qa-with-merrelyn-emery", "resources",    6,   "Q&A with Merrelyn Emery"),
    ("home/learning/origins_of_our_group",              "resources/origins-of-our-group",           "resources",    7,   None),
    ("home/a-history-of-ost",                           "about/history",                            "about",        1,   "A History of OST"),
    ("home/ost-primer",                                 "about/ost-primer",                         "about",        2,   "OST Primer"),
    ("home/contact",                                    "contact/index",                            "contact",      1,   "Overview"),
    ("home/contact/services",                           "contact/services",                         "contact",      2,   None),
]


def extract_title(soup: BeautifulSoup) -> str:
    # Prefer the first <h1>; fall back to <title>.
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    t = soup.find("title")
    if t:
        raw = t.get_text(strip=True)
        # WP titles are "Page – Open Systems Theory ..." — strip the suffix.
        return re.split(r"\s+[–|-]\s+", raw)[0].strip()
    return "Untitled"


def find_content_root(soup: BeautifulSoup) -> Tag | None:
    """The article body lives inside Elementor's main wrapper on every page."""
    candidates = [
        ("div", {"data-elementor-type": "wp-page"}),
        ("div", {"data-elementor-type": "wp-post"}),
        ("main", {"id": "primary"}),
        ("article", {}),
        ("div", {"class": "site-content"}),
    ]
    for tag, attrs in candidates:
        node = soup.find(tag, attrs=attrs)
        if node:
            return node
    return soup.find("body")


def strip_noise(node: Tag) -> None:
    """Remove WP/Elementor cruft from the content subtree."""
    REMOVE_SELECTORS = [
        "script", "style", "noscript",
        ".elementor-element-populated > .elementor-widget-empty",
        ".sharedaddy", ".jp-relatedposts", ".jp-carousel-wrap",
        ".elementor-widget-theme-post-comments",
        ".elementor-search-form", ".elementor-nav-menu", ".elementor-widget-nav-menu",
        ".elementor-button-wrapper",   # remove leftover CTA buttons (manual restoration later if needed)
        ".astra-search-icon",
        "[id^=ast-]",                  # Astra theme widgets
        ".main-header-bar-wrap",
        ".main-navigation",
        ".site-header", ".site-footer", "header", "footer",
        ".elementor-widget-image:has(img[alt=''])",  # decorative blank images
    ]
    for sel in REMOVE_SELECTORS:
        for el in node.select(sel):
            el.decompose()

    # Strip Elementor's per-node inline style/class attrs but keep semantic structure.
    for el in node.find_all(True):
        for attr in list(el.attrs.keys()):
            if attr in ("href", "src", "alt", "title"):
                continue
            del el.attrs[attr]


def _new_path(slug: str) -> str:
    """Slug → public URL path (homepage = '/')."""
    if slug == "index":
        return "/"
    return f"/{slug.replace('/index', '')}/"


# Old legacy paths → new slugs. Covers canonical and stale-duplicate routes.
URL_ALIASES: dict[str, str] = {}
for src, dst, *_ in PAGES:
    if src:
        URL_ALIASES[src] = dst
        # WordPress also exposed many of these without /home/ — capture both.
        if src.startswith("home/"):
            URL_ALIASES[src[len("home/"):]] = dst
# Stale duplicate paths the old WP install kept around.
URL_ALIASES.update({
    "sample-page/key-concepts": "key-concepts/index",
    "sample-page/tools-of-ost": "tools-of-ost/index",
    "sample-page/tools-of-ost/unique-design": "tools-of-ost/unique-design",
    "sample-page/tools-of-ost/__trashed": "tools-of-ost/participative-design-workshop",
    "key-concepts": "key-concepts/index",
    "key-concepts/search-conference": "tools-of-ost/search-conference",
    "key-concepts/the-six-criteria": "key-concepts/the-six-criteria",
    "practitioners": "resources/practitioners",
    "contact": "contact/index",
})


def _resolve(src_dir: str, href: str) -> str | None:
    """Resolve href (relative or absolute) against the page's legacy location,
    return a normalised legacy path like 'home/key-concepts' (no leading/trailing slash,
    no index.html, no query), or None if it's external/unrouteable."""
    # Drop fragments & query.
    href = re.sub(r"[?#].*$", "", href)
    if not href or href.startswith(("mailto:", "tel:", "javascript:")):
        return None

    # Absolute opensystemstheory.org URL.
    m = re.match(r"^https?://(?:www\.)?opensystemstheory\.org/(.*)$", href)
    if m:
        path = m.group(1)
    elif href.startswith("/"):
        path = href.lstrip("/")
    elif href.startswith(("http://", "https://")):
        return None  # external
    else:
        # Relative — resolve against src_dir.
        base = src_dir.split("/") if src_dir else []
        parts = base + href.split("/")
        out: list[str] = []
        for p in parts:
            if p in ("", "."):
                continue
            if p == "..":
                if out:
                    out.pop()
                continue
            out.append(p)
        path = "/".join(out)

    # Strip trailing /index.html or trailing /.
    path = re.sub(r"/index\.html?$", "", path)
    path = path.rstrip("/")
    return path


URL_LIKE_TEXT = re.compile(r"^\s*((?:https?://|www\.)[^\s<>]+)\s*$", re.I)


def rewrite_links(node: Tag, src_dir: str) -> None:
    """Rewrite every <a href> through URL_ALIASES; absolutise <img src>."""
    for a in node.find_all("a", href=True):
        # Heuristic: external links wget couldn't mirror sometimes survived only
        # as their visible text. If the link text is a URL, prefer it as href.
        text = a.get_text(" ", strip=True)
        m = URL_LIKE_TEXT.match(text)
        if m and not a["href"].startswith(("http://", "https://", "mailto:")):
            url = m.group(1)
            if url.startswith("www."):
                url = "https://" + url
            a["href"] = url
            continue

        legacy = _resolve(src_dir, a["href"])
        if legacy is None:
            continue
        if legacy == "":
            a["href"] = "/"
            continue
        if legacy in URL_ALIASES:
            a["href"] = _new_path(URL_ALIASES[legacy])
        elif a["href"].startswith(("http://", "https://", "/")):
            pass  # leave absolute external links alone
        else:
            # Unknown internal target — drop the link, keep the text.
            a.replace_with(NavigableString(a.get_text()))

    # Images: drop the wp-content/uploads prefix → /images/...
    for img in node.find_all("img", src=True):
        m = re.search(r"wp-content/uploads/(.+)$", img["src"])
        if m:
            img["src"] = f"/images/{m.group(1)}"


def html_to_markdown(node: Tag) -> str:
    raw = str(node)
    text = md(
        raw,
        heading_style="ATX",
        bullets="-",
        strip=["span", "div"],   # collapse generic wrappers
        escape_underscores=False,
    )
    # Collapse runs of blank lines + trim.
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    # Drop the leading title (we put it in frontmatter; Astro renders it).
    text = re.sub(r"^#\s+.+?\n\n?", "", text, count=1)
    return text


def fm_value(s: str) -> str:
    """YAML scalar; quote if it contains anything risky."""
    if re.search(r"[:#\[\]{}&*!|>'\"%@`,]|^\s|\s$", s):
        esc = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{esc}"'
    return s


def build_frontmatter(title: str, section: str | None, order: int, nav_label: str | None) -> str:
    lines = ["---", f"title: {fm_value(title)}"]
    if nav_label:
        lines.append(f"navLabel: {fm_value(nav_label)}")
    if section:
        lines.append(f"section: {section}")
        lines.append(f"order: {order}")
    lines.append("---\n")
    return "\n".join(lines)


def process(src_dir: str, slug: str, section: str | None, order: int, nav_label: str | None) -> tuple[str, int]:
    src = LEGACY / src_dir / "index.html" if src_dir else LEGACY / "index.html"
    if not src.exists():
        return (f"  ⚠  {src_dir or '/'}: source not found ({src})", 0)

    soup = BeautifulSoup(src.read_text(encoding="utf-8", errors="replace"), "lxml")
    title = extract_title(soup)
    root = find_content_root(soup)
    if root is None:
        return (f"  ⚠  {src_dir or '/'}: no content root found", 0)

    strip_noise(root)
    rewrite_links(root, src_dir)
    body = html_to_markdown(root)

    out_path = OUT / f"{slug}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_frontmatter(title, section, order, nav_label) + body + "\n", encoding="utf-8")
    return (f"  ✓ {src_dir or '/'} → {slug}.md ({len(body)} chars)", len(body))


def main() -> int:
    if not LEGACY.exists():
        print(f"missing {LEGACY}", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for src, dst, section, order, nav_label in PAGES:
        msg, n = process(src, dst, section, order, nav_label)
        print(msg)
        total += n
    print(f"\n{len(PAGES)} pages, {total} chars total")
    return 0


if __name__ == "__main__":
    sys.exit(main())

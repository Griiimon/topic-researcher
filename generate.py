#!/usr/bin/env python3
"""Topic Learning Lists - static site generator.

Reads comma-separated topic lists from input/*.txt and writes one HTML page
per list, plus an index page, into output/. Standard library only.
"""

import shutil
from html import escape
from pathlib import Path
from urllib.parse import quote, quote_plus

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "input"
OUTPUT_DIR = ROOT / "output"
STYLE_SRC = Path(__file__).resolve().parent / "style.css"


# --------------------------------------------------------------------------
# Research providers (add new destinations here)
# --------------------------------------------------------------------------

def google_url(topic: str) -> str:
    return "https://www.google.com/search?q=" + quote_plus(topic)


def wikipedia_url(topic: str) -> str:
    return "https://en.wikipedia.org/w/index.php?search=" + quote_plus(topic)


def dictionary_url(topic: str) -> str:
    slug = "-".join(topic.lower().split())
    return "https://www.dictionary.com/browse/" + quote(slug, safe="-")


SEARCH_PROVIDERS = [
    ("Google", google_url),
    ("Wikipedia", wikipedia_url),
    ("Dictionary", dictionary_url),
]


# --------------------------------------------------------------------------
# Parsing and formatting
# --------------------------------------------------------------------------

def parse_topics(text: str) -> list[str]:
    """Split on commas, trim whitespace, drop empty entries."""
    topics = []
    for part in text.replace("\n", ",").split(","):
        topic = " ".join(part.split())
        if topic:
            topics.append(topic)
    return topics


def page_title(stem: str) -> str:
    """programming_languages -> Programming Languages"""
    return " ".join(stem.replace("_", " ").replace("-", " ").split()).title()


def display_topic(topic: str) -> str:
    """Capitalise words, but leave words that already contain capitals (ATP)."""
    words = []
    for word in topic.split(" "):
        if word and word == word.lower():
            word = word[0].upper() + word[1:]
        words.append(word)
    return " ".join(words)


# --------------------------------------------------------------------------
# HTML generation
# --------------------------------------------------------------------------

def html_page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
{body}
</body>
</html>
"""


def topic_section(topic: str) -> str:
    links = "\n".join(
        f'            <a href="{escape(url_fn(topic), quote=True)}" '
        f'target="_blank" rel="noopener">{escape(name)}</a>'
        for name, url_fn in SEARCH_PROVIDERS
    )
    return f"""    <section class="topic">
        <h2>{escape(display_topic(topic))}</h2>
        <div class="links">
{links}
        </div>
    </section>"""


def render_topic_page(title: str, topics: list[str]) -> str:
    nav = '<nav class="nav"><a href="index.html">&larr; All topics</a></nav>'
    sections = "\n\n".join(topic_section(t) for t in topics)
    if not sections:
        sections = '    <p class="empty">This list has no topics yet.</p>'
    body = f"""<main>
    {nav}
    <h1>{escape(title)}</h1>

{sections}

    {nav}
</main>"""
    return html_page(title, body)


def render_index(pages: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f'        <li><a href="{escape(filename, quote=True)}">{escape(title)}</a></li>'
        for title, filename in pages
    )
    if not items:
        items = '        <li class="empty">No topic lists yet. Add a .txt file to input/.</li>'
    body = f"""<main>
    <h1>Learning Topics</h1>
    <ul class="collections">
{items}
    </ul>
</main>"""
    return html_page("Learning Topics", body)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Remove stale generated pages so deleted inputs disappear from the site.
    for old in OUTPUT_DIR.glob("*.html"):
        old.unlink()

    pages = []
    for src in sorted(INPUT_DIR.glob("*.txt")):
        topics = parse_topics(src.read_text(encoding="utf-8"))
        title = page_title(src.stem)
        filename = src.stem + ".html"
        (OUTPUT_DIR / filename).write_text(
            render_topic_page(title, topics), encoding="utf-8"
        )
        pages.append((title, filename))

    pages.sort(key=lambda p: p[0].lower())
    (OUTPUT_DIR / "index.html").write_text(render_index(pages), encoding="utf-8")
    shutil.copyfile(STYLE_SRC, OUTPUT_DIR / "style.css")

    print(f"Generated {len(pages)} topic page(s) plus index in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

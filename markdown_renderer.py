"""Markdown rendering with sanitization."""

from __future__ import annotations

import re

import bleach
import markdown
from markupsafe import Markup


ALLOWED_TAGS = list(bleach.ALLOWED_TAGS) + [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "pre", "code", "blockquote",
    "ul", "ol", "li",
    "table", "thead", "tbody", "tr", "th", "td",
    "img", "figure", "figcaption",
    "a", "strong", "em", "del", "sup",
    "div", "span",
    "dl", "dt", "dd",
    "input",
]

ALLOWED_ATTRS = {
    **dict(bleach.ALLOWED_ATTRIBUTES),
    "img": ["src", "alt", "title", "loading"],
    "a": ["href", "title", "rel"],
    "code": ["class"],
    "span": ["class"],
    "div": ["class", "id"],
    "pre": ["class"],
    "input": ["type", "checked", "disabled"],
    "th": ["align"],
    "td": ["align"],
    "h1": ["id"],
    "h2": ["id"],
    "h3": ["id"],
    "h4": ["id"],
}

MD_EXTENSIONS = [
    "markdown.extensions.tables",
    "markdown.extensions.fenced_code",
    "markdown.extensions.footnotes",
    "markdown.extensions.toc",
    "markdown.extensions.meta",
    "markdown.extensions.codehilite",
    "markdown.extensions.smarty",
]

MD_EXTENSION_CONFIGS = {
    "markdown.extensions.codehilite": {
        "css_class": "highlight",
        "guess_lang": False,
    },
    "markdown.extensions.toc": {
        "permalink": "\u00a0#",
        "permalink_class": "anchor-link",
        "toc_depth": "2-4",
    },
}


def convert_obsidian_links(text: str) -> str:
    """Convert Obsidian-specific syntax to standard markdown.

    Handles:
    - ![[image.png]] -> ![](image.png)
    - [[Note Title]] -> [Note Title](/post/note-title)
    """
    from slugify import slugify

    # Image embeds: ![[image.png]]
    text = re.sub(
        r"!\[\[([^\]]+\.(png|jpg|jpeg|webp|gif))\]\]",
        r"![](\1)",
        text,
    )

    # Wikilinks: [[Note Title]] or [[Note Title|Display Text]]
    def _replace_wikilink(match: re.Match) -> str:
        content = match.group(1)
        if "|" in content:
            target, display = content.split("|", 1)
        else:
            target = display = content
        slug = slugify(target.strip())
        return f"[{display.strip()}](/post/{slug})"

    text = re.sub(r"\[\[([^\]]+)\]\]", _replace_wikilink, text)
    return text


def render_markdown(text: str) -> tuple[str, str]:
    """Render markdown to sanitized HTML.

    Returns:
        Tuple of (body_html, toc_html).
    """
    text = convert_obsidian_links(text)

    md = markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
    )
    html = md.convert(text)
    toc = getattr(md, "toc", "")

    # Sanitize
    html = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
    toc = bleach.clean(toc, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)

    return html, toc


def extract_summary(html: str, length: int = 160) -> str:
    """Extract plain-text summary from HTML."""
    text = bleach.clean(html, tags=[], strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > length:
        return text[:length].rsplit(" ", 1)[0] + "..."
    return text

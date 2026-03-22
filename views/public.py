"""Public-facing views."""

from __future__ import annotations

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    render_template,
    request,
    url_for,
)

from models import Post, Tag, db

public = Blueprint("public", __name__)


@public.route("/")
def index():
    """Homepage with paginated posts."""
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["POSTS_PER_PAGE"]
    pagination = (
        Post.query.filter_by(is_published=True)
        .order_by(Post.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template("index.html", posts=pagination.items, pagination=pagination)


@public.route("/post/<slug>")
def post_detail(slug: str):
    """Single post page."""
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("post.html", post=post)


@public.route("/tags")
def tags_page():
    """Page listing all tags with post counts, removing empty ones."""
    tags = Tag.query.all()
    empty_tags = [t for t in tags if not any(p.is_published for p in t.posts)]
    for t in empty_tags:
        db.session.delete(t)
    if empty_tags:
        db.session.commit()
    tags = [t for t in tags if t not in empty_tags]
    return render_template("tags.html", tags=tags)


@public.route("/tag/<slug>")
def tag_posts(slug: str):
    """Posts filtered by tag."""
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["POSTS_PER_PAGE"]
    pagination = (
        Post.query.filter(Post.tags.contains(tag), Post.is_published == True)
        .order_by(Post.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template("tag.html", tag=tag, posts=pagination.items, pagination=pagination)


@public.route("/feed.xml")
def rss_feed():
    """RSS 2.0 feed."""
    posts = (
        Post.query.filter_by(is_published=True)
        .order_by(Post.created_at.desc())
        .limit(20)
        .all()
    )
    site_url = current_app.config["SITE_URL"]
    site_name = current_app.config["SITE_NAME"]
    site_desc = current_app.config["SITE_DESCRIPTION"]

    items = []
    for p in posts:
        link = f"{site_url}/post/{p.slug}"
        pub_date = p.created_at.strftime("%a, %d %b %Y %H:%M:%S +0000")
        items.append(
            f"<item>"
            f"<title>{_escape_xml(p.title)}</title>"
            f"<link>{link}</link>"
            f"<guid>{link}</guid>"
            f"<pubDate>{pub_date}</pubDate>"
            f"<description>{_escape_xml(p.summary)}</description>"
            f"</item>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">'
        "<channel>"
        f"<title>{_escape_xml(site_name)}</title>"
        f"<link>{site_url}</link>"
        f"<description>{_escape_xml(site_desc)}</description>"
        f'<atom:link href="{site_url}/feed.xml" rel="self" type="application/rss+xml"/>'
        + "".join(items)
        + "</channel></rss>"
    )
    return Response(xml, mimetype="application/rss+xml")


def _escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

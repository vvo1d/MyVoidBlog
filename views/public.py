"""Public-facing views."""

from __future__ import annotations

from datetime import datetime, timezone

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
    url_for,
)

from models import Comment, Post, PostView, Tag, db

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

    # Unique view per IP
    ip = request.remote_addr or "unknown"
    existing = PostView.query.filter_by(post_id=post.id, ip=ip).first()
    if not existing:
        db.session.add(PostView(post_id=post.id, ip=ip))
        post.view_count = (post.view_count or 0) + 1
        db.session.commit()

    # Related posts: same tags, excluding current
    related = []
    if post.tags:
        tag_ids = [t.id for t in post.tags]
        related = (
            Post.query.filter(
                Post.id != post.id,
                Post.is_published == True,
                Post.tags.any(Tag.id.in_(tag_ids)),
            )
            .order_by(Post.created_at.desc())
            .limit(3)
            .all()
        )

    return render_template("post.html", post=post, related=related)


@public.route("/post/<slug>/comment", methods=["POST"])
def add_comment(slug: str):
    """Add a comment to a post."""
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()

    author = request.form.get("author", "").strip()
    text = request.form.get("text", "").strip()

    if not author or not text:
        return jsonify({"error": "Имя и текст обязательны."}), 400

    if len(author) > 80:
        author = author[:80]
    if len(text) > 5000:
        text = text[:5000]

    comment = Comment(post_id=post.id, author=author, text=text)
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "id": comment.id,
        "author": comment.author,
        "text": comment.text,
        "created_at": comment.created_at.strftime("%d.%m.%Y %H:%M"),
    })


@public.route("/search")
def search():
    """Search posts by title and content."""
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify([])

    posts = (
        Post.query.filter(
            Post.is_published == True,
            db.or_(
                Post.title.ilike(f"%{q}%"),
                Post.body_md.ilike(f"%{q}%"),
            ),
        )
        .order_by(Post.created_at.desc())
        .limit(10)
        .all()
    )

    return jsonify([
        {
            "title": p.title,
            "slug": p.slug,
            "summary": p.summary[:120],
            "date": p.created_at.strftime("%d.%m.%Y"),
            "url": url_for("public.post_detail", slug=p.slug),
        }
        for p in posts
    ])


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

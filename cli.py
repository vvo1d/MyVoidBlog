"""CLI commands for blog management."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import click
import yaml
from flask import Flask
from slugify import slugify

from markdown_renderer import extract_summary, render_markdown
from models import Post, Tag, User, db


def register_cli(app: Flask) -> None:
    """Register CLI commands with the app."""

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(username: str, password: str) -> None:
        """Create an admin user."""
        if User.query.filter_by(username=username).first():
            click.echo(f"User '{username}' already exists.")
            return
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Admin user '{username}' created.")

    @app.cli.command("sync")
    def sync_posts_cmd() -> None:
        """Sync posts from content/ directory (Obsidian vault)."""
        count = _sync_posts(app)
        click.echo(f"Synced {count} posts.")


def _sync_posts(app: Flask) -> int:
    """Scan content/ folder, parse frontmatter, create/update posts.

    Returns:
        Number of posts processed.
    """
    content_dir: Path = app.config["CONTENT_DIR"]
    static_uploads: Path = app.config["STATIC_UPLOAD_DIR"]
    static_uploads.mkdir(parents=True, exist_ok=True)

    if not content_dir.exists():
        return 0

    # Copy images
    images_dir = content_dir / "images"
    if images_dir.exists():
        for img in images_dir.iterdir():
            if img.is_file():
                dest = static_uploads / img.name
                if not dest.exists() or img.stat().st_mtime > dest.stat().st_mtime:
                    shutil.copy2(img, dest)

    count = 0
    for md_file in content_dir.glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)
        if not meta.get("title"):
            continue

        title = meta["title"]
        slug = slugify(title)
        tag_names = meta.get("tags", [])
        cover = meta.get("cover", "")
        is_published = meta.get("published", False)
        created = meta.get("date")

        # Fix image paths in body to point to static/uploads/
        body = body.replace("](images/", "](/static/uploads/")
        body = body.replace("](./images/", "](/static/uploads/")

        body_html, _ = render_markdown(body)
        summary = extract_summary(body_html)

        post = Post.query.filter_by(slug=slug).first()
        if post:
            post.title = title
            post.body_md = body
            post.body_html = body_html
            post.summary = summary
            post.cover_image = cover
            post.is_published = is_published
            post.updated_at = datetime.now(timezone.utc)
        else:
            post = Post(
                title=title,
                slug=slug,
                body_md=body,
                body_html=body_html,
                summary=summary,
                cover_image=cover,
                is_published=is_published,
            )
            if created:
                if isinstance(created, str):
                    created = datetime.fromisoformat(created).replace(tzinfo=timezone.utc)
                elif isinstance(created, datetime):
                    if created.tzinfo is None:
                        created = created.replace(tzinfo=timezone.utc)
                post.created_at = created
            db.session.add(post)

        # Handle cover path
        if cover and not cover.startswith("/"):
            post.cover_image = f"/static/uploads/{Path(cover).name}"

        post.tags = [Tag.get_or_create(name) for name in tag_names]
        count += 1

    db.session.commit()
    return count


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown text.

    Returns:
        Tuple of (metadata dict, body text without frontmatter).
    """
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}

    body = parts[2].strip()
    return meta, body

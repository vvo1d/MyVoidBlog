"""Admin panel views."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from images import allowed_file, process_image
from markdown_renderer import extract_summary, render_markdown
from models import Post, Tag, User, db

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/login", methods=["GET", "POST"])
def login():
    """Admin login page."""
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for("admin.dashboard"))
        flash("Неверные учётные данные.", "error")

    return render_template("admin/login.html")


@admin.route("/logout")
@login_required
def logout():
    """Logout admin."""
    logout_user()
    return redirect(url_for("public.index"))


@admin.route("/")
@login_required
def dashboard():
    """Admin dashboard with post list."""
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("admin/dashboard.html", posts=posts)


@admin.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    """Create a new post."""
    if request.method == "POST":
        return _save_post(None)
    return render_template("admin/editor.html", post=None, tags=Tag.query.all())


@admin.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id: int):
    """Edit an existing post."""
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        return _save_post(post)
    return render_template("admin/editor.html", post=post, tags=Tag.query.all())


@admin.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
    """Delete a post."""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Пост удалён.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route("/post/<int:post_id>/toggle", methods=["POST"])
@login_required
def toggle_publish(post_id: int):
    """Toggle published status."""
    post = Post.query.get_or_404(post_id)
    post.is_published = not post.is_published
    db.session.commit()
    status = "опубликован" if post.is_published else "черновик"
    flash(f"Пост отмечен как {status}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Image upload page and API endpoint."""
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            return jsonify({"error": "No file provided"}), 400

        allowed = current_app.config["ALLOWED_EXTENSIONS"]
        if not allowed_file(file.filename, allowed):
            return jsonify({"error": "File type not allowed"}), 400

        upload_dir = current_app.config["STATIC_UPLOAD_DIR"]
        filename, thumb = process_image(
            file,
            upload_dir,
            max_width=current_app.config["MAX_IMAGE_WIDTH"],
            thumb_width=current_app.config["THUMBNAIL_WIDTH"],
        )
        image_url = url_for("static", filename=f"uploads/{filename}")
        thumb_url = url_for("static", filename=f"uploads/{thumb}")
        return jsonify({"url": image_url, "thumbnail": thumb_url})

    return render_template("admin/upload.html")


@admin.route("/sync", methods=["POST"])
@login_required
def sync_obsidian():
    """Trigger Obsidian sync from admin panel."""
    from cli import _sync_posts

    count = _sync_posts(current_app)
    flash(f"Синхронизировано постов: {count}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route("/import", methods=["POST"])
@login_required
def import_md():
    """Import a single .md file."""
    file = request.files.get("file")
    if not file or not file.filename or not file.filename.endswith(".md"):
        flash("Загрузите файл .md.", "error")
        return redirect(url_for("admin.new_post"))

    content = file.read().decode("utf-8")
    return render_template(
        "admin/editor.html",
        post=None,
        tags=Tag.query.all(),
        imported_content=content,
    )


def _save_post(post: Post | None):
    """Save or update a post from form data."""
    title = request.form.get("title", "").strip()
    body_md = request.form.get("body_md", "")
    cover_image = request.form.get("cover_image", "")
    is_published = request.form.get("is_published") == "on"
    tag_names = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]

    if not title:
        flash("Заголовок обязателен.", "error")
        return redirect(request.url)

    body_html, _ = render_markdown(body_md)
    summary = extract_summary(body_html)

    if post is None:
        post = Post(title=title)
        post.generate_slug()
        db.session.add(post)
    else:
        post.title = title
        post.generate_slug()

    post.body_md = body_md
    post.body_html = body_html
    post.summary = summary
    post.cover_image = cover_image
    post.is_published = is_published
    post.updated_at = datetime.now(timezone.utc)

    post.tags = [Tag.get_or_create(name) for name in tag_names]

    db.session.commit()
    flash("Пост сохранён.", "success")
    return redirect(url_for("admin.edit_post", post_id=post.id))

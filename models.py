"""Database models."""

from __future__ import annotations

from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from slugify import slugify
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

# Many-to-many association table
post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class User(UserMixin, db.Model):  # type: ignore[name-defined]
    """Admin user model."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Tag(db.Model):  # type: ignore[name-defined]
    """Tag model."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)

    @staticmethod
    def get_or_create(name: str) -> "Tag":
        """Get existing tag or create a new one."""
        slug = slugify(name)
        tag = Tag.query.filter_by(slug=slug).first()
        if not tag:
            tag = Tag(name=name, slug=slug)
            db.session.add(tag)
        return tag


class Post(db.Model):  # type: ignore[name-defined]
    """Blog post model."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    body_md = db.Column(db.Text, nullable=False, default="")
    body_html = db.Column(db.Text, nullable=False, default="")
    summary = db.Column(db.String(300), default="")
    cover_image = db.Column(db.String(300), default="")
    is_published = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    tags = db.relationship("Tag", secondary=post_tags, backref="posts", lazy="select")

    def generate_slug(self) -> None:
        """Generate URL-friendly slug from title."""
        self.slug = slugify(self.title)

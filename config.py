"""Application configuration."""

import os
from pathlib import Path

basedir = Path(__file__).resolve().parent


class Config:
    """Base configuration."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", f"sqlite:///{basedir / 'blog.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Paths
    CONTENT_DIR: Path = basedir / "content"
    UPLOAD_DIR: Path = basedir / "uploads"
    STATIC_UPLOAD_DIR: Path = basedir / "static" / "uploads"

    # Images
    MAX_IMAGE_WIDTH: int = 1200
    THUMBNAIL_WIDTH: int = 400
    ALLOWED_EXTENSIONS: set[str] = {"jpg", "jpeg", "png", "webp"}
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB

    # Pagination
    POSTS_PER_PAGE: int = 10

    # Site meta
    SITE_NAME: str = os.environ.get("SITE_NAME", "Void Blog")
    SITE_URL: str = os.environ.get("SITE_URL", "http://localhost:5000")
    SITE_DESCRIPTION: str = os.environ.get("SITE_DESCRIPTION", "Personal blog")

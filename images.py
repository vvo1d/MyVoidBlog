"""Image processing utilities."""

from __future__ import annotations

import uuid
from pathlib import Path

from PIL import Image
from werkzeug.datastructures import FileStorage


def allowed_file(filename: str, allowed: set[str]) -> bool:
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def process_image(
    file: FileStorage,
    upload_dir: Path,
    max_width: int = 1200,
    thumb_width: int = 400,
) -> tuple[str, str]:
    """Save uploaded image with resize and thumbnail.

    Returns:
        Tuple of (filename, thumbnail_filename).
    """
    ext = file.filename.rsplit(".", 1)[1].lower() if file.filename else "jpg"
    if ext == "jpeg":
        ext = "jpg"
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    thumb_name = f"thumb_{unique_name}"

    upload_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(file.stream)

    # Convert RGBA to RGB for JPEG
    if img.mode == "RGBA" and ext == "jpg":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg

    # Full-size image
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

    save_kwargs: dict = {}
    if ext == "webp":
        save_kwargs["quality"] = 85
    elif ext == "jpg":
        save_kwargs["quality"] = 90
        save_kwargs["optimize"] = True

    img.save(upload_dir / unique_name, **save_kwargs)

    # Thumbnail
    if img.width > thumb_width:
        ratio = thumb_width / img.width
        thumb = img.resize((thumb_width, int(img.height * ratio)), Image.LANCZOS)
    else:
        thumb = img.copy()

    thumb.save(upload_dir / thumb_name, **save_kwargs)

    return unique_name, thumb_name

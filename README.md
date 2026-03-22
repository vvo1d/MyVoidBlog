# MyVoidBlog

Personal blog on Flask with Obsidian integration.

## Quick Start

```bash
cd blog
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit SECRET_KEY

# Create admin user
flask create-admin

# Run dev server
flask run
```

## Obsidian Sync

Place `.md` files with YAML frontmatter in `content/`:

```yaml
---
title: My Post
date: 2025-03-20
tags: [python, flask]
cover: images/photo.jpg
published: true
---
```

Images go in `content/images/`. Then sync:

```bash
flask sync
```

Or use the "Sync Obsidian" button in the admin panel.

Supported Obsidian syntax:
- `![[image.png]]` → standard image embeds
- `[[Note Title]]` → links to posts by slug

## Docker

```bash
cp .env.example .env
docker compose up -d
docker compose exec blog flask create-admin
```

## Admin Panel

Navigate to `/admin/login`. Features:
- Create/edit/delete posts with split-view markdown editor
- Drag-and-drop image upload
- Publish/unpublish toggle
- Import single `.md` files
- One-click Obsidian sync

## Project Structure

```
blog/
├── app.py              # Application factory
├── config.py           # Configuration
├── models.py           # SQLAlchemy models
├── views/
│   ├── public.py       # Public routes (index, post, tag, RSS)
│   └── admin.py        # Admin routes (dashboard, editor, upload)
├── cli.py              # CLI commands (create-admin, sync)
├── markdown_renderer.py # Markdown → HTML with sanitization
├── images.py           # Image processing (resize, thumbnails)
├── content/            # Obsidian vault sync directory
├── templates/          # Jinja2 templates
└── static/             # CSS, JS, uploads
```

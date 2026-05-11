from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "blog-posts"
OUTPUT_DIR = ROOT / "notes"
SITE_URL = "https://JianhaiChen.github.io"


@dataclass
class Post:
  title: str
  slug: str
  date: str
  category: str
  summary: str
  body: str

  @property
  def url(self) -> str:
    return f"notes/{self.slug}.html"

  @property
  def full_url(self) -> str:
    return f"{SITE_URL}/{self.url}"

  @property
  def sort_date(self) -> datetime:
    return datetime.fromisoformat(self.date).replace(tzinfo=timezone.utc)


def parse_front_matter(text: str, path: Path) -> tuple[dict[str, str], str]:
  if not text.startswith("---\n"):
    raise ValueError(f"{path} must start with front matter delimited by ---")

  _, meta_text, body = text.split("---", 2)
  meta: dict[str, str] = {}
  for line in meta_text.strip().splitlines():
    if not line.strip():
      continue
    key, sep, value = line.partition(":")
    if not sep:
      raise ValueError(f"Invalid front matter line in {path}: {line}")
    meta[key.strip()] = value.strip().strip('"')
  return meta, body.strip()


def slugify(value: str) -> str:
  value = value.lower()
  value = re.sub(r"[^a-z0-9]+", "-", value)
  return value.strip("-") or "blog"


def load_posts() -> list[Post]:
  posts: list[Post] = []
  for path in sorted(SOURCE_DIR.glob("*.md")):
    if path.name == "README.md" or path.name == "template.md":
      continue
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path)
    title = meta["title"]
    posts.append(
      Post(
        title=title,
        slug=meta.get("slug") or slugify(title),
        date=meta["date"],
        category=meta.get("category", meta["date"]),
        summary=meta.get("summary", ""),
        body=body,
      )
    )
  return sorted(posts, key=lambda post: post.sort_date, reverse=True)


def inline_markdown(text: str) -> str:
  text = escape(text)
  text = re.sub(r"\*\*\_(.+?)\_\*\*", r"<strong><em>\1</em></strong>", text)
  text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
  text = re.sub(r"\_(.+?)\_", r"<em>\1</em>", text)
  text = re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', text)
  return text


def markdown_to_html(markdown: str) -> str:
  blocks: list[str] = []
  paragraph: list[str] = []

  def flush_paragraph() -> None:
    if paragraph:
      blocks.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
      paragraph.clear()

  for raw_line in markdown.splitlines():
    line = raw_line.strip()
    if not line:
      flush_paragraph()
      continue
    if line.startswith("## "):
      flush_paragraph()
      blocks.append(f"<h2>{inline_markdown(line[3:])}</h2>")
      continue
    if line.startswith("# "):
      flush_paragraph()
      blocks.append(f"<h2>{inline_markdown(line[2:])}</h2>")
      continue
    paragraph.append(line)

  flush_paragraph()
  return "\n        ".join(blocks)


def page_shell(title: str, eyebrow: str, lead: str, body_html: str) -> str:
  return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)} | Jian-Hai Chen</title>
    <link rel="stylesheet" href="../styles.css">
  </head>
  <body>
    <header class="site-header" aria-label="Site navigation">
      <a class="brand" href="../">
        <span class="brand-mark" aria-hidden="true">JC</span>
        <span>Jian-Hai Chen</span>
      </a>
      <nav class="nav-links" aria-label="Primary">
        <a href="../#about">About</a>
        <a href="../#research">Research</a>
        <a href="../#publications">Publications</a>
        <a href="./">Blogs</a>
      </nav>
    </header>

    <main>
      <article class="section-block note-page">
        <p class="eyebrow">{escape(eyebrow)}</p>
        <h1>{escape(title)}</h1>
        <p class="lead">{escape(lead)}</p>
        {body_html}
      </article>
    </main>

    <footer class="site-footer">
      <p>Jian-Hai Chen</p>
      <a href="./">Back to blogs</a>
    </footer>
  </body>
</html>
"""


def render_post(post: Post) -> None:
  body_html = markdown_to_html(post.body)
  (OUTPUT_DIR / f"{post.slug}.html").write_text(
    page_shell(post.title, post.category, post.summary, body_html),
    encoding="utf-8",
  )


def render_index(posts: list[Post]) -> None:
  items = "\n".join(
    f"""          <article class="note-item">
            <span>{escape(post.category)}</span>
            <h3><a href="{quote(post.slug)}.html">{escape(post.title)}</a></h3>
            <p>{escape(post.summary)}</p>
          </article>"""
    for post in posts
  )
  html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Blogs | Jian-Hai Chen</title>
    <link rel="stylesheet" href="../styles.css">
  </head>
  <body>
    <header class="site-header" aria-label="Site navigation">
      <a class="brand" href="../">
        <span class="brand-mark" aria-hidden="true">JC</span>
        <span>Jian-Hai Chen</span>
      </a>
      <nav class="nav-links" aria-label="Primary">
        <a href="../#about">About</a>
        <a href="../#research">Research</a>
        <a href="../#publications">Publications</a>
        <a href="./">Blogs</a>
      </nav>
    </header>

    <main>
      <section class="section-block">
        <div class="section-heading">
          <p class="eyebrow">Blogs</p>
          <h1>Short writing</h1>
          <p class="lead">Research blogs, short essays, project updates, and reading notes.</p>
        </div>
        <div class="notes-grid">
{items}
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <p>Jian-Hai Chen</p>
      <a href="../">Home</a>
    </footer>
  </body>
</html>
"""
  (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")


def render_blog_data(posts: list[Post]) -> None:
  data = [
    {
      "date": post.category,
      "title": post.title,
      "text": post.summary,
      "url": post.url,
    }
    for post in posts
  ]
  (ROOT / "blog-data.js").write_text(
    "window.BLOG_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
  )


def render_feed(posts: list[Post]) -> None:
  latest = posts[0].sort_date if posts else datetime.now(timezone.utc)
  items = "\n".join(
    f"""    <item>
      <title>{xml_escape(post.title)}</title>
      <link>{xml_escape(post.full_url)}</link>
      <guid>{xml_escape(post.full_url)}</guid>
      <pubDate>{format_datetime(post.sort_date)}</pubDate>
      <description>{xml_escape(post.summary)}</description>
    </item>"""
    for post in posts
  )
  feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>Jian-Hai Chen Blogs</title>
    <link>{SITE_URL}/notes/</link>
    <description>Research blogs, short essays, and updates from Jian-Hai Chen.</description>
    <language>en-us</language>
    <lastBuildDate>{format_datetime(latest)}</lastBuildDate>
{items}
  </channel>
</rss>
"""
  (ROOT / "feed.xml").write_text(feed, encoding="utf-8")


def main() -> None:
  OUTPUT_DIR.mkdir(exist_ok=True)
  posts = load_posts()
  for post in posts:
    render_post(post)
  render_index(posts)
  render_blog_data(posts)
  render_feed(posts)
  subprocess.run(["python3", "build_site_config.py"], cwd=ROOT, check=True)
  print(f"Built {len(posts)} blog post(s)")


if __name__ == "__main__":
  main()

# Jian-Hai Chen Academic Website

https://jianhaichen.github.io/

A hand-edited static site. No JavaScript, no data files, no build step for the
homepage: every word on the homepage is plain text inside `index.html`.

## Files

- `index.html` — the whole homepage: text, publications, links, JSON-LD
- `styles.css` — layout and visual design (shared with the blog pages)
- `assets/profile.jpg` — profile photo
- `blog-posts/*.md` — blog sources, the only files you edit for blogs
- `notes/` — generated blog pages, do not hand-edit
- `feed.xml` — generated RSS feed, do not hand-edit
- `build_blogs.py` — turns `blog-posts/*.md` into `notes/` and `feed.xml`
- `robots.txt`, `sitemap.xml` — search engine discovery
- `google2d2122f30cc65f98.html` — Google Search Console verification, do not delete

## Editing the homepage

Open `index.html` and change the words between the tags. Sections are marked
with `EDIT:` comments: About, Updates, Blogs, Research, Selected papers, Links.

Conventions:

- **Updates** (left card) are short news lines: one headline, one sentence.
- **Blogs** (right card) point at the essays in `notes/`.
- **Selected papers** are hand-maintained. The full list lives on Google
  Scholar; this page only shows a curated subset, so a new paper is one copied
  `<article class="featured-item">` block.

Then commit and push:

```bash
git add -A && git commit -m "Update homepage" && git push
```

GitHub Pages redeploys in about a minute.

## Adding a blog post

```bash
cp blog-posts/template.md blog-posts/my-new-post.md
```

Edit the front matter and body, then:

```bash
./publish.sh "Add new blog"
```

That rebuilds `notes/`, the blog index, and `feed.xml`, then commits and pushes.

Supported Markdown: paragraphs, `##` headings, `- ` lists, `> ` blockquotes,
`---` rules, `**bold**`, `_italic_`, and `[links](https://example.com)`.

**The homepage blog card is not rebuilt automatically.** After adding a post,
add a matching `compact-item` block to the Blogs card in `index.html` by hand.
This is the deliberate cost of keeping the homepage hand-editable.

## Search Console

The site is verified through the `google2d2122f30cc65f98.html` file. After
adding pages, resubmit `sitemap.xml` in Search Console so new URLs get crawled.

## Note on Google Scholar

An earlier version of this site pulled publications from a scraped copy of the
public Google Scholar profile. That scraper was removed: Google blocks requests
from GitHub Actions runners, and a failed run silently committed an empty
publication list. Publications are now written by hand in `index.html`.

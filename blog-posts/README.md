# Blog Source Files

Write blogs as Markdown files in this folder.

To add a new blog:

1. Copy `template.md` to a new file, for example `my-new-blog.md`.
2. Edit the title, date, summary, and body.
3. Run `./publish.sh "Add new blog"` from the site folder.

The build script will update the homepage blog card, `notes/index.html`, the generated blog HTML pages, and `feed.xml`.

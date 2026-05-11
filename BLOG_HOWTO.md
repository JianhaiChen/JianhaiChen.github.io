# 如何只改一个文本文件来更新博客

以后写博客，只需要改 `blog-posts/` 里面的 `.md` 文本文件。

## 新增一篇博客

```bash
cd /Users/cjh/Projects/JianhaiChen.github.io
cp blog-posts/template.md blog-posts/my-new-blog.md
```

然后打开 `blog-posts/my-new-blog.md`，修改开头的信息和正文：

```markdown
---
title: My blog title
slug: my-blog-title
date: 2026-05-10
category: Blog
summary: One short sentence for the homepage.
---

Write the blog here.
```

最后运行：

```bash
./publish.sh "Add new blog"
```

它会自动更新首页 Blogs、博客列表页、单篇网页和 RSS 订阅，然后推送到 GitHub。

## 修改已有博客

直接打开对应的文本文件，例如：

```bash
open blog-posts/south-asian-wild-boar-and-pig.md
```

改完后运行：

```bash
./publish.sh "Update blog"
```

不要手动修改 `notes/`、`blog-data.js`、`feed.xml`，这些文件都会自动生成。

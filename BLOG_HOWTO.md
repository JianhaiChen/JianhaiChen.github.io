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

它会自动更新博客列表页、单篇网页和 RSS 订阅，然后推送到 GitHub。

**首页那个 Blogs 卡片不会自动更新。** 新增博客后，还要手动打开 `index.html`，
在 Blogs 卡片里照着已有的 `compact-item` 复制一段。这是首页改成纯手写静态之后
的代价 —— 换来的是首页每个字都能直接改。

## 修改已有博客

直接打开对应的文本文件，例如：

```bash
open blog-posts/south-asian-wild-boar-and-pig.md
```

改完后运行：

```bash
./publish.sh "Update blog"
```

不要手动修改 `notes/` 和 `feed.xml`，这些文件都会自动生成。

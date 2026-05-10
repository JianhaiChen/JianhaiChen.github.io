# Jian-Hai Chen Academic Website

Static personal academic website built from the public Google Scholar profile:

https://scholar.google.com/citations?user=1-onMXMAAAAJ&hl=zh-CN

Open `index.html` in a browser to view the site. The page uses local static files only:

- `index.html` for structure
- `styles.css` for layout and visual design
- `data.js` for Scholar-derived profile/publication data
- `app.js` for metrics, selected papers, and citation charts
- `assets/profile.jpg` for the local profile image
- `notes/` for short articles and personal research notes

The public site keeps the publication section simple: it shows selected papers and links to the full Google Scholar profile.

## Google Scholar refresh

Google Scholar does not provide an official public API. This repository includes a lightweight scraper for the public profile page, but automated runs may occasionally fail if Google blocks the request.

Manual refresh:

```bash
python3 parse_scholar.py --fetch > scholar_data.json
python3 -c "from pathlib import Path; data=Path('scholar_data.json').read_text(encoding='utf-8'); Path('data.js').write_text('window.SCHOLAR_DATA = ' + data + ';\\n', encoding='utf-8')"
```

Automated refresh:

- GitHub Actions workflow: `.github/workflows/refresh-scholar.yml`
- Runs weekly on Monday
- Can also be started manually from GitHub -> Actions -> Refresh Google Scholar data -> Run workflow

## Notes

Short articles can be added under `notes/`. Copy `notes/template.html`, rename it, write the article, then add a link to `notes/index.html`.

## Publish

### GitHub Pages

Recommended for a durable academic homepage.

Automated path:

```bash
export GITHUB_TOKEN=YOUR_TOKEN
./deploy_github_pages.sh JianhaiChen
```

Manual path:

1. Create a public repository named `JianhaiChen.github.io`.
2. Upload `index.html`, `styles.css`, `app.js`, `data.js`, `.nojekyll`, `README.md`, and the `assets/` folder.
3. In the repository, open Settings -> Pages.
4. Select deployment from the `main` branch root.
5. Your site will be available at `https://JianhaiChen.github.io/`.

### Netlify

Fastest no-code option.

1. Go to https://app.netlify.com/drop.
2. Drag the website folder or `jianhai-chen-academic-site.zip` into the drop area.
3. Netlify will publish a free `netlify.app` URL.

### Other free static hosts

Vercel and Cloudflare Pages also work well. Connect a GitHub repository and they will redeploy after every push.

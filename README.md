# Jian-Hai Chen Academic Website

Static academic profile built from the public Google Scholar profile:

https://scholar.google.com/citations?user=1-onMXMAAAAJ&hl=zh-CN

Open `index.html` in a browser to view the site. The page uses local static files only:

- `index.html` for structure
- `styles.css` for layout and visual design
- `data.js` for Scholar-derived profile/publication data
- `app.js` for filtering, sorting, featured papers, and citation charts
- `assets/profile.jpg` for the local profile image

The site also includes a publication-based research trail and source panel built from public records on Google Scholar, ORCID, Nature, Genome Research, PLOS Genetics, Springer Nature, Frontiers, PubMed/PMC, and UChicago Knowledge. The history section is intentionally worded as a public-record research trail rather than a formal CV.

To refresh the data after downloading new Scholar HTML snapshots:

```bash
python3 parse_scholar.py > scholar_data.json
python3 -c "from pathlib import Path; data=Path('scholar_data.json').read_text(encoding='utf-8'); Path('data.js').write_text('window.SCHOLAR_DATA = ' + data + ';\\n', encoding='utf-8')"
```

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

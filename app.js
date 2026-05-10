const data = window.SCHOLAR_DATA;
const profile = data.profile;
const publications = data.publications;
const config = window.SITE_CONFIG;

const numberFormat = new Intl.NumberFormat("en-US");
const $ = (selector) => document.querySelector(selector);

function setText(selector, value) {
  const element = $(selector);
  if (element) element.textContent = value;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function highlightAuthor(text) {
  return text
    .replace(/\bJH Chen\b/g, "<strong>JH Chen</strong>")
    .replace(/\bJ Chen\b/g, "<strong>J Chen</strong>")
    .replace(/\bJianhai Chen\b/g, "<strong>Jianhai Chen</strong>");
}

function renderProfile() {
  document.title = config.name;
  setText(".brand span:last-child", config.name);
  setText("#hero-eyebrow", `${config.name} / ${config.aliases}`);
  setText("#hero-title", config.tagline);
  setText("#hero-bio", config.bio || "");
  setText("#profile-name", config.name);
  setText("#profile-affiliation", config.affiliation);
  setText("#metric-citations", numberFormat.format(profile.metrics.citations.all));
  setText("#metric-h", numberFormat.format(profile.metrics.hIndex.all));
  setText("#metric-i10", numberFormat.format(profile.metrics.i10Index.all));
  setText("#metric-publications", numberFormat.format(publications.length));

  const tagContainer = $("#profile-tags");
  tagContainer.innerHTML = profile.interests
    .map((interest) => `<span class="tag">${escapeHtml(interest)}</span>`)
    .join("");

  $("#hero-links").innerHTML = config.links.map((link) => `
    <a class="${link.primary ? "primary-link" : "secondary-link"}" href="${escapeHtml(link.url)}">${escapeHtml(link.label)}</a>
  `).join("");
}

function renderConfigSections() {
  $("#notice-list").innerHTML = (config.notices || []).map((item) => `
    <div class="compact-item">
      <span>${escapeHtml(item.date)}</span>
      <h3>${item.url ? `<a href="${escapeHtml(item.url)}">${escapeHtml(item.title)}</a>` : escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.text)}</p>
    </div>
  `).join("");

  $("#blog-list").innerHTML = (config.blog || []).map((item) => `
    <div class="compact-item">
      <span>${escapeHtml(item.date)}</span>
      <h3>${item.url ? `<a href="${escapeHtml(item.url)}">${escapeHtml(item.title)}</a>` : escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.text)}</p>
    </div>
  `).join("");

  $("#research-list").innerHTML = config.research.map((item) => `
    <article>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.text)}</p>
    </article>
  `).join("");

  $("#timeline-list").innerHTML = config.timeline.map((item) => `
    <article class="timeline-item">
      <span class="timeline-date">${escapeHtml(item.date)}</span>
      <div>
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.text)}</p>
      </div>
    </article>
  `).join("");

  $("#source-list").innerHTML = config.sources.map((source) => `
    <a class="source-item" href="${escapeHtml(source.url)}">
      <span>${escapeHtml(source.label)}</span>
      <strong>${escapeHtml(source.title)}</strong>
    </a>
  `).join("");
}

function renderFeatured() {
  const featured = [...publications]
    .sort((a, b) => b.citations - a.citations || Number(b.year) - Number(a.year))
    .slice(0, 4);

  $("#featured-list").innerHTML = featured.map((publication) => `
    <article class="featured-item">
      <div class="featured-meta">
        <span>${publication.year}</span>
        <span>${numberFormat.format(publication.citations)} citations</span>
      </div>
      <a class="featured-title" href="${escapeHtml(publication.url)}">${escapeHtml(publication.title)}</a>
      <p class="featured-authors">${highlightAuthor(escapeHtml(publication.authors))}</p>
      <p class="featured-venue">${escapeHtml(publication.venue)}</p>
    </article>
  `).join("");
}

function renderCitationChart() {
  const years = profile.citationYears;
  const values = profile.citationSeries.all;
  const max = Math.max(...values);
  $("#citation-chart").innerHTML = years.map((year, index) => {
    const value = values[index] || 0;
    const height = Math.max(4, Math.round((value / max) * 190));
    return `
      <div class="bar-wrap">
        <div class="bar" style="height:${height}px" title="${value} citations in ${year}"></div>
        <div class="bar-value">${value}</div>
        <div class="bar-year">${year}</div>
      </div>
    `;
  }).join("");
}

renderProfile();
renderConfigSections();
renderFeatured();

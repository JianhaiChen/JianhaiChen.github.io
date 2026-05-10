const data = window.SCHOLAR_DATA;
const profile = data.profile;
const publications = data.publications;

const state = {
  year: "all",
  sort: "year",
  query: "",
};

const numberFormat = new Intl.NumberFormat("en-US");

const $ = (selector) => document.querySelector(selector);

function setText(selector, value) {
  const element = $(selector);
  if (element) {
    element.textContent = value;
  }
}

function renderProfile() {
  setText("#profile-name", profile.name);
  setText("#profile-affiliation", "Scholar profile: University of California, Irvine");
  setText("#metric-citations", numberFormat.format(profile.metrics.citations.all));
  setText("#metric-h", numberFormat.format(profile.metrics.hIndex.all));
  setText("#metric-i10", numberFormat.format(profile.metrics.i10Index.all));
  setText("#metric-publications", numberFormat.format(publications.length));

  $("#scholar-link").href = profile.scholarUrl;

  const tagContainer = $("#profile-tags");
  tagContainer.innerHTML = profile.interests
    .map((interest) => `<span class="tag">${escapeHtml(interest)}</span>`)
    .join("");
}

function renderFeatured() {
  const featured = [...publications]
    .sort((a, b) => b.citations - a.citations || Number(b.year) - Number(a.year))
    .slice(0, 3);

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

function renderYearFilter() {
  const years = [...new Set(publications.map((publication) => publication.year))]
    .sort((a, b) => Number(b) - Number(a));
  const buttons = ["all", ...years].map((year) => {
    const label = year === "all" ? "All" : year;
    const active = state.year === year ? " active" : "";
    return `<button class="year-chip${active}" type="button" data-year="${year}">${label}</button>`;
  });
  $("#year-filter").innerHTML = buttons.join("");
}

function publicationMatches(publication) {
  const haystack = [
    publication.title,
    publication.authors,
    publication.venue,
    publication.year,
  ].join(" ").toLowerCase();
  const queryMatch = !state.query || haystack.includes(state.query);
  const yearMatch = state.year === "all" || publication.year === state.year;
  return queryMatch && yearMatch;
}

function sortedPublications(items) {
  return [...items].sort((a, b) => {
    if (state.sort === "citations") {
      return b.citations - a.citations || Number(b.year) - Number(a.year);
    }
    return Number(b.year) - Number(a.year) || b.citations - a.citations;
  });
}

function renderPublications() {
  const filtered = sortedPublications(publications.filter(publicationMatches));
  const noun = filtered.length === 1 ? "publication" : "publications";
  $("#publication-count").textContent = `${numberFormat.format(filtered.length)} ${noun}`;
  $("#publication-list").innerHTML = filtered.map((publication) => `
    <article class="publication-item">
      <div class="publication-year">${publication.year || "n.d."}</div>
      <div>
        <div class="publication-meta">
          <span>${numberFormat.format(publication.citations)} citations</span>
        </div>
        <a class="publication-title" href="${escapeHtml(publication.url)}">${escapeHtml(publication.title)}</a>
        <p class="publication-authors">${highlightAuthor(escapeHtml(publication.authors))}</p>
        <p class="publication-venue">${escapeHtml(publication.venue)}</p>
      </div>
    </article>
  `).join("");
}

function renderCitationChart() {
  const years = profile.citationYears;
  const values = profile.citationSeries.all;
  const max = Math.max(...values);
  $("#citation-chart").innerHTML = years.map((year, index) => {
    const value = values[index] || 0;
    const height = Math.max(4, Math.round((value / max) * 210));
    return `
      <div class="bar-wrap">
        <div class="bar" style="height:${height}px" title="${value} citations in ${year}"></div>
        <div class="bar-value">${value}</div>
        <div class="bar-year">${year}</div>
      </div>
    `;
  }).join("");
}

function bindEvents() {
  $("#publication-search").addEventListener("input", (event) => {
    state.query = event.target.value.trim().toLowerCase();
    renderPublications();
  });

  $("#year-filter").addEventListener("click", (event) => {
    const button = event.target.closest("[data-year]");
    if (!button) return;
    state.year = button.dataset.year;
    renderYearFilter();
    renderPublications();
  });

  document.querySelectorAll("[data-sort]").forEach((button) => {
    button.addEventListener("click", () => {
      state.sort = button.dataset.sort;
      document.querySelectorAll("[data-sort]").forEach((item) => {
        item.classList.toggle("active", item === button);
      });
      renderPublications();
    });
  });
}

function highlightAuthor(text) {
  return text
    .replace(/\bJH Chen\b/g, "<strong>JH Chen</strong>")
    .replace(/\bJ Chen\b/g, "<strong>J Chen</strong>")
    .replace(/\bJianhai Chen\b/g, "<strong>Jianhai Chen</strong>");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

renderProfile();
renderFeatured();
renderYearFilter();
renderPublications();
renderCitationChart();
bindEvents();

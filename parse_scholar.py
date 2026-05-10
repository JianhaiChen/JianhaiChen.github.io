from __future__ import annotations

import argparse
import html
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCHOLAR_URL = "https://scholar.google.com/citations?user=1-onMXMAAAAJ&hl=zh-CN"
PUBDATE_URL = "https://scholar.google.com/citations?hl=zh-CN&user=1-onMXMAAAAJ&view_op=list_works&sortby=pubdate&pagesize=100"
PROFILE_PATH = ROOT / "scholar_profile.html"
PUBDATE_PATH = ROOT / "scholar_pubdate.html"


ARGS = argparse.ArgumentParser(description="Parse Jian-Hai Chen Google Scholar profile.")
ARGS.add_argument("--fetch", action="store_true", help="Fetch Scholar HTML before parsing.")
args = ARGS.parse_args()


def fetch_url(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


if args.fetch or not PROFILE_PATH.exists() or not PUBDATE_PATH.exists():
    PROFILE_PATH.write_text(fetch_url(SCHOLAR_URL), encoding="utf-8")
    PUBDATE_PATH.write_text(fetch_url(PUBDATE_URL), encoding="utf-8")

PROFILE_HTML = PROFILE_PATH.read_text(encoding="utf-8", errors="ignore")
PUBDATE_HTML = PUBDATE_PATH.read_text(encoding="utf-8", errors="ignore")


def clean_text(value: str) -> str:
    value = html.unescape(value)
    value = value.replace("\u202a", "").replace("\u202c", "")
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def strip_tags(value: str) -> str:
    return clean_text(re.sub(r"<[^>]+>", "", value))


def attr_value(attrs: list[tuple[str, str | None]], name: str) -> str | None:
    for key, value in attrs:
        if key == name:
            return value
    return None


def class_has(attrs: list[tuple[str, str | None]], token: str) -> bool:
    classes = attr_value(attrs, "class") or ""
    return token in classes.split()


def id_is(attrs: list[tuple[str, str | None]], value: str) -> bool:
    return attr_value(attrs, "id") == value


class ScholarParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.profile: dict[str, object] = {
            "name": "",
            "otherNames": "",
            "affiliation": "",
            "verifiedEmail": "",
            "interests": [],
            "metrics": {},
            "citationYears": [],
            "citationSeries": {"all": [], "since2021": []},
            "photo": "",
            "scholarUrl": SCHOLAR_URL,
        }
        self.publications: list[dict[str, object]] = []
        self._capture_stack: list[dict[str, object]] = []
        self._in_interest = False
        self._in_metric_table = False
        self._metric_row_index = -1
        self._metric_cell_index = -1
        self._metric_label = ""
        self._metric_values: list[str] = []
        self._in_year_axis = False
        self._in_citation_bar = False
        self._citation_bar_alt = ""
        self._current_pub: dict[str, object] | None = None
        self._pub_gray_parts: list[str] = []
        self._in_pub_citations = False
        self._in_pub_year = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "meta" and attr_value(attrs, "property") == "og:image":
            self.profile["photo"] = html.unescape(attr_value(attrs, "content") or "")

        if tag == "div" and id_is(attrs, "gsc_prf_in"):
            self._push_capture("name")
        elif tag == "span" and id_is(attrs, "gs_prf_ion_txt"):
            self._push_capture("otherNames")
        elif tag == "div" and class_has(attrs, "gsc_prf_il"):
            if id_is(attrs, "gsc_prf_ivh"):
                self._push_capture("verifiedEmail")
            elif not self.profile["affiliation"]:
                self._push_capture("affiliation")
        elif tag == "a" and class_has(attrs, "gsc_prf_inta"):
            self._in_interest = True
            self._push_capture("interest")

        if tag == "table" and id_is(attrs, "gsc_rsb_st"):
            self._in_metric_table = True
        elif self._in_metric_table and tag == "tr":
            self._metric_row_index += 1
            self._metric_cell_index = -1
            self._metric_label = ""
            self._metric_values = []
        elif self._in_metric_table and tag in {"td", "th"}:
            self._metric_cell_index += 1
            self._push_capture("metric_cell")

        if tag == "span" and class_has(attrs, "gsc_g_t"):
            self._in_year_axis = True
            self._push_capture("citation_year")
        elif tag == "a" and class_has(attrs, "gsc_g_a"):
            self._in_citation_bar = True
            self._citation_bar_alt = attr_value(attrs, "href") or ""
            self._push_capture("citation_bar")

        if tag == "tr" and class_has(attrs, "gsc_a_tr"):
            self._current_pub = {
                "title": "",
                "authors": "",
                "venue": "",
                "year": "",
                "citations": 0,
                "url": "",
            }
            self._pub_gray_parts = []
        elif self._current_pub is not None and tag == "a" and class_has(attrs, "gsc_a_at"):
            href = attr_value(attrs, "href") or ""
            self._current_pub["url"] = "https://scholar.google.com" + html.unescape(href)
            self._push_capture("pub_title")
        elif self._current_pub is not None and tag == "div" and class_has(attrs, "gs_gray"):
            self._push_capture("pub_gray")
        elif self._current_pub is not None and tag == "a" and class_has(attrs, "gsc_a_ac"):
            self._in_pub_citations = True
            self._push_capture("pub_citations")
        elif self._current_pub is not None and tag == "span" and class_has(attrs, "gsc_a_h"):
            self._in_pub_year = True
            self._push_capture("pub_year")

    def handle_endtag(self, tag: str) -> None:
        if self._capture_stack and self._capture_stack[-1]["tag"] == tag:
            capture = self._capture_stack.pop()
            value = clean_text("".join(capture["text"]))
            kind = capture["kind"]
            if kind in {"name", "otherNames", "affiliation", "verifiedEmail"}:
                self.profile[kind] = value
            elif kind == "interest" and value:
                self.profile["interests"].append(value)
                self._in_interest = False
            elif kind == "metric_cell" and self._in_metric_table:
                if self._metric_cell_index == 0:
                    self._metric_label = value
                elif value:
                    self._metric_values.append(value)
            elif kind == "citation_year" and value:
                self.profile["citationYears"].append(value)
                self._in_year_axis = False
            elif kind == "citation_bar" and value:
                numbers = re.findall(r"\d+", self._citation_bar_alt + " " + value)
                if numbers:
                    self.profile["citationSeries"]["all"].append(int(numbers[-1]))
                self._in_citation_bar = False
            elif kind == "pub_title" and self._current_pub is not None:
                self._current_pub["title"] = value
            elif kind == "pub_gray" and self._current_pub is not None and value:
                self._pub_gray_parts.append(value)
            elif kind == "pub_citations" and self._current_pub is not None:
                self._current_pub["citations"] = int(value) if value.isdigit() else 0
                self._in_pub_citations = False
            elif kind == "pub_year" and self._current_pub is not None:
                self._current_pub["year"] = value
                self._in_pub_year = False

        if tag == "table" and self._in_metric_table:
            self._in_metric_table = False
        elif tag == "tr" and self._in_metric_table and self._metric_label and self._metric_values:
            key_map = {
                "引用": "citations",
                "引用次数": "citations",
                "h 指数": "hIndex",
                "i10 指数": "i10Index",
            }
            key = key_map.get(self._metric_label)
            if key:
                self.profile["metrics"][key] = {
                    "all": int(self._metric_values[0]),
                    "since2021": int(self._metric_values[1]) if len(self._metric_values) > 1 else None,
                }
        elif tag == "tr" and self._current_pub is not None:
            self._current_pub["authors"] = self._pub_gray_parts[0] if self._pub_gray_parts else ""
            self._current_pub["venue"] = self._pub_gray_parts[1] if len(self._pub_gray_parts) > 1 else ""
            if self._current_pub["title"]:
                self.publications.append(self._current_pub)
            self._current_pub = None
            self._pub_gray_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_stack:
            self._capture_stack[-1]["text"].append(data)

    def handle_entityref(self, name: str) -> None:
        if self._capture_stack:
            self._capture_stack[-1]["text"].append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._capture_stack:
            self._capture_stack[-1]["text"].append(f"&#{name};")

    def _push_capture(self, kind: str) -> None:
        self._capture_stack.append({"kind": kind, "tag": self.get_starttag_text().split()[0][1:], "text": []})


parser = ScholarParser()
parser.feed(PROFILE_HTML)
parser.feed(PUBDATE_HTML)

for field in ("interests", "citationYears"):
    deduped = []
    for value in parser.profile[field]:
        if value not in deduped:
            deduped.append(value)
    parser.profile[field] = deduped

for key, values in parser.profile["citationSeries"].items():
    midpoint = len(values) // 2
    if midpoint and values[:midpoint] == values[midpoint:]:
        parser.profile["citationSeries"][key] = values[:midpoint]

seen: set[tuple[str, str]] = set()
publications = []
for publication in parser.publications:
    key = (str(publication["title"]), str(publication["year"]))
    if key not in seen:
        seen.add(key)
        publications.append(publication)

publications.sort(key=lambda item: (int(item["year"] or 0), int(item["citations"])), reverse=True)

output = {
    "profile": parser.profile,
    "publications": publications,
}

print(json.dumps(output, ensure_ascii=False, indent=2))

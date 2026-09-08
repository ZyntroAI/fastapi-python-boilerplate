Title: Free Research Toolkit — 2026 Edition
Kicker: Fact-checked guide to genuinely free tools for academic & professional research
Theme: dark
Genre: sop

# Free Research Toolkit — 2026 Edition

A practical, verified stack of **free** tools for academic and professional research: literature search, citation management, bibliometric visualization, writing, and open-science hosting.

> **Fact-checked 2026-09.** Every claim and link below was verified against each tool's live site or API. Where a tool is genuinely unlimited it says so — and where it has real limits (storage quotas, API rate limits), those are stated honestly rather than hidden. No tool here requires a credit card for the tier described.

## Table of Contents

1. [Literature Search & Discovery](#1-literature-search--discovery)
2. [Reference & Citation Management](#2-reference--citation-management)
3. [Bibliometric Visualization](#3-bibliometric-visualization)
4. [Academic Writing](#4-academic-writing)
5. [Open-Science Hosting](#5-open-science-hosting)
6. [End-to-End Workflow](#6-end-to-end-workflow)
7. [Install Notes](#7-install-notes)
8. [Honest Limits & Troubleshooting](#8-honest-limits--troubleshooting)

## 1. Literature Search & Discovery

### Semantic Scholar
- **Site:** <https://www.semanticscholar.org/> · **API docs:** <https://www.semanticscholar.org/product/api/tutorial>
- Database of **200M+** papers with AI summaries, key findings, and citation graphs.
- Searchable **without an account**. Optional free account adds saving, folders, and alerts.
- **Python:** `pip install semanticscholar`

```python
import semanticscholar as sch
paper = sch.paper("10.1038/nature12345")
print(paper["title"], paper["abstract"])
```

- **API base:** `https://api.semanticscholar.org/graph/v1` — verified live (a real paper resolves).
- ⚠️ **Rate limit:** unauthenticated API is capped at **100 requests / 5 minutes** (shared pool). Add delays or retries in bulk scripts — see §8.

### Google Scholar
- **Site:** <https://scholar.google.com/>
- Broad cross-discipline coverage; direct links to full text when open-access or via your institution.
- Cite button (BibTeX / APA / MLA), citation tracking, related-work suggestions.
- **No login needed** to search. Save results to "My library" and set email alerts with an account.
- Advanced operators: `author:"Name"`, `title:"Keywords"`, `year:2020-2026`.
- ⚠️ Google Scholar has **no official public API**. Automated scraping is against its ToS and often bot-blocked — use it interactively, not in scripts.

### PubMed
- **Site:** <https://pubmed.gov/> · **Help:** <https://pubmed.ncbi.nlm.nih.gov/help/>
- **40M+** biomedical/life-science citations, maintained by the U.S. NIH/NLM.
- Full-text links via PubMed Central; MeSH indexing for precise search.
- Filter by **"Free full text available"** for instant access.
- **API:** NCBI E-utilities (free, no key needed for light use):

```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=diabetes&retmax=5"
```

- ⚠️ **Rate limit:** E-utilities allows **3 requests/second** without an API key (10/sec with a free key). Insert `sleep 0.34` between calls in loops.

### OpenAlex
- **Site:** <https://openalex.org/> · **API docs:** <https://developers.openalex.org/>
- Fully **open data** knowledge graph — now **~327 million works** (verified live, Sep 2026), covering papers, authors, institutions, journals, and concepts.
- Web search works with no login. A free API key is optional (raises your rate ceiling) but **not required** to read data.
- **API example:**

```bash
curl "https://api.openalex.org/works?search=quantum%20computing"
```

- ⚠️ Polite pool without a key is ~**10 requests/second** (shared). Registering a free key raises this and gives you a dedicated pool — recommended for bulk pulls.

## 2. Reference & Citation Management

### Zotero
- **Download:** <https://www.zotero.org/download/> · **Docs:** <https://www.zotero.org/support/>
- Open-source reference manager, free forever.
- **Unlimited references and unlimited local storage.** The 300 MB figure applies *only* to free **cloud sync** (see §8) — your local library has no cap.
- Browser connectors for Chrome/Firefox/Edge/Safari; one-click import from major databases.
- Word / Google Docs / LibreOffice integration.

## 3. Bibliometric Visualization

### VOSviewer
- **Home / Download:** <https://www.vosviewer.com/> (use the homepage; there is no stable direct `/download/VOSviewer.zip` URL)
- Free desktop software (no watermark, no limit) for mapping co-authorship, co-citation, and keywords; cluster, density, and overlay views.
- Imports from Scopus, Web of Science, PubMed, Zotero, and CSV; handles 100k+ items.
- ⚠️ **Prerequisite:** Java 8+ runtime. Get the official installer from the VOSviewer site, not third-party mirrors.

## 4. Academic Writing

### Google Docs
- **Editor:** <https://docs.google.com/>
- Unlimited documents, real-time collaboration, cloud sync.
- Zotero citation integration via the Zotero connector. Export to Word/PDF.

## 5. Open-Science Hosting

### OSF (Open Science Framework)
- **Platform:** <https://osf.io/>
- Free project hosting for research: pre-registration, file versioning, audit logs, DOI assignment for public work, and integrations with GitHub, Zotero, Dataverse, and more.
- ⚠️ **Not unlimited.** OSF's free tier gives a **generous per-project storage quota** (roughly 5 GB of free storage), not infinite space. Large datasets are better stored externally (Drive/S3) and *linked* into the project. Exact quotas can change — check <https://osf.io/> before relying on a number.

## 6. End-to-End Workflow

1. **SEARCH** — Semantic Scholar / Google Scholar / PubMed / OpenAlex → export RIS/BibTeX.
2. **ORGANIZE** — Zotero: import → tag → folder → annotate.
3. **VISUALIZE** — VOSviewer: load your Zotero/CSV export → build the citation/co-occurrence network.
4. **WRITE** — Google Docs: insert citations from Zotero → generate the bibliography.
5. **SHARE** — OSF: upload manuscript + data → get a DOI → open access.

## 7. Install Notes

Desktop tools (Zotero, VOSviewer) ship OS-specific installers that change URL with each release, so **always download from the official pages above** rather than pinning a versioned file path:

- **Zotero:** <https://www.zotero.org/download/>
- **VOSviewer:** <https://www.vosviewer.com/> (Java 8+ required first)

Command-line (auto/managed) installs are best done through each OS's package manager so versions stay current:

```bash
# macOS (Homebrew)
brew install --cask zotero      # reference manager
brew install --cask temurin     # Java runtime (for VOSviewer)

# Ubuntu/Debian (via apt for Java; Zotero offers a .deb from its site)
sudo apt install default-jre    # Java for VOSviewer
```

> The original guide's hardcoded `Zotero-7.0.18.tar.bz2` and `/download/VOSviewer.zip` URLs are **outdated/broken** — do not use them.

## 8. Honest Limits & Troubleshooting

| Tool | What's truly free | Real limit to respect |
|---|---|---|
| Semantic Scholar | Full search + API | **100 req / 5 min** unauthenticated |
| Google Scholar | Full search | No official API; scraping blocked |
| PubMed | Full search + E-utilities | ~**3 req/s** without key |
| OpenAlex | Full open data + API | ~**10 req/s** shared pool (free key raises it) |
| Zotero | Unlimited refs + **local** storage | Free cloud **sync** capped at **300 MB** |
| VOSviewer | Full desktop features | Needs Java 8+ |
| Google Docs | Unlimited documents | Standard Google account limits |
| OSF | Free project hosting | Per-project storage **quota** (~5 GB free), not unlimited |

**Troubleshooting**

- **Semantic Scholar 429/rate-limited in a bulk script** — respect the 100-per-5-min pool: add `time.sleep(3)` and retry-on-429 with backoff; or register for a higher-tier key if available.
- **Zotero sync "storage full"** — the 300 MB limit is *cloud sync only*. Keep attachments local (no sync) or export, or upgrade storage. Your reference library itself is never capped.
- **VOSviewer won't launch** — missing/broken Java. Install a current JRE (Java 8+) from a trusted source, then relaunch.
- **Google Scholar auto-queries fail** — expected. Scholar has no API and blocks bots; use it in the browser.
- **OSF says "storage exceeded"** — move large files to Drive/S3 and add them as *links*, which do not count against the project quota.

### Summary

- **Search:** Semantic Scholar + Google Scholar + PubMed + OpenAlex
- **Library:** Zotero (local, unlimited)
- **Visualize:** VOSviewer
- **Write:** Google Docs
- **Host:** OSF

All core functionality is free with no trial or credit card. The "unlimited" framing in the original guide was overstated in a few places — the table in §8 shows exactly where real limits live so you can plan bulk work accordingly.

/**
 * Official documentation registry — single source of truth.
 * ZyntroAI standard: v1.2.0-origin
 *
 * Every URL in OFFICIAL_DOCS was verified with a live HTTP request and the
 * verification date is recorded in VERIFIED_ON. URLs the original brief cited
 * that do NOT resolve are kept in CORRECTED_LINKS together with their
 * replacement, so the audit trail survives the correction.
 *
 * Consumers:
 *   - frontend:  Company.jsx imports OFFICIAL_DOCS / analyze / getSourceDoc
 *   - backend:   official_docs.py reads the generated official-docs.json
 *   - CI:        verify_links.py re-checks every URL
 */

export const REGISTRY_VERSION = "1.2.0-origin";
export const VERIFIED_ON = "2026-09-14";

export const LINK_STATUS = {
  LIVE: "live",
  REPLACED: "replaced",
  REMOVED: "removed",
};

export const IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "webp", "gif", "svg", "avif"];

export const OFFICIAL_DOCS = {
  fastapi: {
    name: "FastAPI Official",
    label: "Core Framework",
    source: "FastAPI",
    links: [
      { id: "docs", label: "Official Docs", url: "https://fastapi.tiangolo.com/" },
      { id: "repo", label: "GitHub Repo", url: "https://github.com/tiangolo/fastapi" },
      { id: "advanced", label: "Advanced Guide", url: "https://fastapi.tiangolo.com/advanced/" },
    ],
  },
  python: {
    name: "Python Docs",
    label: "Language Reference",
    source: "Python",
    links: [{ id: "docs", label: "Python 3 Docs", url: "https://docs.python.org/3/" }],
  },
  fig: {
    name: "FIG Platform",
    label: "Asset Source",
    source: "FIG",
    links: [
      { id: "site", label: "Official Site", url: "https://hellofig.app/" },
      { id: "share", label: "Share / Assets", url: "https://share.hellofig.app/" },
    ],
  },
  dola: {
    name: "Dola AI Vision",
    label: "Image Intelligence",
    source: "Dola",
    links: [
      { id: "site", label: "Dola AI", url: "https://dola.ai/" },
      {
        id: "image-analysis",
        label: "Image Analysis Docs",
        url: "https://dola.ai/docs/features/image-analysis",
      },
      { id: "api", label: "API Reference", url: "https://dola.ai/api-reference" },
    ],
  },
  zyntroai: {
    name: "ZyntroAI Origin Standard",
    label: "Internal Standard",
    source: "ZyntroAI",
    links: [
      {
        id: "origin",
        label: "Origin Branch",
        url: "https://github.com/ZyntroAI/fastapi-python-boilerplate/tree/Origin",
      },
      {
        id: "pr-template",
        label: "PR Template",
        url: "https://github.com/ZyntroAI/fastapi-python-boilerplate/blob/Origin/.github/PULL_REQUEST_TEMPLATE.md",
      },
    ],
  },
};

/**
 * Links from the original brief that were dropped or rewritten, and why.
 * `replacement: null` means nothing usable existed — do not invent one.
 */
export const CORRECTED_LINKS = [
  {
    cited: "https://fastapi.tiangolo.com/advanced/architecture/",
    reason: "404 — that path does not exist",
    replacement: "https://fastapi.tiangolo.com/advanced/",
  },
  {
    cited: "https://docs.hellofig.ai/",
    reason: "Host does not resolve (DNS failure)",
    replacement: "https://hellofig.app/",
  },
  {
    cited: "https://share.hellofig.app/help",
    reason: "404 — /help is not a help centre; the host serves shared conversations",
    replacement: "https://share.hellofig.app/",
  },
  {
    cited: "https://hellofig.app/changelog",
    reason: "404 — no public changelog at this path",
    replacement: null,
  },
  {
    cited: "https://hellofig.ai/",
    reason: "Different domain from the official hellofig.app platform site",
    replacement: "https://hellofig.app/",
  },
  {
    cited:
      "https://github.com/ZyntroAI/fastapi-python-boilerplate/blob/Origin/.github/CHECKLIST_BILLING.md",
    reason: "404 — file does not exist on Origin or main",
    replacement: null,
  },
];

/** source name (as detected from an image URL) -> OFFICIAL_DOCS key */
export const SOURCE_KEYS = {
  FastAPI: "fastapi",
  Python: "python",
  FIG: "fig",
  Dola: "dola",
  ZyntroAI: "zyntroai",
};

/** Accept only http/https — blocks javascript: and data: hrefs. */
export function isSafeUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

export function getPrimaryUrl(key) {
  const entry = OFFICIAL_DOCS[key];
  return entry && entry.links.length > 0 ? entry.links[0].url : null;
}

export function getSourceDoc(source) {
  const key = SOURCE_KEYS[source];
  return key ? OFFICIAL_DOCS[key] : null;
}

/**
 * Map an asset URL to the provider it came from.
 * Falls back to string sniffing when the value is not a parseable URL.
 */
export function detectSource(src) {
  const raw = String(src == null ? "" : src);
  let host = "";
  let path = "";
  try {
    const parsed = new URL(raw);
    host = parsed.hostname.toLowerCase();
    path = parsed.pathname.toLowerCase();
  } catch {
    const lower = raw.toLowerCase();
    if (lower.includes("dola.ai")) return "Dola";
    if (lower.includes("hellofig")) return "FIG";
    if (lower.includes("fastapi")) return "FastAPI";
    if (lower.includes("python.org")) return "Python";
    if (lower.includes("zyntroai")) return "ZyntroAI";
    return "Generic";
  }

  if (host === "dola.ai" || host.endsWith(".dola.ai")) return "Dola";
  if (host === "hellofig.app" || host === "hellofig.ai" || host.endsWith(".hellofig.app")) {
    return "FIG";
  }
  if (host === "docs.python.org" || host.endsWith(".python.org")) return "Python";
  if (host === "fastapi.tiangolo.com") return "FastAPI";
  if (host === "github.com") {
    if (path.startsWith("/tiangolo/fastapi")) return "FastAPI";
    if (path.startsWith("/zyntroai/")) return "ZyntroAI";
  }
  return "Generic";
}

/**
 * Describe an image asset: its provider, the official doc it should link to,
 * and structural facts. Pure and synchronous — safe to call during render.
 */
export function analyze(src, meta) {
  const extra = meta || {};
  const raw = String(src == null ? "" : src);
  const source = detectSource(raw);
  const doc = getSourceDoc(source);

  let host = "";
  let pathname = "";
  let ext = "";
  try {
    const parsed = new URL(raw);
    host = parsed.hostname;
    pathname = parsed.pathname;
    const match = /\.([a-z0-9]+)$/i.exec(pathname);
    if (match) ext = match[1].toLowerCase();
  } catch {
    const match = /\.([a-z0-9]+)(?:[?#].*)?$/i.exec(raw);
    if (match) ext = match[1].toLowerCase();
    pathname = raw;
  }

  return {
    src: raw,
    source,
    docRef: doc ? getPrimaryUrl(SOURCE_KEYS[source]) : null,
    docName: doc ? doc.name : null,
    host,
    pathname,
    ext,
    isImage: IMAGE_EXTENSIONS.includes(ext),
    isExternal: /^https?:\/\//i.test(raw),
    safe: isSafeUrl(raw),
    alt: extra.alt || "",
  };
}

/** Image skill descriptor — the documented surface other modules import. */
export const IMAGE_SKILL = {
  name: "ZyntroAI Vision Engine",
  version: REGISTRY_VERSION,
  sources: Object.keys(OFFICIAL_DOCS),
  docs: OFFICIAL_DOCS,
  verifiedOn: VERIFIED_ON,
  analyze,
  detectSource,
  getSourceDoc,
  getPrimaryUrl,
  isSafeUrl,
};

/** Machine-readable mirror handed to official_docs.py and CI. */
export function toRegistry() {
  return {
    version: REGISTRY_VERSION,
    verifiedOn: VERIFIED_ON,
    docs: OFFICIAL_DOCS,
    sourceKeys: SOURCE_KEYS,
    corrections: CORRECTED_LINKS,
    imageExtensions: IMAGE_EXTENSIONS,
  };
}

export default OFFICIAL_DOCS;

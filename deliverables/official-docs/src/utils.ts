/**
 * Shared helpers for the official-docs registry — isomorphic siblings of the
 * JavaScript functions in src/official-docs.js.
 *
 * The brief asked for a TypeScript build and a Python build of the same
 * bridged utility with matching logic, each adapted to its environment's I/O
 * model. The Python twin (src/official_docs.py) is the backend half: it reads
 * the generated JSON instead of a module graph, and reads request metadata
 * from ASGI headers instead of DOM attributes.
 */

/** Detect the provider an asset URL came from. Mirrors detectSource(). */
export function detectSource(src: string | null | undefined): string {
  const raw = String(src ?? "");
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

/** Accept only http/https. Mirrors isSafeUrl(). */
export function isSafeUrl(url: string | null | undefined): boolean {
  try {
    const parsed = new URL(String(url));
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

/**
 * Derive the provider from a browser Image element, preferring a data
 * attribute the renderer set and falling back to the resolved src.
 * DOM-attribute adaptation of detectSource().
 */
export function sourceFromElement(el: {
  dataset?: DOMStringMap;
  src?: string;
  currentSrc?: string;
}): string {
  const declared = el.dataset?.source?.trim();
  if (declared) return declared;
  return detectSource(el.currentSrc || el.src);
}

/** Join a doc group's links into a single record keyed by link id. */
export function flattenLinks(
  entry: { links?: Array<{ id: string; label: string; url: string }> } | null | undefined
): Record<string, string> {
  const out: Record<string, string> = {};
  for (const link of entry?.links ?? []) {
    if (isSafeUrl(link.url)) out[link.id] = link.url;
  }
  return out;
}

export default { detectSource, isSafeUrl, sourceFromElement, flattenLinks };

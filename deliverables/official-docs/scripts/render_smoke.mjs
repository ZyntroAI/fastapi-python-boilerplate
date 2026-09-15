/**
 * Render smoke test for Company.jsx.
 *
 * Bundles the component with esbuild (CSS modules stubbed), server-renders it,
 * and asserts the documentation bar and gallery cards actually produced links.
 *
 * Run: node scripts/render_smoke.mjs
 */
import { build } from "esbuild";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { mkdirSync } from "node:fs";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");
// Keep the bundle inside the package so Node resolves react from node_modules.
const tmp = join(root, ".render-tmp");
mkdirSync(tmp, { recursive: true });
const outfile = join(tmp, "company-render-smoke.mjs");

await build({
  entryPoints: [join(root, "src", "Company.jsx")],
  outfile,
  bundle: true,
  format: "esm",
  platform: "node",
  jsx: "automatic",
  loader: { ".css": "empty" },
  external: ["react", "react-dom", "prop-types"],
  logLevel: "error",
});

const { default: Company, OFFICIAL_DOCS, UnifiedImageCard } = await import(
  `${outfile}?t=${Date.now()}`
);

const html = renderToStaticMarkup(React.createElement(Company));

const checks = [];
const check = (name, condition) => checks.push({ name, ok: Boolean(condition) });

const anchors = [...html.matchAll(/href="([^"]+)"/g)].map((m) => m[1]);
const unique = new Set(anchors);

check("renders the documentation heading", html.includes("Official Documentation"));
check("renders the gallery", html.includes("FastAPI Architecture"));

const groupNames = Object.values(OFFICIAL_DOCS).map((d) => d.name);
check(
  "every doc group appears",
  groupNames.every((name) => html.includes(name))
);
check(`emits ${groupNames.length} doc-bar anchors`, unique.size >= groupNames.length);
check("every href is http(s)", anchors.every((h) => h.startsWith("http")));
check("every external link sets rel=noopener", !/target="_blank"(?![^>]*rel="noopener)/.test(html));
check("images are lazy-loaded", html.includes('loading="lazy"'));
check("renders source badges", html.includes(">FastAPI<") || html.includes(">FIG<"));

// Per-card rendering: a card must carry its provider's official reference.
const card = renderToStaticMarkup(
  React.createElement(UnifiedImageCard, {
    image: { id: "t", src: "https://dola.ai/x.png", alt: "Dola test", source: "Dola" },
  })
);
check("image card links to its source docs", card.includes("https://dola.ai/"));
check("image card names the source doc", card.includes("Dola AI Vision"));

// A card with no known provider must render without a dead link.
const generic = renderToStaticMarkup(
  React.createElement(UnifiedImageCard, {
    image: { id: "g", src: "https://example.com/x.png", alt: "Generic", source: "Generic" },
  })
);
check("unknown provider renders no reference link", !generic.includes("Official Reference"));

let failed = 0;
for (const { name, ok } of checks) {
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}`);
  if (!ok) failed += 1;
}
console.log(`\n${checks.length - failed}/${checks.length} render checks passed`);
console.log(`anchors rendered: ${anchors.length} (${unique.size} unique)`);
process.exit(failed === 0 ? 1 * 0 : 1);

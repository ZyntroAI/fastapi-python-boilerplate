/**
 * Tests for the official-docs registry. Node's built-in test runner, no deps:
 *   node tests/official-docs.test.mjs
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import {
  OFFICIAL_DOCS,
  CORRECTED_LINKS,
  IMAGE_SKILL,
  analyze,
  detectSource,
  getPrimaryUrl,
  getSourceDoc,
  isSafeUrl,
  toRegistry,
} from "../src/official-docs.js";

test("every registered link is http(s) and well formed", () => {
  for (const [key, entry] of Object.entries(OFFICIAL_DOCS)) {
    assert.ok(entry.links.length > 0, `${key} has no links`);
    for (const link of entry.links) {
      assert.ok(isSafeUrl(link.url), `${key}/${link.id} is not a safe URL: ${link.url}`);
      assert.ok(link.label.length > 0, `${key}/${link.id} has no label`);
    }
  }
});

test("getPrimaryUrl returns the first link per group", () => {
  assert.equal(getPrimaryUrl("fastapi"), "https://fastapi.tiangolo.com/");
  assert.equal(getPrimaryUrl("python"), "https://docs.python.org/3/");
  assert.equal(getPrimaryUrl("fig"), "https://hellofig.app/");
  assert.equal(getPrimaryUrl("nope"), null);
});

test("detectSource maps provider hosts", () => {
  assert.equal(detectSource("https://fastapi.tiangolo.com/img/logo.png"), "FastAPI");
  assert.equal(detectSource("https://docs.python.org/3/_static/py.svg"), "Python");
  assert.equal(detectSource("https://hellofig.app/og-image.png"), "FIG");
  assert.equal(detectSource("https://share.hellofig.app/abc"), "FIG");
  assert.equal(detectSource("https://dola.ai/docs/x.png"), "Dola");
  assert.equal(
    detectSource("https://github.com/ZyntroAI/fastapi-python-boilerplate/blob/main/x.png"),
    "ZyntroAI"
  );
  assert.equal(detectSource("https://github.com/tiangolo/fastapi"), "FastAPI");
  assert.equal(detectSource("https://example.com/a.png"), "Generic");
});

test("detectSource sniffs unparseable values instead of throwing", () => {
  assert.equal(detectSource("assets/dola.ai-capture.png"), "Dola");
  assert.equal(detectSource(""), "Generic");
  assert.equal(detectSource(null), "Generic");
  assert.equal(detectSource(undefined), "Generic");
});

test("host matching does not fall for lookalike domains", () => {
  assert.equal(detectSource("https://notdola.ai/x.png"), "Generic");
  assert.equal(detectSource("https://dola.ai.evil.example/x.png"), "Generic");
  assert.equal(detectSource("https://hellofig.app.evil.example/x.png"), "Generic");
});

test("analyze reports extension and image-ness", () => {
  const png = analyze("https://hellofig.app/og-image.png", { alt: "FIG" });
  assert.equal(png.source, "FIG");
  assert.equal(png.ext, "png");
  assert.equal(png.isImage, true);
  assert.equal(png.docRef, "https://hellofig.app/");
  assert.equal(png.alt, "FIG");

  const page = analyze("https://fastapi.tiangolo.com/advanced/");
  assert.equal(page.isImage, false);
  assert.equal(page.docName, "FastAPI Official");
});

test("analyze works on relative and malformed sources", () => {
  const rel = analyze("./assets/logo.svg");
  assert.equal(rel.source, "Generic");
  assert.equal(rel.ext, "svg");
  assert.equal(rel.safe, false);
  assert.equal(rel.isExternal, false);

  const junk = analyze("not a url at all");
  assert.equal(junk.safe, false);
});

test("getSourceDoc resolves only known sources", () => {
  assert.equal(getSourceDoc("Dola").name, "Dola AI Vision");
  assert.equal(getSourceDoc("FIG").name, "FIG Platform");
  assert.equal(getSourceDoc("Nope"), null);
});

test("isSafeUrl rejects javascript: and data: URLs", () => {
  assert.equal(isSafeUrl("https://example.com"), true);
  assert.equal(isSafeUrl("http://example.com"), true);
  assert.equal(isSafeUrl("javascript:alert(1)"), false);
  assert.equal(isSafeUrl("data:text/html;base64,PHNjcmlwdD4="), false);
  assert.equal(isSafeUrl(""), false);
  assert.equal(isSafeUrl(null), false);
});

test("corrected links record a reason for every removal", () => {
  assert.ok(CORRECTED_LINKS.length > 0);
  for (const item of CORRECTED_LINKS) {
    assert.ok(item.cited.startsWith("http"), `bad cited url: ${item.cited}`);
    assert.ok(item.reason.length > 0, `no reason for ${item.cited}`);
    assert.ok(
      item.replacement === null || item.replacement.startsWith("http"),
      `bad replacement for ${item.cited}`
    );
  }
});

test("no dropped link is still reachable through the registry", () => {
  const live = new Set();
  for (const entry of Object.values(OFFICIAL_DOCS)) {
    for (const link of entry.links) live.add(link.url);
  }
  for (const item of CORRECTED_LINKS) {
    if (item.replacement === null) {
      assert.ok(!live.has(item.cited), `${item.cited} is dead but still registered`);
    }
  }
});

test("toRegistry serialises cleanly and keeps the corrections", () => {
  const payload = toRegistry();
  assert.equal(payload.version, IMAGE_SKILL.version);
  assert.deepEqual(Object.keys(payload.docs), Object.keys(OFFICIAL_DOCS));
  assert.equal(payload.corrections.length, CORRECTED_LINKS.length);
  assert.equal(typeof JSON.parse(JSON.stringify(payload)), "object");
});

test("IMAGE_SKILL exposes the documented surface", () => {
  assert.equal(typeof IMAGE_SKILL.analyze, "function");
  assert.equal(typeof IMAGE_SKILL.detectSource, "function");
  assert.equal(typeof IMAGE_SKILL.getSourceDoc, "function");
  assert.equal(IMAGE_SKILL.name, "ZyntroAI Vision Engine");
  assert.ok(IMAGE_SKILL.sources.includes("fig"));
});

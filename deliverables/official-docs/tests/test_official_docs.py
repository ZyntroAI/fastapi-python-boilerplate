"""Tests for the Python twin of the official-docs registry.

Run:  python -m pytest tests/ -q
Also passes under plain unittest:  python tests/test_official_docs.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from official_docs import (  # noqa: E402
    DocRegistry,
    analyze,
    detect_source,
    is_safe_url,
    load_registry,
    source_from_headers,
)


class SafeUrlTest(unittest.TestCase):
    def test_accepts_http_and_https(self):
        self.assertTrue(is_safe_url("https://example.com"))
        self.assertTrue(is_safe_url("http://example.com/a.png"))

    def test_rejects_dangerous_and_empty(self):
        for bad in (
            "javascript:alert(1)",
            "data:text/html;base64,PHNjcmlwdD4=",
            "file:///etc/passwd",
            "",
            None,
        ):
            self.assertFalse(is_safe_url(bad), bad)


class DetectSourceTest(unittest.TestCase):
    def test_provider_hosts(self):
        cases = {
            "https://fastapi.tiangolo.com/img/logo.png": "FastAPI",
            "https://docs.python.org/3/_static/py.svg": "Python",
            "https://hellofig.app/og-image.png": "FIG",
            "https://share.hellofig.app/abc": "FIG",
            "https://dola.ai/docs/x.png": "Dola",
            "https://github.com/tiangolo/fastapi": "FastAPI",
            "https://github.com/ZyntroAI/fastapi-python-boilerplate/blob/main/x.png": "ZyntroAI",
            "https://example.com/a.png": "Generic",
        }
        for url, expected in cases.items():
            self.assertEqual(detect_source(url), expected, url)

    def test_sniffs_unparseable_values(self):
        self.assertEqual(detect_source("assets/dola.ai-capture.png"), "Dola")
        self.assertEqual(detect_source(""), "Generic")
        self.assertEqual(detect_source(None), "Generic")

    def test_lookalike_domains_are_generic(self):
        self.assertEqual(detect_source("https://notdola.ai/x.png"), "Generic")
        self.assertEqual(detect_source("https://dola.ai.evil.example/x.png"), "Generic")
        self.assertEqual(detect_source("https://hellofig.app.evil.example/x.png"), "Generic")


class SourceFromHeadersTest(unittest.TestCase):
    def test_declared_header_wins(self):
        self.assertEqual(source_from_headers({"x-asset-source": "Dola"}), "Dola")

    def test_header_lookup_is_case_insensitive(self):
        self.assertEqual(source_from_headers({"X-Asset-Source": "FIG"}), "FIG")

    def test_falls_back_to_referer_then_origin(self):
        self.assertEqual(source_from_headers({"referer": "https://dola.ai/x"}), "Dola")
        self.assertEqual(source_from_headers({"origin": "https://hellofig.app"}), "FIG")

    def test_defaults_to_generic(self):
        self.assertEqual(source_from_headers({}), "Generic")


class AnalyzeTest(unittest.TestCase):
    def test_reports_extension_and_image_ness(self):
        meta = analyze("https://hellofig.app/og-image.png", alt="FIG")
        self.assertEqual(meta["source"], "FIG")
        self.assertEqual(meta["ext"], "png")
        self.assertTrue(meta["is_image"])
        self.assertTrue(meta["safe"])
        self.assertEqual(meta["alt"], "FIG")
        self.assertEqual(meta["doc_key"], "fig")

    def test_non_image_page(self):
        meta = analyze("https://fastapi.tiangolo.com/advanced/")
        self.assertFalse(meta["is_image"])
        self.assertEqual(meta["source"], "FastAPI")

    def test_relative_and_malformed_sources(self):
        rel = analyze("./assets/logo.svg")
        self.assertEqual(rel["source"], "Generic")
        self.assertEqual(rel["ext"], "svg")
        self.assertFalse(rel["safe"])
        self.assertFalse(rel["is_external"])

        junk = analyze("not a url at all")
        self.assertFalse(junk["safe"])

    def test_explicit_source_overrides_detection(self):
        meta = analyze("https://cdn.example.com/a.png", source="Dola")
        self.assertEqual(meta["source"], "Dola")
        self.assertEqual(meta["doc_key"], "dola")


class RegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry()

    def test_json_mirror_exists_and_loads(self):
        self.assertIsInstance(self.registry, DocRegistry)
        self.assertTrue(self.registry.version)
        self.assertTrue(self.registry.verified_on)

    def test_every_link_is_safe(self):
        links = list(self.registry.iter_links())
        self.assertGreater(len(links), 0)
        for group_key, _name, _label, url in links:
            self.assertTrue(is_safe_url(url), f"{group_key}: {url}")

    def test_primary_urls(self):
        self.assertEqual(self.registry.primary_url("fastapi"), "https://fastapi.tiangolo.com/")
        self.assertEqual(self.registry.primary_url("python"), "https://docs.python.org/3/")
        self.assertEqual(self.registry.primary_url("fig"), "https://hellofig.app/")
        self.assertIsNone(self.registry.primary_url("nope"))

    def test_doc_for_source(self):
        self.assertEqual(self.registry.doc_for_source("Dola")["name"], "Dola AI Vision")
        self.assertIsNone(self.registry.doc_for_source("Nope"))

    def test_analyze_attaches_doc_reference(self):
        meta = self.registry.analyze("https://dola.ai/og.png")
        self.assertEqual(meta["doc_ref"], "https://dola.ai/")
        self.assertEqual(meta["doc_name"], "Dola AI Vision")

    def test_corrections_are_recorded_with_reasons(self):
        self.assertGreater(len(self.registry.corrections), 0)
        for item in self.registry.corrections:
            self.assertTrue(item["cited"].startswith("http"))
            self.assertTrue(item["reason"])

    def test_dead_links_are_not_registered(self):
        live = {url for _g, _n, _l, url in self.registry.iter_links()}
        for item in self.registry.corrections:
            if item["replacement"] is None:
                self.assertNotIn(item["cited"], live)

    def test_missing_file_raises_actionable_error(self):
        with self.assertRaises(FileNotFoundError) as ctx:
            load_registry(ROOT / "src" / "does-not-exist.json")
        self.assertIn("export_registry.mjs", str(ctx.exception))


class ParityTest(unittest.TestCase):
    """The JS registry and the Python twin must agree — that is the whole point."""

    def test_python_registry_matches_generated_json(self):
        payload = json.loads((ROOT / "src" / "official-docs.json").read_text(encoding="utf-8"))
        registry = load_registry()
        self.assertEqual(payload["version"], registry.version)
        self.assertEqual(payload["verifiedOn"], registry.verified_on)
        self.assertEqual(set(payload["docs"]), set(registry.docs))
        self.assertEqual(len(payload["corrections"]), len(registry.corrections))

    def test_js_and_python_agree_on_detection(self):
        """The shared table lives in this test so a drift in either language fails."""
        shared = {
            "https://fastapi.tiangolo.com/x.png": "FastAPI",
            "https://docs.python.org/3/x.png": "Python",
            "https://hellofig.app/x.png": "FIG",
            "https://dola.ai/x.png": "Dola",
            "https://example.com/x.png": "Generic",
        }
        for url, expected in shared.items():
            self.assertEqual(detect_source(url), expected, url)


if __name__ == "__main__":
    unittest.main(verbosity=2)

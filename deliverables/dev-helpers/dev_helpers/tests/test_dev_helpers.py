"""Tests for dev-helpers — stdlib unittest, no third-party dependency."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dev_helpers import (  # noqa: E402
    build_approval_doc,
    build_pr_body,
    check_push,
    checklist,
    explain_push,
    format_report,
    is_pinned,
    normalize_path,
    parse_state,
    render_markdown,
    required_permissions,
    scan_pins,
)


WORKFLOWS_WRITE = {"contents": "write", "workflows": "write"}
CONTENTS_ONLY = {"contents": "write"}


class TestNormalizePath(unittest.TestCase):
    def test_leaves_github_dot_intact(self):
        # The whole point: lstrip("./") would eat the leading dot.
        self.assertEqual(
            normalize_path(".github/workflows/ci.yml"), ".github/workflows/ci.yml"
        )
        self.assertNotEqual(
            ".github/workflows/ci.yml".lstrip("./"), ".github/workflows/ci.yml"
        )

    def test_strips_dot_slash_prefix(self):
        self.assertEqual(normalize_path("./src/app.py"), "src/app.py")
        self.assertEqual(normalize_path("././src/app.py"), "src/app.py")

    def test_normalises_backslashes(self):
        self.assertEqual(normalize_path(r".github\workflows\ci.yml"), ".github/workflows/ci.yml")


class TestRequiredPermissions(unittest.TestCase):
    def test_plain_change_needs_contents_only(self):
        self.assertEqual(required_permissions(["src/app.py"]), [["contents", "write"]])

    def test_workflow_change_adds_workflows_scope(self):
        req = required_permissions(["src/app.py", ".github/workflows/ci.yml"])
        self.assertIn(["workflows", "write"], req)


class TestCheckPush(unittest.TestCase):
    def test_blocked_without_workflows_scope(self):
        report = check_push(CONTENTS_ONLY, [".github/workflows/ci.yml"])
        self.assertFalse(report["can_push"])
        self.assertEqual(report["missing"], [["workflows", "write"]])
        self.assertEqual(report["workflow_paths"], [".github/workflows/ci.yml"])
        self.assertTrue(report["blockers"])

    def test_allowed_with_both_scopes(self):
        report = check_push(WORKFLOWS_WRITE, [".github/workflows/ci.yml"])
        self.assertTrue(report["can_push"])
        self.assertEqual(report["missing"], [])

    def test_allowed_for_non_workflow_change(self):
        report = check_push(CONTENTS_ONLY, ["README.md"])
        self.assertTrue(report["can_push"])

    def test_one_workflow_file_blocks_the_whole_push(self):
        report = check_push(
            CONTENTS_ONLY, ["README.md", "src/a.py", ".github/workflows/x.yml"]
        )
        self.assertFalse(report["can_push"])
        self.assertIn("REJECTED", explain_push(report))

    def test_none_permission_counts_as_missing(self):
        report = check_push({"contents": "write", "workflows": None}, [".github/workflows/a.yml"])
        self.assertFalse(report["can_push"])


class TestExplainAndReport(unittest.TestCase):
    def test_explain_allowed(self):
        self.assertIn("Push allowed", explain_push(check_push(WORKFLOWS_WRITE, ["a.py"])))

    def test_format_report_mentions_verdict(self):
        text = format_report(check_push(CONTENTS_ONLY, [".github/workflows/a.yml"]))
        self.assertIn("Push permission check", text)
        self.assertIn("blocked", text)


class TestPinning(unittest.TestCase):
    def test_full_sha_is_pinned(self):
        self.assertTrue(is_pinned("a" * 40))
        self.assertTrue(is_pinned("A" * 40))

    def test_tag_is_not_pinned(self):
        self.assertFalse(is_pinned("v4"))
        self.assertFalse(is_pinned("main"))

    def test_sha_with_version_comment_is_pinned(self):
        self.assertTrue(
            is_pinned("11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2")
        )

    def test_scan_pins_splits_correctly(self):
        text = (
            "steps:\n"
            "  - uses: actions/checkout@v4\n"
            f"  - uses: actions/setup-python@{'b' * 40} # v5\n"
            "  - uses: ./.github/actions/local\n"
        )
        pins = scan_pins(text)
        self.assertEqual(pins["total"], 2)  # local action excluded
        self.assertEqual(len(pins["unpinned"]), 1)
        self.assertEqual(len(pins["pinned"]), 1)

    def test_negative_hyphenated_workflow_name_not_a_sha(self):
        self.assertFalse(is_pinned("zzzz"))


class TestParseState(unittest.TestCase):
    def test_valid_yaml_parses(self):
        state = parse_state("name: ci\non: push\njobs:\n  a:\n    steps: []\n")
        self.assertTrue(state["parses"])

    def test_broken_yaml_flagged(self):
        state = parse_state("name: ci\non: push\njobs: [unclosed\n")
        if state["engine"] == "structural":
            self.skipTest("pyyaml not installed; structural fallback is lenient")
        self.assertFalse(state["parses"])


class TestApprovalDoc(unittest.TestCase):
    def test_document_names_repo_and_permission(self):
        doc = build_approval_doc(
            repo="ZyntroAI/fastapi-python-boilerplate",
            branch="fig/topic",
            files=[".github/workflows/ci.yml"],
            permission="workflows",
            reason="CI gate cannot be pushed.",
        )
        self.assertEqual(doc["file_count"], 1)
        self.assertEqual(doc["repo"], "ZyntroAI/fastapi-python-boilerplate")

    def test_render_mentions_how_to_grant(self):
        md = render_markdown(
            build_approval_doc(
                repo="o/r",
                branch="b",
                files=[".github/workflows/ci.yml"],
                permission="workflows",
                reason="blocked",
            )
        )
        self.assertIn("Workflows", md)
        self.assertIn("Read and write", md)
        self.assertIn("`.github/workflows/ci.yml`", md)

    def test_render_lists_the_alternative(self):
        md = render_markdown(
            build_approval_doc("o/r", "b", ["x"], "contents", "nope")
        )
        self.assertIn("contents", md)


class TestPrHelper(unittest.TestCase):
    def test_checklist_marks_gaps(self):
        rows = checklist({"CHANGELOG.md updated": True})
        changelog = [r for r in rows if r["item"] == "CHANGELOG.md updated"][0]
        tests_row = [r for r in rows if r["item"].startswith("Tests added")][0]
        self.assertTrue(changelog["done"])
        self.assertFalse(tests_row["done"])

    def test_string_value_becomes_evidence(self):
        rows = checklist({"CHANGELOG.md updated": "PR #284"})
        self.assertEqual(rows and rows[2]["evidence"], "PR #284")

    def test_pr_body_has_sections(self):
        body = build_pr_body(
            summary="Add dev-helpers.",
            files=[".github/x", "a.py"],
            tests="`python -m unittest` — OK",
            dod_facts={"CHANGELOG.md updated": True},
        )
        self.assertIn("## Summary", body)
        self.assertIn("## Changes", body)
        self.assertIn("## Verification", body)
        self.assertIn("## Definition of Done", body)
        self.assertIn("[ ]", body)  # the gap is visible, not hidden


if __name__ == "__main__":
    unittest.main(verbosity=2)

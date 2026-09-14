"""Test suite for the FIG best-practices gate.

    python -m pytest tests -q

Two kinds of test here, and the distinction matters:

* unit tests on the engine (contrast math, glob matching, redaction) — these
  pin behaviour that is easy to get subtly wrong;
* fixture tests against ``examples/`` — these prove the gate actually
  distinguishes a good project from a bad one, which is the only claim that
  matters.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figbp import load_policy, run_gate  # noqa: E402
from figbp import integrations, secrets, tokens  # noqa: E402
from figbp.policy import matches_any  # noqa: E402
from quality_gate import main as gate_main  # noqa: E402

CLEAN = ROOT / "examples" / "clean-project"
BROKEN = ROOT / "examples" / "broken-project"


@pytest.fixture(scope="module")
def policy():
    p = load_policy()
    assert p.errors == [], f"policy is invalid: {p.errors}"
    return p


def by_id(report, cid):
    return next(r for r in report.results if r.id == cid)


# ---------------------------------------------------------------------------
# Policy
# ---------------------------------------------------------------------------
class TestPolicy:
    def test_loads_and_is_structurally_valid(self, policy):
        assert policy.errors == []
        assert policy.version
        assert policy.standard == "fig-best-practices"

    def test_declares_six_layers_in_order(self, policy):
        ids = [layer["id"] for layer in policy.layers]
        assert ids == [
            "01-structure",
            "02-design",
            "03-security",
            "04-performance",
            "05-team",
            "06-deployment",
        ]

    def test_declares_eight_criteria(self, policy):
        assert len(policy.criteria) == 8
        assert [c["id"] for c in policy.criteria] == [
            "STRUCTURE",
            "DESIGN",
            "SECURITY",
            "PERFORMANCE",
            "TESTING",
            "PERMISSIONS",
            "BACKUP",
            "DEPLOYMENT",
        ]

    def test_every_layer_owner_is_a_declared_role(self, policy):
        roles = set(policy.roles)
        for layer in policy.layers:
            assert layer["owner_role"] in roles, layer["id"]

    def test_every_role_scope_is_a_declared_layer(self, policy):
        layer_ids = {layer["id"] for layer in policy.layers}
        for role, entry in policy.roles.items():
            assert entry["scope"] in layer_ids, role

    def test_corrections_are_recorded_with_a_status(self, policy):
        assert len(policy.corrections) >= 4
        for item in policy.corrections:
            assert item.get("claim")
            assert item.get("status") in {"unverified", "corrected", "removed"}

    def test_invalid_policy_is_rejected(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("version: '1.0'\nstandard: x\n", encoding="utf-8")
        loaded = load_policy(bad)
        assert loaded.errors  # layers/roles/criteria absent

    def test_missing_policy_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_policy(tmp_path / "nope.yaml")


# ---------------------------------------------------------------------------
# Glob matching — the subtle one
# ---------------------------------------------------------------------------
class TestGlobMatching:
    def test_double_star_crosses_directories(self):
        assert matches_any("src/a/b/c.py", ["**/*.py"])
        assert matches_any("a.py", ["**/*.py"])

    def test_single_star_stays_in_one_segment(self):
        assert matches_any("src/a.py", ["src/*.py"])
        assert not matches_any("src/a/b.py", ["src/*.py"])

    def test_exact_path(self):
        assert matches_any("README.md", ["README.md"])
        assert not matches_any("docs/README.md", ["README.md"])

    def test_question_mark(self):
        assert matches_any("a1.py", ["a?.py"])
        assert not matches_any("a12.py", ["a?.py"])

    def test_regex_is_anchored(self):
        assert not matches_any("notreadme.md", ["readme.md"])


# ---------------------------------------------------------------------------
# Contrast mathematics
# ---------------------------------------------------------------------------
class TestContrast:
    def test_black_on_white_is_maximum(self):
        assert tokens.contrast_ratio("#000000", "#ffffff") == 21.0

    def test_same_colour_is_minimum(self):
        assert tokens.contrast_ratio("#777777", "#777777") == 1.0

    def test_known_pair_matches_wcag_value(self):
        # #767676 on white is the canonical 4.54:1 boundary case.
        assert tokens.contrast_ratio("#767676", "#ffffff") == pytest.approx(4.54, abs=0.01)

    def test_three_digit_hex_expands(self):
        assert tokens.parse_hex("#fff") == (255, 255, 255)
        assert tokens.parse_hex("#000") == (0, 0, 0)

    def test_eight_digit_hex_ignores_alpha(self):
        assert tokens.parse_hex("#ff000080") == (255, 0, 0)

    def test_invalid_hex_raises(self):
        for bad in ("hello", "#12345", "rgb(0,0,0)", ""):
            with pytest.raises(ValueError):
                tokens.parse_hex(bad)

    @pytest.mark.parametrize(
        "fg,bg,expected_floor_met",
        [
            ("#0f172a", "#ffffff", True),
            ("#64748b", "#ffffff", True),
            ("#cccccc", "#ffffff", False),
            ("#f8fafc", "#0f172a", True),
        ],
    )
    def test_floor_boundaries(self, fg, bg, expected_floor_met):
        ratio = tokens.contrast_ratio(fg, bg)
        assert (ratio >= 4.5) is expected_floor_met


# ---------------------------------------------------------------------------
# Secret scanning
# ---------------------------------------------------------------------------
class TestSecretScanning:
    def test_redaction_never_echoes_the_full_value(self):
        value = "abcdef1234567890abcdef1234567890"
        masked = secrets.redact(value, keep=4)
        assert masked.startswith("abcd")
        assert value not in masked
        assert "*" in masked

    def test_short_value_is_fully_masked(self):
        assert secrets.redact("abc", keep=4) == "***"

    def test_token_assignment_is_caught(self, policy):
        findings = secrets.scan_forbidden_patterns(policy, BROKEN)
        locations = [f.location for f in findings]
        assert any(loc.startswith("src/settings.py") for loc in locations), locations

    def test_private_key_block_is_caught(self, policy, tmp_path):
        (tmp_path / "key.pem").write_text(
            "-----BEGIN RSA PRIVATE KEY-----\nMIIabc\n-----END RSA PRIVATE KEY-----\n",
            encoding="utf-8",
        )
        findings = secrets.scan_forbidden_patterns(policy, tmp_path)
        assert any(f.pattern_id == "private_key_block" for f in findings)

    def test_github_token_is_caught(self, policy, tmp_path):
        (tmp_path / "cfg.py").write_text('t = "ghp_' + "a" * 40 + '"\n', encoding="utf-8")
        findings = secrets.scan_forbidden_patterns(policy, tmp_path)
        assert any(f.pattern_id == "github_token" for f in findings)

    def test_aws_key_is_caught(self, policy, tmp_path):
        key = "AKIA" + "IOSFODNN7" + "EXAMPLE"
        (tmp_path / "cfg.py").write_text(f'k = "{key}"\n', encoding="utf-8")
        findings = secrets.scan_forbidden_patterns(policy, tmp_path)
        assert any(f.pattern_id == "aws_access_key" for f in findings)

    def test_clean_tree_has_no_findings(self, policy):
        assert secrets.scan_forbidden_patterns(policy, CLEAN) == []

    def test_committed_env_is_flagged(self, policy):
        names = [Path(p).name for p in secrets.scan_committed_env(policy, BROKEN)]
        assert ".env" in names, names

    def test_env_example_is_allowlisted(self, policy, tmp_path):
        (tmp_path / ".env").write_text("A=1\n", encoding="utf-8")
        assert len(secrets.scan_committed_env(policy, tmp_path)) == 1
        (tmp_path / ".env").rename(tmp_path / ".env.example")
        assert secrets.scan_committed_env(policy, tmp_path) == []

    def test_comment_only_env_is_not_flagged(self, policy, tmp_path):
        (tmp_path / ".env").write_text("# nothing configured yet\n", encoding="utf-8")
        assert secrets.scan_committed_env(policy, tmp_path) == []


# ---------------------------------------------------------------------------
# Integration contracts
# ---------------------------------------------------------------------------
class TestIntegrations:
    def test_shipped_example_validates(self, policy):
        assert integrations.check_integrations(policy, ROOT) == []

    def test_missing_required_field_is_caught(self):
        schema = integrations.load_schema()
        issues = integrations.validate_against_schema({"id": "x"}, schema)
        assert any("missing required" in str(i) for i in issues)

    def test_literal_secret_ref_is_rejected(self):
        schema = integrations.load_schema()
        instance = {
            "id": "svc-a",
            "provider": "P",
            "transport": "rest",
            "auth": {"type": "bearer", "secretRef": "sk-literal-value"},
            "owner": "security",
        }
        issues = integrations.validate_against_schema(instance, schema)
        assert any("pattern" in str(i) or "does not match" in str(i) for i in issues)

    def test_env_secret_ref_is_accepted(self):
        schema = integrations.load_schema()
        instance = {
            "id": "svc-a",
            "provider": "P",
            "transport": "rest",
            "auth": {"type": "bearer", "secretRef": "env:MY_KEY"},
            "owner": "security",
        }
        assert integrations.validate_against_schema(instance, schema) == []

    def test_unexpected_property_is_rejected(self):
        schema = integrations.load_schema()
        instance = {
            "id": "svc-a",
            "provider": "P",
            "transport": "rest",
            "auth": {"type": "bearer", "secretRef": "env:K"},
            "owner": "security",
            "surprise": True,
        }
        issues = integrations.validate_against_schema(instance, schema)
        assert any("unexpected property" in str(i) for i in issues)

    def test_http_baseurl_is_rejected(self, policy, tmp_path):
        (tmp_path / "integrations").mkdir()
        (tmp_path / "integrations" / "bad.integration.yaml").write_text(
            "id: svc-a\nprovider: P\ntransport: rest\n"
            'baseUrl: "http://insecure.example"\n'
            "auth:\n  type: bearer\n  secretRef: env:K\nowner: security\n",
            encoding="utf-8",
        )
        messages = integrations.check_integrations(policy, tmp_path)
        assert any("plaintext HTTP" in m for m in messages), messages

    def test_bad_transport_enum_is_rejected(self, policy, tmp_path):
        (tmp_path / "integrations").mkdir()
        (tmp_path / "integrations" / "bad.integration.yaml").write_text(
            "id: svc-a\nprovider: P\ntransport: carrier-pigeon\n"
            "auth:\n  type: bearer\n  secretRef: env:K\nowner: security\n",
            encoding="utf-8",
        )
        messages = integrations.check_integrations(policy, tmp_path)
        assert any("not one of" in m for m in messages), messages


# ---------------------------------------------------------------------------
# The gate against the fixtures — the real claim
# ---------------------------------------------------------------------------
class TestCleanProject:
    @pytest.fixture(scope="class")
    def report(self, policy):
        return run_gate(policy, CLEAN)

    def test_passes_every_criterion(self, report):
        failed = [(r.id, r.evidence) for r in report.results if not r.passed]
        assert failed == [], failed
        assert report.passed is True

    def test_scores_eight_of_eight(self, report):
        assert report.score == "8/8"

    def test_every_criterion_has_a_layer(self, report):
        for result in report.results:
            assert result.layer.startswith("0")

    def test_json_shape_is_stable(self, report):
        payload = json.loads(json.dumps(report.to_dict()))
        assert payload["passed"] is True
        assert len(payload["results"]) == 8
        assert {"id", "layer", "severity", "status", "summary", "evidence"} <= set(
            payload["results"][0]
        )


class TestBrokenProject:
    @pytest.fixture(scope="class")
    def report(self, policy):
        return run_gate(policy, BROKEN)

    def test_is_blocked(self, report):
        assert report.passed is False

    def test_structure_fails(self, report):
        result = by_id(report, "STRUCTURE")
        assert not result.passed
        assert any("BEST-PRACTICES.md" in e for e in result.evidence)

    def test_design_fails_on_contrast(self, report):
        result = by_id(report, "DESIGN")
        assert not result.passed
        assert any("contrast" in e or "hard-coded" in e for e in result.evidence)

    def test_design_fails_on_hardcoded_colour(self, report):
        result = by_id(report, "DESIGN")
        assert any("Card.tsx" in e for e in result.evidence), result.evidence

    def test_security_fails(self, report):
        result = by_id(report, "SECURITY")
        assert not result.passed
        assert any("settings.py" in e for e in result.evidence), result.evidence

    def test_security_fails_on_committed_env(self, report):
        result = by_id(report, "SECURITY")
        assert any("env.committed" in e for e in result.evidence), result.evidence

    def test_security_evidence_never_leaks_the_secret(self, report):
        result = by_id(report, "SECURITY")
        joined = " ".join(result.evidence)
        assert "abcdef1234567890abcdef1234567890" not in joined

    def test_performance_fails_on_oversized_image(self, report):
        result = by_id(report, "PERFORMANCE")
        assert not result.passed
        assert any("hero.png" in e for e in result.evidence), result.evidence

    def test_permissions_fails_on_unscoped_agent(self, report):
        result = by_id(report, "PERMISSIONS")
        assert not result.passed
        assert any("ghost.md" in e for e in result.evidence), result.evidence

    def test_backup_fails(self, report):
        assert not by_id(report, "BACKUP").passed

    def test_deployment_fails_on_unpinned_action(self, report):
        result = by_id(report, "DEPLOYMENT")
        assert not result.passed
        assert any("not SHA-pinned" in e for e in result.evidence), result.evidence

    def test_testing_passes_because_tests_exist(self, report):
        assert by_id(report, "TESTING").passed

    def test_security_covers_integration_contracts(self, policy, tmp_path):
        """A secret inlined in an integration contract is still a leak."""
        (tmp_path / "integrations").mkdir()
        (tmp_path / "integrations" / "leaky.integration.yaml").write_text(
            "id: svc-a\nprovider: P\ntransport: rest\n"
            "auth:\n  type: bearer\n  secretRef: env:OK\nowner: security\n",
            encoding="utf-8",
        )
        (tmp_path / "integrations" / "inlined.integration.yaml").write_text(
            "id: svc-b\nprovider: P\ntransport: rest\n"
            "auth:\n  type: bearer\n  secretRef: literal-secret-value\nowner: security\n",
            encoding="utf-8",
        )
        report = run_gate(policy, tmp_path)
        result = by_id(report, "SECURITY")
        assert not result.passed
        assert any("inlined.integration.yaml" in e for e in result.evidence), result.evidence
        # The well-formed sibling must not be implicated.
        assert not any(e.startswith("integrations/leaky") for e in result.evidence)

    def test_at_least_seven_criteria_fail(self, report):
        failed = [r.id for r in report.results if not r.passed]
        assert len(failed) >= 7, failed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
class TestCli:
    def test_clean_project_exits_zero(self, capsys):
        code = gate_main(["--root", str(CLEAN)])
        assert code == 0
        assert "safe to deploy" in capsys.readouterr().out

    def test_broken_project_exits_one(self, capsys):
        code = gate_main(["--root", str(BROKEN)])
        assert code == 1
        assert "BLOCKED" in capsys.readouterr().out

    def test_json_output_parses(self, capsys):
        gate_main(["--root", str(BROKEN), "--json"])
        payload = json.loads(capsys.readouterr().out)
        assert payload["passed"] is False
        assert payload["score"].endswith("/8")

    def test_list_prints_eight_criteria(self, capsys):
        assert gate_main(["--list"]) == 0
        lines = [l for l in capsys.readouterr().out.splitlines() if l.strip()]
        assert len(lines) == 8

    def test_missing_root_is_an_error(self, capsys):
        assert gate_main(["--root", "/nonexistent/path/xyz"]) == 2

    def test_missing_policy_is_an_error(self, tmp_path, capsys):
        assert gate_main(["--policy", str(tmp_path / "no.yaml"), "--root", str(CLEAN)]) == 2

    def test_invalid_policy_is_an_error(self, tmp_path, capsys):
        bad = tmp_path / "bad.yaml"
        bad.write_text("version: '1'\nstandard: x\n", encoding="utf-8")
        assert gate_main(["--policy", str(bad), "--root", str(CLEAN)]) == 2


# ---------------------------------------------------------------------------
# Cross-checks
# ---------------------------------------------------------------------------
class TestConsistency:
    def test_best_practices_doc_names_every_criterion(self, policy):
        doc = (ROOT / "BEST-PRACTICES.md").read_text(encoding="utf-8")
        for criterion in policy.criteria:
            assert criterion["id"] in doc, criterion["id"]

    def test_agent_files_are_scoped_and_listed(self, policy):
        listed = (ROOT / "agents" / "README.md").read_text(encoding="utf-8")
        for role in policy.roles:
            path = ROOT / "agents" / f"{role}.md"
            assert path.exists(), role
            assert role in listed, role
            assert policy.role_scope(role) in path.read_text(encoding="utf-8")

    def test_design_tokens_file_parses(self):
        payload = json.loads((ROOT / "design" / "design-tokens.json").read_text(encoding="utf-8"))
        assert payload["$contrastPairs"]
        assert payload["color"]

    def test_jsonschema_agrees_when_installed(self):
        """Cross-check our validator against the real library, if present."""
        jsonschema = pytest.importorskip("jsonschema")
        schema = integrations.load_schema()
        instance = integrations.load_integration(
            ROOT / "integrations" / "example.integration.yaml"
        )
        jsonschema.validate(instance=instance, schema=schema)
        assert integrations.validate_against_schema(instance, schema) == []

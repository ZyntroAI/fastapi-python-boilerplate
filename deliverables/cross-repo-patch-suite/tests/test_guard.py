"""Overwrite guard and policy loading."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchsuite import Intent, all_allowed, guard, plan_writes
from patchsuite.loader import load_manifest, load_policy


def test_create_on_a_free_path_is_allowed(tmp_path: Path):
    result = guard(tmp_path / "new.md", Intent.CREATE)
    assert result.allowed is True
    assert result.exists is False


def test_create_over_an_existing_file_is_refused(tmp_path: Path):
    p = tmp_path / "exists.md"
    p.write_text("original\n")
    result = guard(p, Intent.CREATE)
    assert result.allowed is False
    assert "already exists" in result.reason
    assert p.read_text() == "original\n", "the guard must not touch the file"


def test_refusal_points_at_writing_beside_it(tmp_path: Path):
    p = tmp_path / "exists.md"
    p.write_text("x\n")
    assert "different name" in guard(p, Intent.CREATE).reason


def test_append_is_allowed_without_approval(tmp_path: Path):
    p = tmp_path / "f.md"
    p.write_text("a\n")
    result = guard(p, Intent.APPEND)
    assert result.allowed is True
    assert "additive" in result.reason


def test_replace_is_refused_without_approval(tmp_path: Path):
    p = tmp_path / "f.md"
    p.write_text("a\n")
    result = guard(p, Intent.REPLACE)
    assert result.allowed is False
    assert "exact path" in result.reason


def test_replace_is_refused_when_approval_names_a_different_path(tmp_path: Path):
    p = tmp_path / "f.md"
    p.write_text("a\n")
    assert guard(p, Intent.REPLACE, approval=str(tmp_path / "other.md")).allowed is False


def test_replace_is_allowed_when_approval_matches_exactly(tmp_path: Path):
    p = tmp_path / "f.md"
    p.write_text("a\n")
    assert guard(p, Intent.REPLACE, approval=str(p)).allowed is True


def test_guard_records_existing_hash(tmp_path: Path):
    p = tmp_path / "f.md"
    p.write_text("a\n")
    assert len(guard(p, Intent.APPEND).existing_sha256) == 64


def test_guard_accepts_a_plain_string_intent(tmp_path: Path):
    assert guard(tmp_path / "n.md", "create").allowed is True


def test_guard_rejects_an_unknown_intent(tmp_path: Path):
    with pytest.raises(ValueError):
        guard(tmp_path / "n.md", "obliterate")


def test_guard_result_as_dict_is_json_safe(tmp_path: Path):
    p = tmp_path / "f.md"
    p.write_text("a\n")
    assert json.loads(json.dumps(guard(p, Intent.APPEND).as_dict()))["allowed"] is True


def test_plan_writes_checks_a_whole_changeset_before_writing(tmp_path: Path):
    existing = tmp_path / "taken.md"
    existing.write_text("x\n")
    plan = plan_writes(
        {
            str(existing): Intent.CREATE,
            str(tmp_path / "free.md"): Intent.CREATE,
        }
    )
    by_path = {p.path: p for p in plan}
    assert by_path[str(existing)].decision == "refuse"
    assert by_path[str(tmp_path / "free.md")].decision == "allow"
    assert all_allowed(plan) is False


def test_plan_writes_passes_when_the_approval_is_given(tmp_path: Path):
    existing = tmp_path / "taken.md"
    existing.write_text("x\n")
    plan = plan_writes({str(existing): Intent.REPLACE}, approvals={str(existing)})
    assert all_allowed(plan) is True


def test_policy_loads_from_the_suite():
    policy = load_policy()
    assert policy.name == "cross-repo-patch-suite"
    assert policy.version == "1.0.0"
    assert policy.appends["byte_exact"] is True
    assert policy.guard["refuse_create_over_existing"] is True
    assert policy.workflow["require_sha_pin"] is True


def test_policy_flag_helper():
    policy = load_policy()
    assert policy.flag("workflow", "sha_length") == 40
    assert policy.flag("workflow", "does_not_exist", "fallback") == "fallback"


def test_policy_appends_defaults_match_the_code():
    """The policy documents the behaviour — keep them in step."""
    policy = load_policy()
    assert policy.appends["align_to_file"] is True
    assert policy.appends["close_unterminated_final_line"] is True


def test_manifest_lists_every_sub_skill():
    manifest = load_manifest()
    ids = {s["id"] for s in manifest["sub_skills"]}
    assert {"byte-append", "eol-fidelity", "patch-apply", "workflow-gate", "overwrite-guard"} <= ids


def test_manifest_sub_skill_modules_exist(suite_root: Path):
    manifest = load_manifest()
    missing = [s["module"] for s in manifest["sub_skills"] if not (suite_root / s["module"]).exists()]
    assert missing == [], f"manifest references missing modules: {missing}"


def test_manifest_entrypoints_are_importable():
    """Package entrypoints must be exported; script entrypoints are checked at file level."""
    import patchsuite

    manifest = load_manifest()
    missing = []
    for skill in manifest["sub_skills"]:
        module = skill["module"]
        if not module.startswith("src/"):
            continue  # a standalone script, exercised by its own CLI test
        for name in skill.get("entrypoints", []):
            if not hasattr(patchsuite, name):
                missing.append(f"{skill['id']}:{name}")
    assert missing == [], f"entrypoints not exported: {missing}"


def test_manifest_script_entrypoints_are_defined(suite_root: Path):
    """Script entrypoints must at least exist as callables in their file."""
    manifest = load_manifest()
    for skill in manifest["sub_skills"]:
        module = skill["module"]
        if module.startswith("src/"):
            continue
        source = (suite_root / module).read_text(encoding="utf-8")
        for name in skill.get("entrypoints", []):
            assert f"def {name}(" in source, f"{module} does not define {name}()"


def test_manifest_fixture_paths_exist(suite_root: Path):
    manifest = load_manifest()
    for key, rel in manifest["fixtures"].items():
        assert (suite_root / rel).exists(), f"{key} fixture missing: {rel}"

"""ตรวจว่าโครง task tracker ยังถูกต้อง — ไม่ใช่แค่มีโฟลเดอร์ แต่ข้อมูลต้องสอดคล้องกัน"""
import datetime as dt
import re

import tasks
import pytest

ROOT = tasks.ROOT
STATUSES = tasks.STATUSES
REQUIRED_KEYS = {
    "id", "title", "status", "priority", "created", "updated",
    "owner", "repo", "prs", "tokens",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def all_tasks():
    return list(tasks.iter_tasks())


def test_status_folders_exist():
    for status in STATUSES:
        assert (ROOT / status).is_dir(), f"ไม่มีโฟลเดอร์ {status}/"


def test_every_task_has_front_matter():
    tasks = all_tasks()
    assert tasks, "ไม่พบไฟล์งานเลย"
    for _status, path, fm in tasks:
        missing = REQUIRED_KEYS - set(fm)
        assert not missing, f"{path.name} ขาด key: {sorted(missing)}"


def test_status_matches_folder():
    """สถานะใน front-matter ต้องตรงกับโฟลเดอร์ — กันงานเสร็จแล้วค้างใน inprogress/"""
    for status, path, fm in all_tasks():
        assert fm["status"] == status, (
            f"{path.name}: status='{fm['status']}' แต่ไฟล์อยู่ {status}/"
        )


def test_status_is_valid_value():
    for _status, path, fm in all_tasks():
        assert fm["status"] in STATUSES, f"{path.name}: status ไม่ถูกต้อง"


def test_ids_unique():
    ids = [fm["id"] for _s, _p, fm in all_tasks()]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"id ซ้ำ: {sorted(dupes)}"


def test_dates_are_iso():
    for _status, path, fm in all_tasks():
        for key in ("created", "updated"):
            assert DATE_RE.match(fm[key]), f"{path.name}: {key}='{fm[key]}' ต้องเป็น YYYY-MM-DD"
            dt.date.fromisoformat(fm[key])


def test_done_tasks_have_evidence():
    """งานที่ปิดแล้วต้องอ้าง PR ได้ — ไม่งั้น 'done' ไม่มีหลักฐาน"""
    for status, path, fm in all_tasks():
        if status != "done":
            continue
        assert fm.get("prs", "[]") not in ("[]", ""), (
            f"{path.name}: อยู่ใน done/ แต่ไม่มี PR อ้างอิง"
        )


def test_token_field_is_numeric():
    for _status, path, fm in all_tasks():
        int(fm["tokens"]), f"{path.name}: tokens ต้องเป็นตัวเลข"


def test_estimate_tokens_uses_len_div_4():
    assert tasks.estimate_tokens("a" * 40) == 10
    assert tasks.estimate_tokens("") == 0


def test_read_front_matter_roundtrip(tmp_path):
    f = tmp_path / "t.md"
    f.write_text("---\nid: X\nstatus: new\n---\n\n# body\n", encoding="utf-8")
    assert tasks.read_front_matter(f) == {"id": "X", "status": "new"}


def test_write_front_matter_value(tmp_path):
    f = tmp_path / "t.md"
    f.write_text("---\nstatus: new\nupdated: 2026-01-01\n---\n\n# body\n", encoding="utf-8")
    tasks.write_front_matter_value(f, "status", "done")
    assert tasks.read_front_matter(f)["status"] == "done"


def test_report_runs(capsys):
    assert tasks.main(["report"]) == 0
    out = capsys.readouterr().out
    assert "สรุปภาพรวม" in out


def test_list_runs(capsys):
    assert tasks.main(["list"]) == 0
    assert "งาน" in capsys.readouterr().out


def test_move_updates_status_and_folder(tmp_path, monkeypatch):
    """ย้ายงานแล้วทั้งโฟลเดอร์และ front-matter ต้องเปลี่ยนตามกัน"""
    fixed = tmp_path
    for s in STATUSES:
        (fixed / s).mkdir()
    monkeypatch.setattr(tasks, "ROOT", fixed)
    (fixed / "new" / "TASK-X.md").write_text(
        "---\nid: TASK-X\ntitle: t\nstatus: new\ncreated: 2026-01-01\n"
        "updated: 2026-01-01\nprs: []\ntokens: 0\n---\n# x\n", encoding="utf-8")

    assert tasks.main(["move", "TASK-X", "done"]) == 0
    assert not (fixed / "new" / "TASK-X.md").exists()
    moved = fixed / "done" / "TASK-X.md"
    assert moved.exists()
    assert tasks.read_front_matter(moved)["status"] == "done"


def test_archive_is_a_status_but_not_in_the_working_flow():
    """archive/ อยู่ใน STATUSES แต่ไม่นับเป็น active — runbook ยัง new->inprogress->done"""
    assert "archive" in STATUSES
    assert "archive" not in tasks.ACTIVE_STATUSES
    assert set(tasks.ACTIVE_STATUSES) == {"new", "inprogress", "done"}


def test_move_to_archive_updates_status_and_folder(tmp_path, monkeypatch):
    """ย้ายงานเข้า archive/ แล้ว front-matter ต้องเป็น archived ตาม"""
    fixed = tmp_path
    for s in STATUSES:
        (fixed / s).mkdir()
    monkeypatch.setattr(tasks, "ROOT", fixed)
    (fixed / "new" / "TASK-Y.md").write_text(
        "---\nid: TASK-Y\ntitle: t\nstatus: new\ncreated: 2026-01-01\n"
        "updated: 2026-01-01\nprs: []\ntokens: 0\n---\n# y\n", encoding="utf-8")

    assert tasks.main(["move", "TASK-Y", "archive"]) == 0
    assert not (fixed / "new" / "TASK-Y.md").exists()
    archived = fixed / "archive" / "TASK-Y.md"
    assert archived.exists()
    assert tasks.read_front_matter(archived)["status"] == "archive"


def test_archive_command_writes_reason(tmp_path, monkeypatch, capsys):
    """คำสั่ง archive ต้องย้ายงานเข้า archive/ และจดเหตุผลลง Completion summary"""
    fixed = tmp_path
    for s in STATUSES:
        (fixed / s).mkdir()
    monkeypatch.setattr(tasks, "ROOT", fixed)
    (fixed / "new" / "TASK-Z.md").write_text(
        "---\nid: TASK-Z\ntitle: t\nstatus: new\ncreated: 2026-01-01\n"
        "updated: 2026-01-01\nprs: []\ntokens: 0\n---\n# z\n\n"
        "## Completion summary\n\n(old text)\n", encoding="utf-8")

    assert tasks.main(["archive", "TASK-Z", "ถูกแทนที่ด้วย", "#176"]) == 0
    archived = fixed / "archive" / "TASK-Z.md"
    assert archived.exists()
    assert not (fixed / "new" / "TASK-Z.md").exists()
    assert tasks.read_front_matter(archived)["status"] == "archive"

    body = archived.read_text(encoding="utf-8")
    assert "ถูกแทนที่ด้วย #176" in body
    assert "(old text)" not in body, "Completion summary เดิมต้องถูกแทนที่"
    assert body.count("## Completion summary") == 1
    assert "archive" in capsys.readouterr().out


def test_archive_command_requires_a_reason(tmp_path, monkeypatch):
    fixed = tmp_path
    for s in STATUSES:
        (fixed / s).mkdir()
    monkeypatch.setattr(tasks, "ROOT", fixed)
    (fixed / "new" / "TASK-W.md").write_text(
        "---\nid: TASK-W\ntitle: t\nstatus: new\ncreated: 2026-01-01\n"
        "updated: 2026-01-01\nprs: []\ntokens: 0\n---\n# w\n", encoding="utf-8")

    with pytest.raises(SystemExit):
        tasks.main(["archive", "TASK-W", "   "])
    # งานต้องยังอยู่ที่เดิม เพราะไม่มีเหตุผลให้บันทึก
    assert (fixed / "new" / "TASK-W.md").exists()


def test_archive_command_appends_heading_when_missing(tmp_path, monkeypatch):
    """งานเก่าที่ไม่มีหัวข้อ Completion summary ต้องไม่พัง — ต่อหัวข้อให้"""
    fixed = tmp_path
    for s in STATUSES:
        (fixed / s).mkdir()
    monkeypatch.setattr(tasks, "ROOT", fixed)
    (fixed / "new" / "TASK-V.md").write_text(
        "---\nid: TASK-V\ntitle: t\nstatus: new\ncreated: 2026-01-01\n"
        "updated: 2026-01-01\nprs: []\ntokens: 0\n---\n# v\n", encoding="utf-8")

    assert tasks.main(["archive", "TASK-V", "ซ้ำกับ TASK-U"]) == 0
    body = (fixed / "archive" / "TASK-V.md").read_text(encoding="utf-8")
    assert "## Completion summary" in body
    assert "ซ้ำกับ TASK-U" in body


def test_new_creates_file_in_new(tmp_path, monkeypatch):
    fixed = tmp_path
    for s in STATUSES:
        (fixed / s).mkdir()
    # cmd_new reads TASK_TEMPLATE.md from ROOT -- there is no templates/ subdir.
    (fixed / "TASK_TEMPLATE.md").write_text(
        "---\nid: TASK-YYYYMMDD-NNN\ntitle: short title\nstatus: new\n"
        "created: YYYY-MM-DD\nupdated: YYYY-MM-DD\n---\n# x\n", encoding="utf-8")
    monkeypatch.setattr(tasks, "ROOT", fixed)

    assert tasks.main(["new", "ทดสอบ สร้างงาน"]) == 0
    created = list((fixed / "new").glob("*.md"))
    assert len(created) == 1
    fm = tasks.read_front_matter(created[0])
    assert fm["title"] == "ทดสอบ สร้างงาน"

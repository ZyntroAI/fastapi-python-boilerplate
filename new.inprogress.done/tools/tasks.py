#!/usr/bin/env python3
"""tasks — Task tracker CLI.

คำสั่ง:
    list                     รายการงานทั้งหมด + สรุปจำนวนตามสถานะ
    report                   สรุปภาพรวม รวม token ที่ประมาณไว้
    new "ชื่องาน"             สร้างงานใหม่ใน new/ (ใช้ template)
    move <id> <status>       ย้ายงานไป new|inprogress|done|archive แล้วแก้ front-matter ให้ตรง
    archive <id> "<เหตุผล>"   ย้ายงานเข้า archive/ พร้อมบันทึกเหตุผลลง Completion summary

ไม่พึ่ง dependency ภายนอก — ใช้แค่ stdlib
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Active statuses are the working lifecycle. "archive" is a terminal holding
# area for tasks that were closed WITHOUT shipping (superseded, abandoned,
# duplicate) — it is deliberately outside the new -> inprogress -> done flow.
STATUSES = ("new", "inprogress", "done", "archive")
ACTIVE_STATUSES = ("new", "inprogress", "done")
COMPLETION_HEADING = "## Completion summary"
ID_RE = re.compile(r"^id:\s*(\S+)$", re.M)


def estimate_tokens(text: str) -> int:
    """ประมาณจำนวน token ด้วยกฎ len(text) // 4 ของโปรเจกต์นี้"""
    return len(text) // 4


def read_front_matter(path: Path) -> dict:
    """อ่าน front-matter แบบง่าย (key: value) ไม่ต้องใช้ PyYAML"""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def write_front_matter_value(path: Path, key: str, value: str) -> None:
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(rf"^{key}:\s*.*$", f"{key}: {value}", text, count=1, flags=re.M)
    if n == 0:
        raise SystemExit(f"ไม่พบ key '{key}' ใน {path.name}")
    path.write_text(new, encoding="utf-8")


def write_completion_summary(path: Path, text: str) -> None:
    """เขียนทับเนื้อหาใต้หัวข้อ '## Completion summary' ด้วยข้อความที่ให้

    ถ้าไม่มีหัวข้อนี้ (งานเก่าที่ยังไม่ใช้ template ปัจจุบัน) จะต่อท้ายไฟล์ให้เลย
    """
    content = path.read_text(encoding="utf-8")
    idx = content.find(COMPLETION_HEADING)
    if idx == -1:
        updated = content.rstrip() + f"\n\n{COMPLETION_HEADING}\n\n{text}\n"
    else:
        updated = content[: idx + len(COMPLETION_HEADING)] + f"\n\n{text}\n"
    path.write_text(updated, encoding="utf-8")


def iter_tasks():
    """ให้ (status, path, front_matter) ของทุกไฟล์งาน"""
    for status in STATUSES:
        for path in sorted((ROOT / status).glob("*.md")):
            yield status, path, read_front_matter(path)


def find_task(task_id: str):
    """คืน (status, path, front_matter) ของงานตาม id หรือ None ถ้าไม่พบ"""
    for status, path, fm in iter_tasks():
        if fm.get("id") == task_id:
            return status, path, fm
    return None


def _relocate(task_id: str, target_status: str):
    """ย้ายไฟล์งานไปโฟลเดอร์ปลายทางและปรับ front-matter ให้ตรง

    คืน (old_status, dest_path) หรือคืน None ถ้างานอยู่ในสถานะปลายทางอยู่แล้ว
    """
    if target_status not in STATUSES:
        raise SystemExit(f"status ต้องเป็นหนึ่งใน {STATUSES}")

    found = find_task(task_id)
    if found is None:
        raise SystemExit(f"ไม่พบงาน id = {task_id}")

    status, path, _fm = found
    if status == target_status:
        return None

    dest = ROOT / target_status / path.name
    shutil.move(str(path), str(dest))
    write_front_matter_value(dest, "status", target_status)
    write_front_matter_value(dest, "updated", dt.date.today().isoformat())
    return status, dest


def cmd_list(args) -> int:
    ok = True
    for status in STATUSES:
        rows = [(p, fm) for s, p, fm in iter_tasks() if s == status]
        print(f"\n[{status}] {len(rows)} งาน")
        if not rows:
            print("  (ว่าง)")
            continue
        for path, fm in rows:
            block = fm.get("blocked_by", "")
            mark = " [ติด: " + block + "]" if block else ""
            print(f"  {fm.get('id', '?'):<22} {fm.get('title', path.stem)}{mark}")
            if status != fm.get("status"):
                print(f"    ! status ใน front-matter = '{fm.get('status')}' ไม่ตรงกับโฟลเดอร์")
                ok = False
    return 0 if ok else 1


def cmd_report(args) -> int:
    tasks = list(iter_tasks())
    counts = {s: 0 for s in STATUSES}
    total = 0
    blocked = 0
    for status, path, fm in tasks:
        counts[status] += 1
        try:
            total += int(fm.get("tokens") or 0)
        except ValueError:
            pass
        if fm.get("blocked_by"):
            blocked += 1

    print("=" * 58)
    print("task tracker — สรุปภาพรวม")
    print("=" * 58)
    for status in STATUSES:
        print(f"  {status:<12} {counts[status]:>3}")
    print(f"  {'รวม':<12} {len(tasks):>3}")
    print(f"\n  ติด blocker    {blocked}")
    print(f"  token ประมาณ   {total:,}")
    print(f"\n  อัปเดตล่าสุด: {dt.date.today().isoformat()}")
    return 0


def cmd_new(args) -> int:
    today = dt.date.today().strftime("%Y%m%d")
    existing = {fm.get("id", "") for _, _, fm in iter_tasks()}
    n = 1
    while f"TASK-{today}-{n:03d}" in existing:
        n += 1
    task_id = f"TASK-{today}-{n:03d}"

    template = (ROOT / "TASK_TEMPLATE.md").read_text(encoding="utf-8")
    title = args.title
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50] or "task"
    # Substituting the title by placeholder was brittle: it silently did nothing
    # when the template's wording changed, leaving the file titled "short title".
    # Rewrite the front-matter lines directly instead.
    today = dt.date.today().isoformat()
    body = template.replace("TASK-YYYYMMDD-NNN", task_id)
    body = re.sub(r"^title:.*$", f"title: {title}", body, count=1, flags=re.M)
    body = re.sub(r"^created:.*$", f"created: {today}", body, count=1, flags=re.M)
    body = re.sub(r"^updated:.*$", f"updated: {today}", body, count=1, flags=re.M)
    # The template annotates status with a comment ("new  # new | inprogress …").
    # Copying that verbatim made the value fail the folder/status check, so keep
    # the bare value and drop the trailing comment.
    body = re.sub(r"^status:.*$", "status: new", body, count=1, flags=re.M)
    body = body.replace("YYYY-MM-DD", today)

    dest = ROOT / "new" / f"{task_id}-{slug}.md"
    dest.write_text(body, encoding="utf-8")
    print(f"สร้างแล้ว: {dest.relative_to(ROOT.parent)}")
    return 0


def cmd_move(args) -> int:
    result = _relocate(args.id, args.status)
    if result is None:
        print(f"{args.id} อยู่ใน {args.status} แล้ว")
        return 0
    old_status, _dest = result
    print(f"{args.id}: {old_status} -> {args.status}")
    return 0


def cmd_archive(args) -> int:
    """ย้ายงานเข้า archive/ และบันทึกเหตุผลลง Completion summary อัตโนมัติ

    ต่างจาก `move <id> archive` ตรงที่บังคับให้ระบุเหตุผล เพื่อไม่ให้งานที่ถูก
    ยกเลิกหายไปโดยไม่มีร่องรอยว่าทำไม
    """
    reason = " ".join(args.reason).strip()
    if not reason:
        raise SystemExit('ต้องระบุเหตุผลการ archive เช่น: archive TASK-... "ถูกแทนที่ด้วย #176"')

    result = _relocate(args.id, "archive")
    if result is None:
        print(f"{args.id} อยู่ใน archive แล้ว")
        return 0
    old_status, dest = result

    entry = f"Archived {dt.date.today().isoformat()} — {reason}"
    write_completion_summary(dest, entry)
    print(f"{args.id}: {old_status} -> archive")
    print(f"  เหตุผล: {reason}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="tasks", description="Task tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="รายการงานทั้งหมด").set_defaults(func=cmd_list)
    sub.add_parser("report", help="สรุปภาพรวม").set_defaults(func=cmd_report)

    p_new = sub.add_parser("new", help="สร้างงานใหม่")
    p_new.add_argument("title")
    p_new.set_defaults(func=cmd_new)

    p_move = sub.add_parser("move", help="ย้ายสถานะงาน")
    p_move.add_argument("id")
    p_move.add_argument("status")
    p_move.set_defaults(func=cmd_move)

    p_arch = sub.add_parser("archive", help="ย้ายงานเข้า archive/ พร้อมเหตุผล")
    p_arch.add_argument("id")
    p_arch.add_argument("reason", nargs="+", help="เหตุผลที่ยกเลิกงานนี้")
    p_arch.set_defaults(func=cmd_archive)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

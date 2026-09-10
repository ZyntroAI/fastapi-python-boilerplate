#!/usr/bin/env python3
"""tasks — Task tracker CLI.

คำสั่ง:
    list                     รายการงานทั้งหมด + สรุปจำนวนตามสถานะ
    report                   สรุปภาพรวม รวม token ที่ประมาณไว้
    new "ชื่องาน"             สร้างงานใหม่ใน new/ (ใช้ template)
    move <id> <status>       ย้ายงานไป new|inprogress|done แล้วแก้ front-matter ให้ตรง

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
STATUSES = ("new", "inprogress", "done")
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


def iter_tasks():
    """ให้ (status, path, front_matter) ของทุกไฟล์งาน"""
    for status in STATUSES:
        for path in sorted((ROOT / status).glob("*.md")):
            yield status, path, read_front_matter(path)


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
    body = body.replace("YYYY-MM-DD", today)

    dest = ROOT / "new" / f"{task_id}-{slug}.md"
    dest.write_text(body, encoding="utf-8")
    print(f"สร้างแล้ว: {dest.relative_to(ROOT.parent)}")
    return 0


def cmd_move(args) -> int:
    if args.status not in STATUSES:
        raise SystemExit(f"status ต้องเป็นหนึ่งใน {STATUSES}")

    target = None
    for status, path, fm in iter_tasks():
        if fm.get("id") == args.id:
            target = (status, path, fm)
            break
    if target is None:
        raise SystemExit(f"ไม่พบงาน id = {args.id}")

    status, path, fm = target
    if status == args.status:
        print(f"{args.id} อยู่ใน {args.status} แล้ว")
        return 0

    dest = ROOT / args.status / path.name
    shutil.move(str(path), str(dest))
    write_front_matter_value(dest, "status", args.status)
    write_front_matter_value(dest, "updated", dt.date.today().isoformat())
    print(f"{args.id}: {status} -> {args.status}")
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

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

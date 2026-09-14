"""Generate the fixture assets the gate needs to have something to measure.

Run from the deliverable root:  python scripts/make_fixtures.py

- examples/broken-project/assets/hero.png  — oversized, must fail PERFORMANCE
- examples/clean-project/assets/logo.svg   — tiny vector, must pass

Both are deterministic: same bytes every run, so the gate's verdict is stable.
Written without third-party image libraries.
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _chunk(tag: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)


def write_png(path: Path, width: int, height: int) -> int:
    """Write an RGB PNG with pseudo-random-but-deterministic noise.

    Noise defeats compression, which is exactly what an unoptimised photo
    looks like on disk — a flat colour would compress to almost nothing and
    the fixture would not exercise the budget.
    """
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0 (None)
        for x in range(width):
            raw.append((x * 137 + y * 31) % 256)
            raw.append((x * 89 + y * 173) % 256)
            raw.append((x * 211 + y * 57) % 256)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    data = (
        PNG_MAGIC
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return len(data)


def write_svg(path: Path) -> int:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">\n'
        '  <rect width="64" height="64" rx="12" fill="var(--color-brand-primary)"/>\n'
        '  <circle cx="32" cy="32" r="14" fill="var(--color-surface-base)"/>\n'
        "</svg>\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    return len(svg.encode("utf-8"))


def main() -> int:
    broken = ROOT / "examples" / "broken-project" / "assets" / "hero.png"
    clean = ROOT / "examples" / "clean-project" / "assets" / "logo.svg"

    png_bytes = write_png(broken, width=420, height=420)
    svg_bytes = write_svg(clean)

    kb = png_bytes / 1024
    print(f"{broken.relative_to(ROOT)}: {kb:.0f}KB (budget 250KB -> must FAIL)")
    print(f"{clean.relative_to(ROOT)}: {svg_bytes}B (svg -> must PASS)")

    if kb <= 250:
        print(
            f"ERROR: fixture is only {kb:.0f}KB, which would pass the budget. "
            "Increase the dimensions in this script.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

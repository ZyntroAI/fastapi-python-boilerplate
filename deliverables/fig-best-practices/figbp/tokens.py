"""Design token validation with real WCAG 2.1 contrast math.

Contrast is computed, not asserted: the ratio is derived from relative
luminance per WCAG 2.1 §1.4.3, so a token change is checked against the policy
floor rather than trusted.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .policy import Policy, read_text

HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
# Inline colour literals in source: hex, rgb(), rgba(), hsl(), hsla().
INLINE_COLOR_RE = re.compile(
    r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)",
)
# Property-name heuristics — used only to attribute a finding, never to decide it.
ANIMATION_MS_RE = re.compile(r"\d+(?:\.\d+)?ms\b")


@dataclass
class TokenIssue:
    code: str
    message: str
    location: str = ""

    def __str__(self) -> str:
        return f"{self.code}: {self.message}" + (f" ({self.location})" if self.location else "")


def parse_hex(value: str) -> tuple[int, int, int]:
    """Parse a hex colour to 8-bit RGB. Raises ValueError on anything else."""
    text = str(value).strip()
    if not HEX_RE.match(text):
        raise ValueError(f"not a hex colour: {value!r}")
    body = text[1:]
    if len(body) in (3, 4):
        body = "".join(ch * 2 for ch in body[:3])
    elif len(body) in (6, 8):
        body = body[:6]
    return int(body[0:2], 16), int(body[2:4], 16), int(body[4:6], 16)


def _channel_luminance(channel_8bit: int) -> float:
    c = channel_8bit / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG 2.1 relative luminance."""
    r, g, b = (_channel_luminance(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    """WCAG 2.1 contrast ratio, rounded to 2 dp. Range 1.0 – 21.0."""
    l1 = relative_luminance(parse_hex(fg))
    l2 = relative_luminance(parse_hex(bg))
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def flatten_colors(node: Any, prefix: str = "") -> dict[str, str]:
    """Flatten a nested colour tree to {'brand.primary': '#2563eb'}."""
    out: dict[str, str] = {}
    if isinstance(node, Mapping):
        for key, value in node.items():
            if str(key).startswith("$"):
                continue
            out.update(flatten_colors(value, f"{prefix}{key}."))
    elif isinstance(node, str) and HEX_RE.match(node.strip()):
        out[prefix.rstrip(".")] = node.strip()
    return out


def load_tokens(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve(colors: Mapping[str, str], dotted: str) -> str | None:
    return colors.get(dotted)


def check_tokens(policy: Policy, root: Path) -> list[TokenIssue]:
    """Validate the token file and every declared contrast pair."""
    issues: list[TokenIssue] = []
    rules = policy.rule("design")

    token_rel = rules.get("token_file", "design/design-tokens.json")
    token_path = Path(root) / token_rel

    if not token_path.exists():
        return [TokenIssue("design.no_token_file", f"token file missing: {token_rel}")]

    try:
        payload = load_tokens(token_path)
    except json.JSONDecodeError as exc:
        return [TokenIssue("design.invalid_json", f"{token_rel}: {exc}", token_rel)]

    colors = flatten_colors(payload.get("color", {}))
    if not colors:
        issues.append(TokenIssue("design.no_colors", "no colour tokens found", token_rel))

    for name, value in colors.items():
        if not HEX_RE.match(value):
            issues.append(TokenIssue("design.bad_hex", f"{name} = {value!r}", token_rel))

    floor = float(rules.get("contrast_floor", payload.get("contrastFloor", 4.5)))

    pairs: Iterable[Mapping[str, Any]] = payload.get("$contrastPairs", [])
    for pair in pairs:
        fg_name, bg_name = pair.get("text"), pair.get("background")
        required = float(pair.get("min", floor))
        fg, bg = resolve(colors, fg_name), resolve(colors, bg_name)
        if not fg or not bg:
            issues.append(
                TokenIssue("design.pair_missing", f"{fg_name} / {bg_name} not resolvable", token_rel)
            )
            continue
        try:
            ratio = contrast_ratio(fg, bg)
        except ValueError as exc:
            issues.append(TokenIssue("design.pair_bad_color", str(exc), token_rel))
            continue
        if ratio < required:
            issues.append(
                TokenIssue(
                    "design.contrast_below_floor",
                    f"{fg_name} on {bg_name} = {ratio}:1, below {required}:1",
                    token_rel,
                )
            )

    if not pairs:
        issues.append(TokenIssue("design.no_contrast_pairs", "no $contrastPairs declared", token_rel))

    return issues


def check_inline_colors(policy: Policy, root: Path) -> list[TokenIssue]:
    """Flag colour literals in source that should come from tokens."""
    rules = policy.rule("design")
    enforce_in = rules.get("enforce_tokens_in") or []
    if not enforce_in:
        return []

    allowed = {
        str(v).strip().lower().replace(" ", "") for v in (rules.get("allowed_literals") or [])
    }
    issues: list[TokenIssue] = []

    for rel, path in policy.scoped_files(root):
        from .policy import matches_any

        if not matches_any(rel, enforce_in):
            continue
        text = read_text(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            # A comment is documentation, not a rendered colour.
            if stripped.startswith(("//", "/*", "*", "#")):
                continue
            for match in INLINE_COLOR_RE.finditer(line):
                literal = match.group(0)
                if literal.lower().replace(" ", "") in allowed:
                    continue
                issues.append(
                    TokenIssue(
                        "design.hardcoded_color",
                        f"hard-coded colour {literal!r} — use a design token",
                        f"{rel}:{lineno}",
                    )
                )
    return issues

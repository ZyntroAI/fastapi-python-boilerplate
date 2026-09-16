# cross-repo-patch-suite

Patches that move between repositories fail for reasons that have nothing to do
with the change being made. A two-line append lands as a whole-file rewrite. A
workflow file that parses locally fails the scanner in CI. A patch that
`git apply --check` accepts is rejected by `git am` with "patch does not apply",
and you spend an afternoon looking for a conflict that does not exist.

This suite is the set of checks that stop those three. It is byte-oriented
throughout: it never decodes a file it is going to write back, because that
round-trip *is* the bug.

## The three failure modes, precisely

### 1. The text-mode round-trip

```python
text = path.read_text()          # CRLF becomes LF
path.write_text(text + "\nnew")  # every line is now "changed"
```

The append is two lines. The diff is the whole file. On a file with 400 lines,
that is 400 lines of review noise for a two-line change — and on a file with
mixed endings it silently normalises content nobody asked you to touch.

### 2. CRLF without a trailing newline

`git am` rejects it. `git apply --check` accepts it. The two commands disagree,
and the one that says "OK" is the one you will probably run first.

This is reproduced against real git in
[`tests/test_end_to_end.py`](tests/test_end_to_end.py) — the CRLF patch fails
`git am` with `patch does not apply`, and the byte-identical LF control applies
cleanly. The suite's
[`audit_eol_risk`](src/patchsuite/gitops.py) finds these files *before* you try,
so the diagnosis is not a mystery.

### 3. A workflow that will not parse

A colon inside an unquoted string — `- name: :x:` — is a YAML `ScannerError`.
The message names a line and column; the cause is that you meant a string and
the parser saw a mapping. Separately, an `uses:` reference on a tag (`@v4`)
parses perfectly and is still mutable, so the pin audit is a second, independent
check rather than part of YAML validity.

## Quick start

```sh
cd deliverables/cross-repo-patch-suite
python -m pytest -q                       # 125 tests
python scripts/make_fixtures.py           # regenerate fixtures byte-exactly
```

Append to a file without disturbing a byte of it:

```sh
python helpers/safe_append.py CONTRIBUTING.md --text "## Tests
Run pytest before opening a PR."          # dry run
python helpers/safe_append.py CONTRIBUTING.md --text-file snippet.md --apply
```

Audit and repair the file state that breaks `git am`:

```sh
python helpers/fix_eol.py .github/workflows --to crlf          # dry run
python helpers/fix_eol.py .github/workflows --to crlf --apply
```

Run the gate over a tree:

```sh
python scripts/patchctl.py eol   .github/workflows      # CRLF risk
python scripts/patchctl.py yaml  .github/workflows/ci.yml
python scripts/patchctl.py pins  .github/workflows      # unpinned actions
python scripts/patchctl.py check some.patch --in /path/to/repo
```

Every mutating command is a **dry run unless `--apply` is passed**. That is a
deliberate default: an append that rewrites line endings looks like a success
until you read the diff.

## What is in it

| Path | What it does |
|------|--------------|
| `src/patchsuite/eol.py` | Detect LF/CRLF/CR/mixed; resolve the append terminator; convert without touching content |
| `src/patchsuite/append.py` | Byte-exact append, plus `verify_append` and `diff_stat` to prove it |
| `src/patchsuite/gitops.py` | `git apply` / `git am` wrappers that name the cause instead of echoing "does not apply" |
| `src/patchsuite/yamlgate.py` | YAML validation with line/column, and the action SHA-pin audit |
| `src/patchsuite/guard.py` | Refuse creating over an existing file; require exact-path approval to replace |
| `src/patchsuite/loader.py` | Policy and manifest loading |
| `kernel/policy.yaml` | Every threshold and default, in one reviewable place |
| `scripts/patchctl.py` | CLI over all of the above |
| `scripts/make_handoff.py` | Patch + handoff doc for when the token cannot push to `.github/workflows/` |
| `helpers/safe_append.py` | The append you actually run |
| `helpers/fix_eol.py` | The EOL repair you actually run |
| `fixtures/clean-project` | A project that passes every check — guards against false positives |
| `fixtures/broken-project` | One file per failure mode, byte-exact |

## Use it as a library

```python
from patchsuite import append_text, verify_append, audit_pins, validate_yaml_file

before = path.read_bytes()
append_text(path, "## New section")
assert verify_append(before, path.read_bytes()).ok      # nothing else moved

if not validate_yaml_file(".github/workflows/ci.yml").valid:
    raise SystemExit("workflow does not parse")

assert audit_pins(".github/workflows").compliant        # every action SHA-pinned
```

## The overwrite guard

Repository policy here is that existing work is not silently replaced. The guard
makes that mechanical rather than a matter of remembering:

```python
from patchsuite import guard, Intent

guard("docs/NOTES.md", Intent.CREATE)            # refused — it exists
guard("docs/NOTES.md", Intent.REPLACE)           # refused — no approval
guard("docs/NOTES.md", Intent.REPLACE,
      approval="docs/NOTES.md")                  # allowed — named exactly
guard("docs/NOTES.md", Intent.APPEND)            # allowed — additive by nature
```

Approval must name the exact path. A blanket "yes" is not accepted, because the
point is to force the specific file into view before it is overwritten.

## Policy

All behaviour is driven by [`kernel/policy.yaml`](kernel/policy.yaml) — the
align-to-file default, the guard rules, the SHA length, and the offline handoff
path. Change the policy, not the code.

## Requirements

Python 3.10+, `PyYAML`, `git` on `PATH`, and `pytest` to run the suite. `httpx`
is optional and only used by `resolve_sha` to turn a tag into a commit SHA over
the network; without it, unresolved pins are reported rather than guessed.

## Scope

This suite is about **moving changes between repositories faithfully**. It is
not a linter, a formatter, or a CI runner, and it does not fix the files it
audits unless you pass `--apply`. Two things it deliberately does not do:
rewrite a file to normalise endings it did not have to change, and resolve a
SHA by guessing — an unresolved pin is reported as unresolved.

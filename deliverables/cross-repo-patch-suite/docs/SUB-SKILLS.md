# Sub-skills

Six focused capabilities. Each is usable on its own; the manifest in
[`manifest.json`](../manifest.json) is the machine-readable index.

---

## byte-append

**Module:** `src/patchsuite/append.py` · **CLI:** `patchctl append`, `patchctl verify`

Appends text to a file without decoding it, matching the target's line endings
so the diff shows only the new lines. The only change it may make to
pre-existing bytes is inserting a single terminator when the file did not end
with one.

```python
from patchsuite import append_text, verify_append

before = path.read_bytes()
append_text(path, "## New section")
assert verify_append(before, path.read_bytes()).ok
```

`verify_append` is the point of the sub-skill: it proves the pre-existing region
survived, and `diff_stat` turns that into the number a reviewer looks at
(`removed: 0`).

**Gotcha.** `plan_append` is pure and does no I/O — use it when you want the
resulting bytes without touching the disk.

---

## eol-fidelity

**Module:** `src/patchsuite/eol.py` · **CLI:** `patchctl eol`

Detects LF, CRLF, CR, and mixed endings, and resolves which terminator an append
should use. Mixed files resolve to the majority; ties break toward LF because
the repository's `.gitattributes` normalises to LF, and a tie broken the other
way would fight the checkout.

The combination to watch for is **CRLF with no trailing newline**:
`git am` rejects it while `git apply --check` accepts it. `audit_eol_risk` names
that symptom explicitly in its report rather than leaving you to infer it.

---

## patch-apply

**Module:** `src/patchsuite/gitops.py` · **CLI:** `patchctl check`

Wraps `git apply` and `git am` and turns the single unhelpful "does not apply"
into a named cause and a concrete fix. The categories it distinguishes are
whitespace drift, EOL/malformed patches, index mismatch, missing paths, and
paths that already exist.

```python
from patchsuite import check_patch, apply_mailbox

diag = check_patch(patch, repo)
if diag.applies:
    apply_mailbox(patch, repo)
else:
    print(diag.likely_cause, diag.suggested_fix)
```

`apply_mailbox` runs `git am --abort` first, so a previous failed attempt cannot
wedge the next one.

---

## workflow-gate

**Module:** `src/patchsuite/yamlgate.py` · **CLI:** `patchctl yaml`, `patchctl pins`

Two independent checks that are often confused for one:

1. **Does it parse?** `validate_yaml_file` reports the line and column, and for
   an unquoted colon it says so directly: `:x:` must be `":x:"`.
2. **Is it safe?** `audit_pins` requires every `uses:` reference to be a
   40-character commit SHA. A tag parses perfectly and is still mutable. Local
   (`./`) and container (`docker://`) references are skipped — there is no SHA
   to pin.

`resolve_sha` turns a tag into a SHA over the network and returns `None` rather
than guessing when it cannot.

---

## overwrite-guard

**Module:** `src/patchsuite/guard.py` · **CLI:** `patchctl guard`

Three intents with three different levels of ceremony:

| Intent | Behaviour |
|--------|-----------|
| `CREATE` | Allowed only if the path is free. Refused if anything is there. |
| `APPEND` | Always allowed — additive by construction. |
| `REPLACE` | Allowed only with an approval naming that exact path. |

A blanket approval is refused on purpose: the whole value is forcing the
specific file into view. `plan_writes` checks an entire changeset before any of
it is written.

---

## handoff

**Script:** `scripts/make_handoff.py`

When a token cannot push to `.github/workflows/` — GitHub requires the
`workflows` scope for that path — the change must still reach a human intact.
This produces a patch plus a `HANDOFF.md` naming the exact commands to land it,
including a `git apply --check` step that must print nothing.

The failure it prevents is a denied push with no artefact, which leaves the work
to be redone from memory.

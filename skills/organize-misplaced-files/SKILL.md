# 🧭 Skill: Organize Misplaced Files

**ย้ายไฟล์ที่อยู่ผิดที่อย่างปลอดภัย — พิสูจน์ก่อนขยับ ไม่ใช่กวาดรวม**

A repository root that has collected scratch exports, workflow copies, fonts and
one-off scripts is normal. Moving them is easy; moving them **without breaking
the app** is the whole job. This skill is the procedure, with the safety gate
that makes it safe.

---

## When this applies

- The root holds dozens (or hundreds) of files that are clearly not part of the tree.
- Someone says "จัดระเบียบไฟล์", "clean up the root", "files are in the wrong place".
- A move is being considered *before* a repo is handed over or audited.

Not for: moving files you just created, or a project with a tidy root already.

---

## The one rule

**A file moves only when nothing still depends on it.** "Depends on" means four
different things, and grep only finds one of them:

| Dependency | How to check | Why grep is not enough |
| ---------- | ------------ | ---------------------- |
| Imported as a module | Parse with `ast`, match the **exact** module name | `import auth` inside `app/api/auth.py` is not `import auth` at root |
| Referenced by name in docs/config | Text search for the basename | `FILE-MANIFEST.md` naming `deployment.yaml` |
| Referenced by a workflow or manifest | Text search over `.github/`, `k8s/`, `helm/` | `k8s/kustomization.yaml` naming a root YAML |
| Is a canonical repo file | Allow-list | `README.md`, `package.json`, `requirements.txt` |

Miss any one of these and you move a file that something needs.

---

## Procedure

### 1. Enumerate the real boundary

```bash
git ls-files | awk -F/ 'NF==1' | sort        # tracked root files only
```

Tracked, not `ls` — untracked scratch is a different problem. Quoted names
(spaces, leading `-`, emoji) will appear with escapes; handle paths as a list,
never interpolate them into a shell string.

### 2. Build the import index with AST

```python
import ast, subprocess
from pathlib import Path

files = [f for f in subprocess.run(["git","ls-files","-z"], capture_output=True,
         text=True).stdout.split("\0") if f]

index = {}                     # module name -> [files that import it]
for f in (x for x in files if x.endswith(".py")):
    try:
        tree = ast.parse(Path(f).read_text(encoding="utf-8", errors="ignore"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        continue               # unparseable is not "no importers" — flag it
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module.split(".")[0]]
        for n in names:
            index.setdefault(n, []).append(f)
```

Two traps here. `from app.services.auth import x` must **not** count as a use of
root `auth.py` — split on `.` and take the top level. And a file that fails to
parse must be reported, not silently treated as having no importers.

### 3. Hold anything still referenced

Collect the basename hits across every tracked `.md`, `.yml`, `.yaml`, `.json`,
`.toml`, `Makefile`, `Dockerfile*`, `.sh`. A single hit parks the file. This is
where a clean-looking plan loses 20 files — and the ones it loses are exactly the
ones that would have broken something.

### 4. Plan to `archive/`, never to `/dev/null`

Destination layout by kind keeps the archive legible:

```
archive/<reason>-<YYYY-MM>/
  scripts/    one-off .py nothing imported
  manifests/  workflow / k8s YAML copies
  exports/    csv, txt, patch, log snippets
  html/       saved pages
  assets/     fonts, images, zips
  notes/      markdown notes and chat exports
  misc/
```

`git mv` (not `mv`) keeps history and makes the change a rename in the PR diff.
For a path starting with `-`, terminate options: `git mv -- "- name.txt" dest/`.

### 5. Dry-run is the default, `--apply` is opt-in

Write the mover with `--apply` off by default and print the plan as JSON:
`{counts, move[], hold[], keep[]}`. Read `hold` before running the apply. If the
plan moves an `.py` a workflow calls, the gate in step 6 is what saves you.

### 6. Prove the app still boots — before and after

A move that changes an import outcome must be caught here. Capture signatures on
both sides and **diff them**:

```python
targets = ["main", "app.main", "app.core.main"]     # whatever the repo serves
for t in targets:
    try:
        mod = __import__(t, fromlist=["app"])
        print(t, "OK", len(mod.app.routes))
    except Exception as e:
        print(t, "FAIL", type(e).__name__, e)
```

Run it on pristine code, then after the move. **The signature must be identical.**
If a target failed before, it must fail after, with the same error. A target that
newly succeeds is a bonus; one that newly fails is a stop.

This is also how you separate your damage from pre-existing breakage — a repo
with a broken entrypoint already will show it in the *before* run, and now the
PR can say so honestly.

### 7. Write the archive a README

Say what moved, why, the three-condition rule, how to restore a file
(`git mv archive/… <original-path>`), and — the useful part — **what is still at
the root and needs a decision**, with the reason it could not be moved.

---

## Gotchas earned in practice

- **Config files lie about being unused.** `ci.yml` at the root is referenced by
  `CHANGELOG.md` and `FILE-MANIFEST.md`; a root `deployment.yaml` by
  `k8s/kustomization.yaml`. Text search is not optional.
- **`.env` is often tracked** despite `.gitignore` listing it. Moving it is not
  the fix — flag it (rotate, `git rm --cached`) rather than burying it.
- **A root `.py` may be an entrypoint for a platform, not for the code.** Check
  `Dockerfile`, `vercel.json`, `Makefile`, `*.service` before touching anything
  that looks like `main.py` / `app.py` / `index.py`.
- **Duplicate content is not duplicate function.** `main.py` and `app/main.py`
  can be byte-identical yet both referenced by different tooling.
- **Filenames with spaces, emoji or a leading dash will break a naive loop.**
  Drive moves from Python with an argument list, never a shell string.
- **Re-verify after writing.** Some environments reset files mid-task; confirm
  each edit landed (read the file back) before running the gate.

## Output

A PR that contains: the moves (`git mv`), `archive/<reason>-<date>/README.md`,
and the before/after gate signature in the description. Nothing deleted.

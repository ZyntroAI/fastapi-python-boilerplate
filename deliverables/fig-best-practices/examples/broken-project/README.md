# Broken example project

Deliberately non-compliant. It exists so the gate's *failures* are tested, not
just its passes. Every defect below is intentional and each one must be caught
by the named criterion.

| Defect | Criterion that catches it |
|--------|---------------------------|
| `BEST-PRACTICES.md` missing | STRUCTURE |
| Hard-coded `#ff00aa` and a below-floor contrast pair | DESIGN |
| Committed `.env` and a credential-shaped assignment | SECURITY |
| A 300KB+ PNG | PERFORMANCE |
| `agents/ghost.md` with no `scope:` | PERMISSIONS |
| No backup record | BACKUP |
| No approval record; action pinned to a floating tag | DEPLOYMENT |
| — | TESTING passes: the tests below are real |

Do not copy anything from this directory into a project.

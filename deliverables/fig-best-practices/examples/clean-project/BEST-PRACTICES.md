# Best practices

This project follows the FIG best-practices standard, version 1.0.0.

- Layout: `src/` for source, `tests/` for tests, `design/` for tokens.
- Design: all colour comes from `design/design-tokens.json`.
- Security: no credentials in the tree; secrets are referenced via `env:NAME`.
- Performance: images stay under the size budget.
- Team: every role in `agents/` declares a scope.
- Deployment: `BACKUP.md` and `DEPLOYMENT.md` record the release evidence.

# Clean example project

A minimal project that satisfies all eight criteria. It exists so the gate has
a known-good subject: if `quality_gate.py --root examples/clean-project` ever
fails, the gate is wrong, not the project.

```
clean-project/
├─ README.md
├─ BEST-PRACTICES.md
├─ BACKUP.md
├─ DEPLOYMENT.md
├─ design/design-tokens.json
├─ agents/developer.md
├─ src/App.tsx
└─ tests/test_app.py
```

Everything here is deliberately small — the point is the shape, not the content.

# Backup and rollback

## Backup

- Data store: none — this example is stateless.
- Configuration: version-controlled in this repository.
- Last verified restore: 2026-09-14 (dry run, no data to restore).

## Rollback path

1. Identify the last known-good commit: `git log --oneline -n 5`.
2. Revert the release commit: `git revert <sha> --no-edit`.
3. Push the revert branch and open a PR.
4. If a migration ran, restore from the snapshot taken before deploy.
5. Verify with `python quality_gate.py --root .` — all eight criteria must pass.

The rollback path is written before the release, not during the incident.

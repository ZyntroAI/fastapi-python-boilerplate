# Deployment

## Approval

- Change: initial example fixture.
- Approved by: repository owner (role `deployment`).
- Date: 2026-09-14.
- Rollback owner: role `deployment`.

## Release checklist

- [x] `python quality_gate.py --root .` passes all eight criteria
- [x] `python -m pytest tests -q` is green
- [x] Rollback path recorded in `BACKUP.md`
- [x] Actions pinned to full commit SHAs

## Notes

This fixture is not deployed anywhere. It exists as the gate's known-good
subject.

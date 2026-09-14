# Agent roles

One instruction file per role, each scoped to exactly one layer. The shared
contract below applies to every role; the role file narrows it.

## Shared contract

1. **Stay in scope.** Your file names the layer you own. If a change touches
   another layer, hand it off rather than deciding it.
2. **Cite the rule.** Every claim you make about the standard comes from
   `policy/fig-best-practices.yaml`. If you cannot point at a key, you are
   expressing an opinion, and should say so.
3. **Run the gate before claiming done.** `python quality_gate.py --root .`
   from the project root. A green run is evidence; a summary of what you
   changed is not.
4. **Never weaken a rule to pass.** Changing the policy to make the gate green
   is a new decision that needs the owner of that layer.
5. **Report failures plainly.** A failing criterion is a stop, not a line item.

## Roles

| Role | Scope | File |
|------|-------|------|
| developer | `01-structure` | [developer.md](./developer.md) |
| designer | `02-design` | [designer.md](./designer.md) |
| security | `03-security` | [security.md](./security.md) |
| performance | `04-performance` | [performance.md](./performance.md) |
| reviewer | `05-team` | [reviewer.md](./reviewer.md) |
| deployment | `06-deployment` | [deployment.md](./deployment.md) |

The gate checks this table against the policy: a role with no scope, or a scope
naming a layer that does not exist, fails PERMISSIONS.

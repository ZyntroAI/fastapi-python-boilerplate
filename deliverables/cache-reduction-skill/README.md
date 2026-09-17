# Cache Reduction

A cache-footprint audit toolkit for ZyntroAI services. Three independent
surfaces, one reporting shape, no live-cache access required — you point it at
source, at response headers, or at pasted `INFO` output.

Built for the stack we actually run: FastAPI + async, Redis for cache / queue /
rate-limit state, Vite + React frontends, Python and Node CI.

## Install

```bash
pip install -e .
pytest -q                       # 41 tests, pure stdlib
```

Or use it in place with no install:

```bash
PYTHONPATH=. python -m cache_reduction scan .
```

## The three surfaces

### 1. Static source scan — `scan`

Walks Python / TypeScript / JS / Markdown / YAML and reports the cache mistakes
that cost real memory in production.

```bash
python -m cache_reduction scan app/            # audit the app tree
python -m cache_reduction scan . --json        # machine-readable
```

Findings carry a stable code so they can be tracked over time:

| Code  | Severity | What it catches |
|-------|----------|-----------------|
| CR101 | high     | Cache write with no TTL — the key never expires on its own |
| CR102 | medium   | Sentinel TTL (`0`, `-1`, `99999999`, `1000000000`) that never expires |
| CR103 | medium   | Unbounded memoization — `@cache` with no `maxsize=` or TTL |
| CR104 | medium   | `keys("prefix:*")` wildcard scan over the whole keyspace |
| CR105 | high     | `flushdb()` / `flushall()` — clears keys other services own |
| CR201 | medium   | Agent-context file over the 30,000-character budget |
| CR202 | medium   | Identical block repeated inside one context file |
| CR203 | low      | External URLs inlined into a context file |

The report grades itself **A–F** from a weighted score (high 5, medium 2,
low 1). Exit code is `1` when any high finding is present, so it drops straight
into CI:

```yaml
- name: Cache footprint gate
  run: PYTHONPATH=. python -m cache_reduction scan app/
```

### 2. HTTP / CDN headers — `headers`

Answers the two questions that decide whether a response is wasting browser and
edge cache: *may it be stored, and for how long* — and, after a deploy, *would
returning clients still be served the old bytes*.

```bash
python -m cache_reduction headers --before "Cache-Control: public, max-age=31536000"
python -m cache_reduction headers \
  --before "Cache-Control: public, max-age=300" \
  --after  "Cache-Control: public, max-age=60"
```

| Code | Severity | What it catches |
|------|----------|-----------------|
| H101 | high     | No `Cache-Control` at all — heuristic freshness applies |
| H102 | medium   | Bare `public` with no shared lifetime |
| H103 | high     | `private` combined with `s-maxage` — contradictory |
| H104 | low      | Shared-only lifetime; browsers cannot hold it cheaply |
| H105 | high     | **Stale after change** — content changed, URL and headers did not, no ETag |
| H106 | medium   | `no-store` alongside a freshness lifetime |
| H107 | low      | Very long `max-age` without `immutable` |

`H105` is the one that bites in practice: a deploy changes the asset but not the
URL, and every returning client keeps the old bytes until the lifetime runs out.
Pass `--after` with the new build's headers to detect it before the deploy, then
call `recompute_after_change()` to re-check once it has landed.

### 3. Redis memory and hit rate — `redis`

Takes pasted `INFO` output — never a live connection — and reports where the
memory is going, whether the cache is working at all, and how much is
reclaimable.

```bash
redis-cli INFO > info.txt
python -m cache_reduction redis --file info.txt
redis-cli INFO | python -m cache_reduction redis
```

| Code | Severity | What it catches |
|------|----------|-----------------|
| R101 | high     | Fragmentation ≥ 2.0 — RSS is roughly 2x the dataset |
| R102 | high     | No `maxmemory` — the cache can grow until the host dies |
| R103 | high     | `noeviction` policy with a limit set — writes fail when full |
| R104 | high     | Keys being evicted — the working set does not fit |
| R105 | high     | Hit rate below 70% — memory spent without saving work |
| R106 | medium   | Fewer than 10% of keys carry a TTL — the reclaimable pool |

The report estimates reclaimable bytes as `used_memory × (1 − ttl_coverage)`,
which is the size of the no-TTL pool a TTL pass would put on a clock.

It also states the **outage stance** explicitly: `fail-open` means a Redis
outage degrades to cache misses rather than taking the service down. Pass
`--fail-closed` if your service actually treats Redis as a hard dependency, and
the report will say so rather than quietly assuming the safe answer.

## Library use

```python
from cache_reduction import scan_path, analyze_cache_headers, audit_redis_info

report = scan_path("app/")
print(report.summary())                  # "Scanned 12 file(s) — 3 finding(s) (grade C, score 9): ..."

headers = analyze_cache_headers(before_raw, after_raw)
if headers["stale_after_change"]:
    raise SystemExit("deploy would not reach clients — needs a content hash or an ETag")

redis = audit_redis_info(open("info.txt").read())
print(redis["reclaimable_human"], redis["key_safety"])
```

Every object has `.to_dict()`, so the reports serialise straight to JSON or into
a ZyntroAI `deliverables/` record.

## Design notes

- **Offline by construction.** Nothing here opens a socket. You supply the
  source text, the header block, or the `INFO` dump; the audit is pure and
  reproducible.
- **Stable codes.** `CR`/`H`/`R` codes are meant to be referenced in tickets and
  tracked across runs — they are treated as an interface, not log lines.
- **Ranked, not dumped.** Severity weights feed a single score and grade, so a
  report leads with what matters instead of a wall of equal-looking warnings.
- **The production stance is stated, not assumed.** Cache-read failure behaviour
  (`fail-open` vs `fail-closed`) is reported in plain words because getting it
  wrong is the difference between a slow page and an outage.

## Applying it to a ZyntroAI service

1. `python -m cache_reduction scan app/` — fix every CR1xx high first; those are
   the keys that live forever.
2. Audit the Redis `INFO` dump — R102 (`maxmemory` unset) and R106 (almost no
   TTLs) usually travel together and account for most of the footprint.
3. Run a TTL pass on the no-TTL pool, sized from `reclaimable_human`.
4. Re-run the header check against the deployed assets — H105 catches the
   deploys that look successful but never reach returning clients.
5. Add the scan as a CI gate so no-TTL writes cannot come back.

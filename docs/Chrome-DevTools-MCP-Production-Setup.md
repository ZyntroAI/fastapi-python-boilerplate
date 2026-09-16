# Chrome DevTools MCP — Production Setup

> Security-hardened setup for the [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
> server: a pinned MCP config, a containerised browser, and a CI gate that catches
> misconfiguration.
> Reference: **MCP-DOC-2026-0916** · Verified against `chrome-devtools-mcp@1.0.1`
> through `@1.9.0`, 16 September 2026.
> Companion files: [`docs/mcp/`](./mcp/) · Verifier: [`scripts/verify-mcp-flags.py`](../../scripts/verify-mcp-flags.py)

---

## The trap this guide is written around

`chrome-devtools-mcp` parses its CLI arguments with a **non-strict** parser. An
unknown flag is not an error — it is silently discarded, and the process starts
normally and exits 0.

We confirmed this directly:

```console
$ npx chrome-devtools-mcp@1.0.1 --totally-bogus-flag-xyz
# ...starts normally, exit 0
```

That has a nasty consequence for exactly this kind of hardening work. A config
that misspells or invents a flag **looks completely healthy**. `--help` works,
the server boots, MCP clients connect, CI stays green — and the security control
the flag was supposed to enable was never applied. There is no runtime signal.

So the rule for this repo is: **never trust that the server started.** Every flag
must be checked against the server's own `--help` for the version you pinned. That
check is [`scripts/verify-mcp-flags.py`](../../scripts/verify-mcp-flags.py), and it runs in CI.

---

## 1. Hardened MCP configuration

[`docs/mcp/mcp-config.json`](./mcp/mcp-config.json):

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@1.4.0",
        "--headless",
        "--isolated",
        "--redact-network-headers",
        "--no-usage-statistics",
        "--no-performance-crux",
        "--channel=stable",
        "--user-data-dir=/tmp/chrome-mcp-profile",
        "--log-file=/var/log/chrome-devtools-mcp.log",
        "--blocked-url-pattern=https://*/auth/*",
        "--blocked-url-pattern=https://*/api/*/private"
      ],
      "env": {
        "CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS": "1",
        "NODE_ENV": "production"
      }
    }
  }
}
```

### Version choice

`@1.4.0` is pinned deliberately rather than taking `@latest`. It is the version
this config was verified against, and it is new enough to carry every control in
the list below.

Two later features are worth knowing about but are **not** in this config:

- `--allowedUrlPattern` (allow-list rather than deny-list) requires **Chrome 149+**.
  On an older browser it is accepted and does nothing useful — an allow-list that
  fails open is worse than no allow-list, so do not add it until the browser is
  pinned at 149 or above.
- The `--categoryExtensions` control is only effective on a pipe connection;
  `autoConnect`, `browserUrl` and `wsEndpoint` connections ignore it.

### A note on the tool categories

`--categoryExtensions` and `--categoryExperimentalThirdParty` already default to
`false` in this version, so there is nothing to switch off — adding
`--no-category-extensions` would be a no-op that *looks* like a hardening step.
(It is also not a recognised flag spelling in 1.4.0; the verifier in §4 caught it
in an earlier draft of this config, which is the whole reason that script exists.)
If you later bump to a version where they default on, re-run the verifier before
adding them back.

### Flag notes

| Flag | What it does |
| --- | --- |
| `--headless` | No UI. Required in a container. |
| `--isolated` | Temporary user-data-dir, cleaned up on exit. Prefer this over a long-lived profile for agent work. |
| `--redact-network-headers` | Redacts sensitive request/response headers before they reach the model. |
| `--no-usage-statistics` | Opts out of usage telemetry. (`--no-performance-crux` additionally stops trace URLs being sent to the CrUX API.) |
| `--blocked-url-pattern` | Browser-level deny-list. Blocks navigations **and** subresource requests. |
| `--channel=stable` | Use the system's stable Chrome. |

> **The deny-list is not a network sandbox.** Upstream's own
> [`SECURITY.md`](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/SECURITY.md)
> is explicit: `--blocked-url-pattern` "is not a complete network sandbox and it
> only applies to Chrome DevTools targets while `chrome-devtools-mcp` is attached
> to them. To have a full network sandbox, we recommend using a separate OS/VM
> sandbox mechanism." Treat it as one layer, not the layer.

---

## 2. Containerised server

Two files: [`docs/mcp/Dockerfile`](./mcp/Dockerfile) and
[`docs/mcp/docker-compose.yml`](./mcp/docker-compose.yml). The properties that
matter:

- **Runs as non-root.** The image ends with `USER node`; the compose file also
  sets `cap_drop: ALL` and `security_opt: no-new-privileges:true`.
- **Read-only root filesystem.** `read_only: true`, with `/tmp` and `/var/log`
  as the only writable paths, both `tmpfs` and both mounted `noexec,nosuid`.
- **No published ports.** The server speaks JSON-RPC over stdio — it is not a
  network service. There is no `ports:` and no `expose:`, because there should
  not be a DevTools port to reach.
- **`shm_size: 1gb`.** Chromium needs more than Docker's default 64 MB of
  `/dev/shm`; without it you get crashes that look like random page failures.
- **`internal: true` network.** Containers on this network have no route off the
  host, so even a browser started with a debugging port cannot be reached from
  outside.

### Chromium on Alpine

The image is based on `node:20.19-alpine` and installs Chromium from Alpine's
**community** repository — which a bare `node:20.19-alpine` already enables, so
no extra repository configuration is needed. `nss`, `freetype`, `harfbuzz` and
`ttf-freefont` are installed alongside it because headless Chromium will not
launch correctly without them.

`CHROME_PATH` is pointed at the packaged binary so the server does not download a
second copy of Chrome at run time.

```bash
docker compose -f docs/mcp/docker-compose.yml config   # validate
docker compose -f docs/mcp/docker-compose.yml build    # build
```

---

## 3. CI

[`docs/mcp/mcp-ci.yml`](./mcp/mcp-ci.yml) — SHA-pinned, and it gates on the flag
check described above.

> It lives under `docs/mcp/` rather than `.github/workflows/` because the Fig
> GitHub App lacks the App-installation `workflows` permission needed to push
> into that directory. A maintainer can move it into place unchanged:
>
> ```bash
> git mv docs/mcp/mcp-ci.yml .github/workflows/mcp-ci.yml
> ```

The steps:

1. **JSON validity** — `jq -e '.mcpServers'`, so a malformed config fails loudly
   instead of at connect time.
2. **Flag verification** — runs `verify-mcp-flags.py` against the *pinned* spec.
   This is the step that earns its keep.
3. **Version installable** — confirms the pinned version resolves and starts.
4. **Compose validity** — `docker compose config`.

All `uses:` refs are pinned to real 40-character commit SHAs:

| Action | SHA | Tag |
| --- | --- | --- |
| `actions/checkout` | `11d5960a326750d5838078e36cf38b85af677262` | `v4` |
| `actions/setup-node` | `49933ea5288caeca8642d1e84afbd3f7d6820020` | `v4` |
| `browser-actions/setup-chrome` | `c785b87e244131f27c9f19c1a33e2ead956ab7ce` | `v1` |

Note `checkout` and `setup-node` publish an annotated **tag object**; the SHA
above is the dereferenced commit (via `refs/tags/<tag>^{}`), which is what
`uses:` needs. Pinning the tag object's own SHA resolves to no commit and the
workflow is rejected before any job runs.

---

## 4. Verifying your own changes

```bash
python3 scripts/verify-mcp-flags.py docs/mcp/mcp-config.json
```

Expected output ends with:

```
checked 10 flag(s); 0 unsupported
```

Point it at a different release to check a config you are about to bump:

```bash
python3 scripts/verify-mcp-flags.py docs/mcp/mcp-config.json \
  --server chrome-devtools-mcp@1.9.0
```

The script understands yargs' boolean negation — `--no-foo` is accepted wherever
`--foo` is declared, even though the negated spelling never appears in `--help`
itself — so it will not flag a legitimate `--no-*` control. It exits `1` and names
every unsupported flag on stderr, so it works as a pre-commit hook as well as a CI
gate.

Cross-checking against a newer release is worth doing before a bump; this config
verified clean against both `@1.4.0` and `@1.9.0`.

### Flags from the original draft that are *not* real server options

These were in the first draft of this document and are **not** supported by the
server. Because the parser is non-strict they fail silently — which is precisely
why they were worth listing rather than quietly deleting:

| Draft flag | Status | Correct form |
| --- | --- | --- |
| `--disable-gpu` | Not a server flag | `--chrome-arg='--disable-gpu'` |
| `--no-sandbox` | Not a server flag | `--chrome-arg='--no-sandbox'` (avoids Chrome's own sandbox — think hard before using it) |
| `--blocked-url-pattern <v>` (space form) | Works, but yargs `array` type is unreliable in space form | `--blocked-url-pattern=<v>` (equals form) |

Everything else in the draft — `--headless`, `--redact-network-headers`,
`--user-data-dir`, `--channel`, `--log-file` — is valid, and both kebab-case and
camelCase spellings are honoured. `--channel`, `--log-file`, `--logFile` and
`--redact-network-headers` all appear in `--help`; `--disable-gpu` and
`--no-sandbox` do not, and only work passed through as Chrome arguments.

---

## 5. Security summary

What each layer actually buys you:

1. **No reachable DevTools port** — the server is stdio-only, not a network
   service. There is no `9222` to expose, so nothing depends on a firewall.
2. **Network isolation** — the compose network is `internal: true`, so a
   container on it has no route off the host.
3. **Read-only container** — `read_only: true` plus `noexec,nosuid` tmpfs mounts
   for the only two writable paths.
4. **No privilege escalation** — non-root user, `cap_drop: ALL`,
   `no-new-privileges:true`.
5. **Header redaction** — `--redact-network-headers` strips sensitive headers
   before they are returned to the model.
6. **URL blocking** — `--blocked-url-pattern` blocks both navigation and
   subresource requests to auth and private endpoints, enforced at the browser.
7. **Deterministic supply chain** — the server version is pinned in the config,
   the image and CI alike; the image is digest-pinnable; and every CI action is
   pinned to a real commit SHA.

### What this does not cover

Being explicit about the edges, because the gaps are where production surprises
live:

- **The deny-list is not a network sandbox** (see §1). Add an OS or VM-level
  egress control if you need one.
- **The browser is a powerful capability by design.** Upstream's `SECURITY.md`
  notes the server can write files (downloads, screenshots) and load extensions;
  this is documented behaviour, not a vulnerability. Its stated expectation is
  that the *client* validates tool calls and parameters before sending them.
- **Page content reaches the model as-is.** If you browse untrusted pages, prompt
  injection is a live risk — prefer trusted content, or use
  `--experimentalStructuredContent` when output structure matters.
- **`.env` is still tracked in git.** No scanner in this workflow will fail on
  it; that needs its own commit.

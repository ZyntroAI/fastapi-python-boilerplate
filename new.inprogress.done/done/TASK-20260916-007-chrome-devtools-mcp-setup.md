---
id: TASK-20260916-007
title: Chrome DevTools MCP production setup guide, with verified flags
status: done
priority: medium
created: 2026-09-16
updated: 2026-09-26
owner: fig-ai-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: [316]
blocked_by:
tokens: 0
---

# TASK-20260916-007 — Chrome DevTools MCP production setup guide

## Goal

Publish a production-ready, security-hardened setup for the `chrome-devtools-mcp`
server: pinned MCP config, containerised browser, and a CI gate. The draft that
prompted this named several flags that looked plausible but were never checked
against the real server, so the guide had to be verified before it shipped.

## What was verified

Every claim was checked against the installed package, not from memory:

- `chrome-devtools-mcp@1.0.1` **is** a real published version (1.0.1 → 1.9.0 exist;
  latest is 1.9.0). Node engine requirement is `^20.19.0 || ^22.12.0 || >=23`.
- The CLI parser is **non-strict**: `--totally-bogus-flag-xyz` is silently ignored
  and the process exits 0. This is the central finding — "the server started" is
  worthless as a validity check for a config.
- `--blocked-url-pattern` / `--allowed-url-pattern` are **real**, but they arrived
  *after* 1.0.1 (absent from that build's source; present in 1.4.0 and 1.9.0).
- `--redact-network-headers` is real and implemented in 1.0.1.
- `--disable-gpu` and `--no-sandbox` are **not** server flags; they only work via
  `--chrome-arg=`.
- Both kebab-case and camelCase spellings are honoured (tested with `--log-file`
  and `--logFile`, both wrote their log file).
- `--categoryExtensions` / `--categoryExperimentalThirdParty` already default to
  `false` in 1.4.0 — the draft's `--no-*` forms were redundant *and* unrecognised.
- Alpine: the `node:20.19-alpine` base enables the **community** repo, so no extra
  repo configuration is needed for Chromium.
- Real SHAs resolved for `actions/checkout@v4`, `actions/setup-node@v4` and
  `browser-actions/setup-chrome@v1`; the first two are annotated tags, so the
  dereferenced commit SHA is used.

## Deliverables

- `docs/Chrome-DevTools-MCP-Production-Setup.md`
- `docs/mcp/mcp-config.json`, `Dockerfile`, `docker-compose.yml`, `mcp-ci.yml`
- `scripts/verify-mcp-flags.py` — asserts every configured flag appears in the
  pinned server's `--help`, since the server will not do so itself.

## Out of scope / follow-ups

- `docs/mcp/mcp-ci.yml` is not installed into `.github/workflows/` — the Fig App
  lacks the App-installation `workflows` permission. A maintainer can `git mv` it
  into place unchanged.
- `--allowedUrlPattern` (allow-list) needs Chrome 149+; deliberately not used.
- `.env` remains tracked in git; unrelated to this task.

---
name: fetching
version: 1.0.0
description: Low-level async HTTP/GraphQL fetch — SSRF-safe, retry, cache, provenance
provides: [fetch.url, fetch.json, fetch.cached, fetch.gql, fetch.ws_connect, fetch.ws_send, fetch.ws_receive, fetch.ws_close, fetch.github.repo, fetch.github.pr]
security: { https_only: true, block: [localhost, private, cloud-metadata, file, data], redirects_max: 5 }
depends: [httpx]
---

# Fetching Skill

SSRF-protected async fetch with retry, TTL cache, and provenance on every result.

## Usage
```python
from skills.fetching import fetch

await fetch.json("https://api.example.com/data")          # -> parsed JSON
data = await fetch.cached("https://docs.example.com", ttl=120)
await fetch.gql("https://api.example.com/graphql", "query { user { id } }")  # GraphQL
await fetch.ws_connect("wss://stream.example.com/socket")                    # WebSocket
repo = await fetch.github.repo("ZyntroAI/fastapi-python-boilerplate")
```

## Pipeline
Request -> SSRF/policy check -> HTTP(S) fetch (timeout, redirect cap) -> provenance -> (cache)

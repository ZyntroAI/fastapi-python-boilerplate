---
name: fetching
version: 1.0.0
description: Low-level async HTTP/GraphQL fetch — SSRF-safe, retry, cache, provenance
provides: [fetch.url, fetch.json, fetch.cached, fetch.github.repo, fetch.github.pr]
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
repo = await fetch.github.repo("ZyntroAI/fastapi-python-boilerplate")
```

## Pipeline
Request -> SSRF/policy check -> HTTP(S) fetch (timeout, redirect cap) -> provenance -> (cache)

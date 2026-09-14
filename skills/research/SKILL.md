---
name: research
version: 1.0.0
description: Multi-source research & knowledge synthesis with cross-validation, provenance graph, confidence score
base: skills/fetching
category: Research/Knowledge
provides: [research.run]
security: { inherit: fetching, ssrf_https_only: true }
---

# Research — Deep Multi-Source Knowledge Synthesis

Synthesize knowledge across many sources: fetch → dedupe → cross-validate →
confidence score + provenance graph.

## Usage
```python
from skills.research import research
res = await research("FastAPI best practices",
                     sources=["https://api.example.com/a", "https://api.example.com/b"])
print(res["summary"])      # Synthesized 2 source(s) on ... — NN% confidence
print(res["confidence"])   # 0.0–1.0
print(res["provenance"])   # graph + fetched_at + checksum
```

## Return shape
```json
{
  "summary": "str",
  "confidence": 0.87,
  "contradictions": [],
  "sources_used": ["https://..."],
  "sources_skipped": [],
  "provenance": { "graph": [...], "fetched_at": "ISO", "cache": "MISS", "checksum": "sha256:..." }
}
```

## Security
All outbound traffic routes through `skills.fetching`, inheriting SSRF guard,
HTTPS-only, retry, and cache. localhost/private/metadata hosts are skipped.

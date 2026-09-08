"""Research skill — multi-source fetch, cross-validation, provenance graph.

Synthesizes knowledge across many sources with a confidence score. All fetches
route through ``skills.fetching`` so SSRF/HTTPS/retry/cache are inherited.

Example:
    from skills.research import research
    res = await research("FastAPI", ["https://api.example.com/a"])
    print(res["summary"])
"""
from .main import ResearchSkill, research

__version__ = "1.0.0"
__all__ = ["ResearchSkill", "research"]

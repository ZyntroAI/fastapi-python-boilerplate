"""Prometheus metrics — request/latency/cache/fallback/token coverage."""
from prometheus_client import Counter, Histogram

API_REQUESTS = Counter(
    "onspaceai_api_requests_total", "Total API requests", ["endpoint", "status"]
)
CACHE_HITS = Counter("onspaceai_cache_hits_total", "Cache hits")
CACHE_MISSES = Counter("onspaceai_cache_misses_total", "Cache misses")
FALLBACK_TOTAL = Counter(
    "onspaceai_fallback_total", "Fallback events", ["from_provider", "to_provider"]
)
DEGRADED_TOTAL = Counter("onspaceai_degraded_responses_total", "Degraded/stale responses")
LATENCY = Histogram("onspaceai_request_latency_seconds", "Request latency", ["endpoint"])
TOKEN_TOTAL = Counter("onspaceai_tokens_total", "Total tokens processed", ["model"])
TOKEN_SAVED = Counter("onspaceai_tokens_saved", "Tokens saved by optimization")

"""Cache-reduction toolkit.

Three independent surfaces, one reporting shape:

* ``cache_audit``  — static scan of Python/Node sources and agent-context files
* ``headers``      — HTTP / CDN ``Cache-Control`` analysis and cache-bust checks
* ``redis_audit``  — Redis ``INFO`` memory-pressure and hit-rate verdicts

Everything is pure-stdlib and offline. Nothing here touches a live cache.
"""

from .cache_audit import AuditReport, Finding, scan_path, scan_text
from .headers import analyze_cache_headers, diff_headers, recompute_after_change
from .redis_audit import audit_redis_info, audit_redis_infos

__version__ = "1.0.0"

__all__ = [
    "AuditReport",
    "Finding",
    "scan_path",
    "scan_text",
    "analyze_cache_headers",
    "diff_headers",
    "recompute_after_change",
    "audit_redis_info",
    "audit_redis_infos",
    "__version__",
]

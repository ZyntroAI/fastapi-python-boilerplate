"""access-verification — bounded post-change re-probe loop (wait -> probe -> confirm).

Avoids excessive retries: max_attempts is caller-controlled with a sane cap.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List

MAX_ATTEMPTS = 3


async def verify_access(url: str, probe: Callable[[str], List[str]],
                        attempts: int = MAX_ATTEMPTS) -> Dict[str, Any]:
    """Re-probe until the access state is confirmed stable (or attempts run out).

    Args:
        probe: async callable returning evidence list for a URL.
    """
    results = []
    for i in range(min(attempts, MAX_ATTEMPTS)):
        evidence = await probe(url)
        results.append(evidence)
    # confirmed if all probes agree on the same non-empty classification
    from .access import classify_access
    states = {classify_access(e)["state"] for e in results}
    confirmed = len(states) == 1 and "UNKNOWN" not in states and "INVALID" not in states
    return {"confirmed": confirmed, "states": sorted(states), "attempts": len(results)}

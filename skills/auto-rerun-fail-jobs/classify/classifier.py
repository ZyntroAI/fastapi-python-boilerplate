import re
from typing import Dict, Tuple
from .patterns import FAILURE_PATTERNS

class FailureClassifier:
    RETRYABLE = {"transient", "infrastructure", "rate_limit"}
    NON_RETRYABLE = {"test_failure", "code_failure", "dependency", "permission", "security"}

    @classmethod
    def fingerprint(cls, logs: str) -> str:
        """Extract unique signature from logs"""
        lines = [l for l in logs.splitlines() if l.strip() and any(kw in l.lower()
            for kw in ["error", "failed", "exception", "assertion"])]
        return "\n".join(lines[-5:]) if lines else "unknown"

    @classmethod
    def classify(cls, logs: str) -> Tuple[str, bool]:
        """Return (failure_type, should_retry)"""
        text = logs.lower()
        for ftype, patterns in FAILURE_PATTERNS.items():
            if any(re.search(p, text, re.I) for p in patterns):
                return ftype, ftype in cls.RETRYABLE
        return "unknown", False

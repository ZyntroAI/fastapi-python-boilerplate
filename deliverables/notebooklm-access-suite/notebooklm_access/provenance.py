"""source-access-provenance — append-only in-memory provenance log."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class ProvenanceLog:
    def __init__(self) -> None:
        self._rows: List[Dict[str, Any]] = []

    def record(self, url: str, mode: str, result: str, evidence: List[str]) -> Dict[str, Any]:
        row = {"timestamp": datetime.now(timezone.utc).isoformat(), "url": url,
               "mode": mode, "result": result, "evidence": list(evidence)}
        self._rows.append(row)
        return row

    def rows(self) -> List[Dict[str, Any]]:
        return list(self._rows)

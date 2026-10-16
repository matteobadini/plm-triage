"""Local JSONL audit log of query executions. Never records result data or raw params."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def params_digest(params: dict[str, Any]) -> str:
    canonical = json.dumps(params, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AuditLog:
    def __init__(self, path: Path):
        self.path = path

    def record(
        self,
        query: str,
        params: dict[str, Any],
        *,
        ok: bool,
        rows: int | None = None,
        duration_ms: int | None = None,
        error: str | None = None,
    ) -> None:
        entry = {
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "query": query,
            "params_sha256": params_digest(params),
            "rows": rows,
            "duration_ms": duration_ms,
            "ok": ok,
            "error": error,
        }
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except OSError as exc:
            # Auditing must not break triage; stderr is visible in the MCP server log.
            print(f"plm-db: audit log write failed: {exc}", file=sys.stderr)

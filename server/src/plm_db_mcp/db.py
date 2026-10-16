"""Read-only query execution against SQL Server via pymssql."""

from __future__ import annotations

import contextlib
import re
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from .catalog import Query
from .config import DbSettings

GUARDRAIL_STATEMENTS = ("SET LOCK_TIMEOUT 5000", "SET DEADLOCK_PRIORITY LOW")
READ_UNCOMMITTED_STATEMENT = "SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
LOGIN_TIMEOUT_S = 10
MAX_ERROR_LEN = 300


class Cursor(Protocol):
    description: Sequence[Sequence[Any]] | None

    def execute(self, operation: str, params: Any = ...) -> Any: ...
    def fetchmany(self, size: int) -> list[Sequence[Any]]: ...
    def close(self) -> Any: ...


class Connection(Protocol):
    def cursor(self) -> Cursor: ...
    def close(self) -> Any: ...


ConnectFactory = Callable[[DbSettings, int], Connection]


class QueryError(Exception):
    """Sanitized database failure; safe to show to the model."""

    def __init__(self, message: str, kind: str = "db_error"):
        super().__init__(message)
        self.kind = kind


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[tuple[Any, ...]]
    truncated: bool
    duration_ms: int


def pymssql_connect(settings: DbSettings, timeout_s: int) -> Connection:
    import pymssql

    return pymssql.connect(
        server=settings.host,
        port=str(settings.port),
        user=settings.user,
        password=settings.password,
        database=settings.database,
        login_timeout=LOGIN_TIMEOUT_S,
        timeout=timeout_s,
        tds_version=settings.tds_version,
        appname="plm-triage",
    )


def _close(conn: Connection) -> None:
    with contextlib.suppress(Exception):
        conn.close()


def _is_timeout(exc: BaseException) -> bool:
    text = str(exc).lower()
    return "timed out" in text or "timeout expired" in text or "20003" in text


def _flatten(value: Any) -> str:
    if isinstance(value, (tuple, list)):
        return " ".join(_flatten(v) for v in value)
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value)


def sanitize_error(exc: BaseException, settings: DbSettings | None) -> str:
    """Return a short error text without secrets or connection details."""
    # pymssql errors carry args like (20009, b"DB-Lib error message ...").
    text = _flatten(exc.args) or str(exc)
    text = re.sub(r"(?i)(password|pwd)\s*[=:]\s*\S+", r"\1=<redacted>", text)
    if settings is not None:
        for secret, label in ((settings.password, "<redacted>"), (settings.host, "<host>")):
            if secret:
                text = text.replace(secret, label)
    text = " ".join(text.split())
    if len(text) > MAX_ERROR_LEN:
        text = text[:MAX_ERROR_LEN] + "..."
    return f"{type(exc).__name__}: {text}"


class Executor:
    def __init__(self, settings: DbSettings, connect: ConnectFactory = pymssql_connect):
        self.settings = settings
        self._connect = connect

    def _open(self, timeout_s: int) -> Connection:
        try:
            return self._connect(self.settings, timeout_s)
        except Exception as exc:
            raise QueryError(sanitize_error(exc, self.settings), "connect_error") from None

    def run(self, query: Query, params: dict[str, Any]) -> QueryResult:
        start = time.monotonic()
        conn = self._open(query.timeout_s)
        try:
            cursor = conn.cursor()
            for statement in GUARDRAIL_STATEMENTS:
                cursor.execute(statement)
            if query.isolation == "read_uncommitted":
                cursor.execute(READ_UNCOMMITTED_STATEMENT)
            if query.params:
                cursor.execute(query.sql, params)
            else:
                # Without params pymssql does no substitution, so the SQL goes through verbatim.
                cursor.execute(query.sql)
            columns = [str(col[0]) for col in cursor.description or ()]
            rows = [tuple(r) for r in cursor.fetchmany(query.max_rows + 1)]
        except Exception as exc:
            if _is_timeout(exc):
                raise QueryError(
                    f"query `{query.name}` exceeded timeout of {query.timeout_s}s", "timeout"
                ) from None
            raise QueryError(sanitize_error(exc, self.settings)) from None
        finally:
            _close(conn)
        truncated = len(rows) > query.max_rows
        return QueryResult(
            columns=columns,
            rows=rows[: query.max_rows],
            truncated=truncated,
            duration_ms=int((time.monotonic() - start) * 1000),
        )

    def ping(self) -> dict[str, Any]:
        start = time.monotonic()
        conn = self._open(LOGIN_TIMEOUT_S)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT CAST(SERVERPROPERTY('ProductVersion') AS nvarchar(128)), DB_NAME()"
            )
            row = (cursor.fetchmany(1) or [(None, None)])[0]
        except Exception as exc:
            raise QueryError(sanitize_error(exc, self.settings)) from None
        finally:
            _close(conn)
        return {
            "server_version": row[0],
            "database": row[1],
            "duration_ms": int((time.monotonic() - start) * 1000),
        }

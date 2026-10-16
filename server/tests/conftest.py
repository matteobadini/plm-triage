from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from plm_db_mcp.config import DbSettings

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_CATALOG = REPO_ROOT / "instance-template" / "catalog"

SECRET = "s3cr3t-Pa55"


class FakeCursor:
    def __init__(self, conn: FakeConnection):
        self.conn = conn
        self.description: list[tuple[str]] | None = None

    def execute(self, operation: str, params: Any = None) -> None:
        self.conn.executed.append((operation, params))
        if self.conn.fail_on is not None and self.conn.fail_on in operation:
            raise self.conn.error
        if not operation.startswith("SET "):
            self.description = [(c,) for c in self.conn.columns]

    def fetchmany(self, size: int) -> list[tuple[Any, ...]]:
        self.conn.fetch_sizes.append(size)
        return self.conn.rows[:size]

    def close(self) -> None:
        pass


class FakeConnection:
    def __init__(self, columns=("A",), rows=(), fail_on=None, error=None):
        self.columns = list(columns)
        self.rows = list(rows)
        self.fail_on = fail_on
        self.error = error
        self.executed: list[tuple[str, Any]] = []
        self.fetch_sizes: list[int] = []
        self.closed = False
        self.timeouts: list[int] = []

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def settings() -> DbSettings:
    return DbSettings(
        host="db.example.invalid", port=1433, database="DEMO", user="reader", password=SECRET
    )


@pytest.fixture
def fake_conn() -> FakeConnection:
    return FakeConnection()


def make_connect(conn: FakeConnection):
    def connect(settings: DbSettings, timeout_s: int) -> FakeConnection:
        conn.timeouts.append(timeout_s)
        return conn

    return connect


def write_sql(directory: Path, filename: str, header: str, body: str) -> Path:
    path = directory / filename
    path.write_text(f"/* ---\n{header.strip()}\n--- */\n{body}\n", encoding="utf-8")
    return path

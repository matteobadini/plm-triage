from __future__ import annotations

from pathlib import Path

import pytest
from conftest import SECRET, FakeConnection, make_connect

from plm_db_mcp.catalog import parse_query
from plm_db_mcp.db import (
    GUARDRAIL_STATEMENTS,
    READ_UNCOMMITTED_STATEMENT,
    Executor,
    QueryError,
    sanitize_error,
)


def make_query(isolation="read_committed", max_rows=3, params=True):
    header = (
        "name: q\ndescription: d\nwhen_to_use: w\n"
        f"max_rows: {max_rows}\ntimeout_s: 7\nisolation: {isolation}\n"
    )
    body = "SELECT A FROM DEMO_ITEM"
    if params:
        header += "params:\n  n: {type: int}\n"
        body += " WHERE N = @n"
    return parse_query(f"/* ---\n{header}--- */\n{body}", Path("q.sql"))


def test_guardrails_run_before_query_in_order(settings, fake_conn):
    Executor(settings, make_connect(fake_conn)).run(make_query(), {"n": 1})
    statements = [op for op, _ in fake_conn.executed]
    assert statements == [*GUARDRAIL_STATEMENTS, "SELECT A FROM DEMO_ITEM WHERE N = %(n)s"]
    assert fake_conn.executed[-1][1] == {"n": 1}
    assert fake_conn.timeouts == [7]
    assert fake_conn.closed


def test_read_uncommitted_only_when_opted_in(settings, fake_conn):
    Executor(settings, make_connect(fake_conn)).run(make_query("read_uncommitted"), {"n": 1})
    statements = [op for op, _ in fake_conn.executed]
    assert statements[:3] == [*GUARDRAIL_STATEMENTS, READ_UNCOMMITTED_STATEMENT]


def test_query_without_params_is_sent_without_substitution(settings, fake_conn):
    Executor(settings, make_connect(fake_conn)).run(make_query(params=False), {})
    assert fake_conn.executed[-1] == ("SELECT A FROM DEMO_ITEM", None)


def test_truncation(settings):
    conn = FakeConnection(columns=["A"], rows=[(i,) for i in range(10)])
    result = Executor(settings, make_connect(conn)).run(make_query(max_rows=3), {"n": 1})
    assert conn.fetch_sizes == [4]
    assert result.rows == [(0,), (1,), (2,)]
    assert result.truncated is True
    assert result.columns == ["A"]


def test_not_truncated_at_exact_limit(settings):
    conn = FakeConnection(rows=[(1,), (2,), (3,)])
    result = Executor(settings, make_connect(conn)).run(make_query(max_rows=3), {"n": 1})
    assert result.truncated is False and len(result.rows) == 3


def test_timeout_maps_to_clean_error(settings):
    conn = FakeConnection(
        fail_on="DEMO_ITEM", error=Exception(20003, b"Adaptive Server connection timed out")
    )
    with pytest.raises(QueryError) as exc:
        Executor(settings, make_connect(conn)).run(make_query(), {"n": 1})
    assert exc.value.kind == "timeout"
    assert "exceeded timeout of 7s" in str(exc.value)
    assert conn.closed


def test_db_error_is_sanitized(settings):
    err = Exception(f"Login failed host={settings.host} password={SECRET} pwd: {SECRET}")
    conn = FakeConnection(fail_on="DEMO_ITEM", error=err)
    with pytest.raises(QueryError) as exc:
        Executor(settings, make_connect(conn)).run(make_query(), {"n": 1})
    text = str(exc.value)
    assert SECRET not in text and settings.host not in text
    assert "<redacted>" in text


def test_connect_error_is_sanitized(settings):
    def connect(s, t):
        raise OSError(f"cannot reach {s.host} with {s.password}")

    with pytest.raises(QueryError) as exc:
        Executor(settings, connect).run(make_query(), {"n": 1})
    assert exc.value.kind == "connect_error"
    assert SECRET not in str(exc.value) and settings.host not in str(exc.value)


def test_sanitize_truncates_and_decodes_bytes(settings):
    text = sanitize_error(Exception((20009, b"x" * 1000)), settings)
    assert text.startswith("Exception: 20009 xxx") and text.endswith("...")
    assert len(text) < 400


def test_ping(settings):
    conn = FakeConnection(rows=[("16.0.1000.6", "DEMO")])
    info = Executor(settings, make_connect(conn)).ping()
    assert info["server_version"] == "16.0.1000.6" and info["database"] == "DEMO"

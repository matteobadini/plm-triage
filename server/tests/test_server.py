from __future__ import annotations

import asyncio
import datetime as dt
import decimal
import json
import shutil
import uuid

import pytest
from conftest import SECRET, TEMPLATE_CATALOG, FakeConnection, make_connect
from mcp.server.mcpserver.exceptions import ToolError

from plm_db_mcp.server import build_server, to_json_value

EXPECTED_TOOLS = {"ping", "list_queries", "describe_query", "run_query"}


@pytest.fixture
def instance(tmp_path):
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    for src in TEMPLATE_CATALOG.glob("_example_*.sql"):
        shutil.copy(src, catalog / src.name.removeprefix("_example_"))
    return tmp_path


def env_for(instance):
    return {
        "PLM_UC_INSTANCE_DIR": str(instance),
        "PLM_DB_HOST": "db.example.invalid",
        "PLM_DB_DATABASE": "DEMO",
        "PLM_DB_USER": "reader",
        "PLM_DB_PASSWORD": SECRET,
    }


def call(server, name, args=None):
    return asyncio.run(server.call_tool(name, args or {}))


def error_of(server, name, args=None) -> str:
    """MCPServer.call_tool raises ToolError; over the wire it becomes an is_error result."""
    with pytest.raises(ToolError) as exc:
        call(server, name, args)
    return str(exc.value)


def payload(result):
    assert not result.is_error, result.content
    return result.structured_content


def no_keyring(service, key):
    return None


def test_exactly_four_read_only_tools(instance):
    server = build_server(env_for(instance), no_keyring)
    tools = asyncio.run(server.list_tools())
    assert {t.name for t in tools} == EXPECTED_TOOLS
    assert all(t.annotations and t.annotations.read_only_hint for t in tools)


def test_list_and_describe(instance):
    server = build_server(env_for(instance), no_keyring)
    names = {q["name"] for q in payload(call(server, "list_queries"))["queries"]}
    assert "item_by_number" in names
    desc = payload(call(server, "describe_query", {"name": "item_by_number"}))
    assert desc["params"]["item_number"]["type"] == "str"
    assert "@item_number" in desc["sql"]


def test_run_query_serializes_and_audits(instance):
    rows = [(dt.datetime(2026, 1, 2, 3, 4, 5), decimal.Decimal("1.10"), b"\x01", uuid.UUID(int=1))]
    conn = FakeConnection(columns=["T", "D", "B", "U"], rows=rows)
    server = build_server(env_for(instance), no_keyring, make_connect(conn))
    out = payload(
        call(server, "run_query", {"name": "item_by_number", "params": {"item_number": "P-100"}})
    )
    assert out["rows"] == [
        ["2026-01-02T03:04:05", "1.10", {"base64": "AQ=="}, str(uuid.UUID(int=1))]
    ]
    assert out["truncated"] is False and out["columns"] == ["T", "D", "B", "U"]
    json.dumps(out)
    log = (instance / "logs" / "queries.jsonl").read_text(encoding="utf-8").splitlines()
    entry = json.loads(log[-1])
    assert entry["query"] == "item_by_number" and entry["ok"] is True and entry["rows"] == 1
    assert "P-100" not in log[-1] and len(entry["params_sha256"]) == 64


def test_run_query_invalid_params_is_tool_error_and_audited(instance):
    server = build_server(env_for(instance), no_keyring, make_connect(FakeConnection()))
    error_of(
        server, "run_query", {"name": "item_by_number", "params": {"item_number": "bad value!"}}
    )
    entry = json.loads(
        (instance / "logs" / "queries.jsonl").read_text(encoding="utf-8").splitlines()[-1]
    )
    assert entry["ok"] is False and entry["error"] == "invalid_params"


def test_unknown_query(instance):
    server = build_server(env_for(instance), no_keyring)
    assert "list_queries" in error_of(server, "describe_query", {"name": "nope"})


def test_db_error_reaches_model_sanitized(instance):
    conn = FakeConnection(fail_on="DEMO_ITEM", error=Exception(f"bad login {SECRET}"))
    server = build_server(env_for(instance), no_keyring, make_connect(conn))
    text = error_of(
        server, "run_query", {"name": "item_by_number", "params": {"item_number": "P-1"}}
    )
    assert "bad login" in text and SECRET not in text


def test_ping_ok_and_missing_instance(instance):
    conn = FakeConnection(rows=[("16.0", "DEMO")])
    server = build_server(env_for(instance), no_keyring, make_connect(conn))
    out = payload(call(server, "ping"))
    assert out["ok"] is True and out["catalog_queries"] == 3
    assert out["instance_dir"] == str(instance.resolve())
    assert set(out) == {
        "ok", "instance_dir", "catalog_queries", "server_version", "database", "duration_ms"
    }  # fmt: skip
    bad = build_server({"PLM_DB_HOST": "x"}, no_keyring)
    assert "instance_dir" in error_of(bad, "ping")


def test_to_json_value_fallback():
    assert to_json_value(dt.date(2026, 1, 1)) == "2026-01-01"
    assert to_json_value(object()).startswith("<object")


def test_ping_missing_credentials_reports_instance(instance):
    env = {"PLM_UC_INSTANCE_DIR": str(instance), "PLM_DB_PASSWORD": SECRET}
    text = error_of(build_server(env, no_keyring), "ping")
    assert "Missing database settings" in text and SECRET not in text
    assert json.dumps(str(instance.resolve()))[1:-1] in text and '"catalog_queries": 3' in text

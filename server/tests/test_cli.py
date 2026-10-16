from __future__ import annotations

from conftest import SECRET

from plm_db_mcp import cli


def test_check_without_instance_dir_warns_and_still_pings(monkeypatch, capsys):
    for var in ("PLM_INSTANCE_DIR", "PLM_UC_INSTANCE_DIR"):
        monkeypatch.delenv(var, raising=False)
    for key, value in {
        "PLM_DB_HOST": "db.example.invalid",
        "PLM_DB_DATABASE": "DEMO",
        "PLM_DB_USER": "reader",
        "PLM_DB_PASSWORD": SECRET,
    }.items():
        monkeypatch.setenv(key, value)
    pinged = []

    class FakeExecutor:
        def __init__(self, settings):
            pass

        def ping(self):
            pinged.append(True)
            return {"duration_ms": 1, "database": "DEMO"}

    monkeypatch.setattr(cli, "Executor", FakeExecutor)
    assert cli.check() == 0
    out = capsys.readouterr().out
    assert "instance_dir: WARNING" in out and "ERROR" not in out
    assert '$env:PLM_INSTANCE_DIR="C:\\percorso\\istanza"' in out
    assert "export PLM_INSTANCE_DIR=" in out
    assert pinged and SECRET not in out

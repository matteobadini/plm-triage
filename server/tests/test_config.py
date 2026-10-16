from __future__ import annotations

import pytest

from plm_db_mcp.config import ConfigError, resolve_db_settings, resolve_instance_dir

FULL_UC = {
    "PLM_UC_DB_HOST": "uc-host",
    "PLM_UC_DB_PORT": "1500",
    "PLM_UC_DB_DATABASE": "uc-db",
    "PLM_UC_DB_USER": "uc-user",
    "PLM_UC_DB_PASSWORD": "uc-pass",
}


def keyring_with(values):
    return lambda service, key: values.get(key) if service == "plm-triage" else None


NO_KEYRING = keyring_with({})


def test_env_beats_userconfig_beats_keyring():
    env = {**FULL_UC, "PLM_DB_HOST": "env-host", "PLM_UC_DB_USER": ""}
    kr = keyring_with({"user": "kr-user", "password": "kr-pass", "host": "kr-host"})
    s = resolve_db_settings(env, kr)
    assert (s.host, s.user, s.password, s.port) == ("env-host", "kr-user", "uc-pass", 1500)
    assert s.sources["host"] == "env" and s.sources["user"] == "keyring"
    assert s.sources["password"] == "userConfig"


def test_unexpanded_placeholders_are_ignored():
    env = {k: "${user_config.x}" for k in FULL_UC}
    kr = keyring_with({"host": "h", "database": "d", "user": "u", "password": "p"})
    s = resolve_db_settings(env, kr)
    assert s.host == "h" and s.port == 1433 and s.sources["port"] == "default"


def test_tds_version_default_and_override():
    assert resolve_db_settings(FULL_UC, NO_KEYRING).tds_version == "7.3"
    env = {**FULL_UC, "PLM_UC_DB_TDS_VERSION": "7.4"}
    assert resolve_db_settings(env, NO_KEYRING).tds_version == "7.4"


def test_missing_fields_error_is_actionable_and_secret_free():
    env = {"PLM_UC_DB_PASSWORD": "top-secret"}
    with pytest.raises(ConfigError) as exc:
        resolve_db_settings(env, NO_KEYRING)
    msg = str(exc.value)
    assert "host, database, user" in msg and "plm-db set-credentials" in msg
    assert "top-secret" not in msg


def test_invalid_port():
    with pytest.raises(ConfigError, match="port"):
        resolve_db_settings({**FULL_UC, "PLM_DB_PORT": "abc"}, NO_KEYRING)


def test_password_not_in_repr_or_redacted():
    s = resolve_db_settings(FULL_UC, NO_KEYRING)
    assert "uc-pass" not in repr(s)
    assert s.redacted()["password"] == "<set>"
    assert "uc-pass" not in str(s.redacted())


def test_keyring_failure_is_treated_as_missing():
    def broken(service, key):
        return None

    with pytest.raises(ConfigError):
        resolve_db_settings({}, broken)


def test_instance_dir_resolution_order(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    assert resolve_instance_dir({"PLM_INSTANCE_DIR": str(a), "PLM_UC_INSTANCE_DIR": str(b)}) == a
    assert resolve_instance_dir({"PLM_INSTANCE_DIR": "", "PLM_UC_INSTANCE_DIR": str(b)}) == b
    placeholder = {"PLM_UC_INSTANCE_DIR": "${user_config.instance_dir}"}
    with pytest.raises(ConfigError, match="instance_dir"):
        resolve_instance_dir(placeholder)


def test_instance_dir_must_exist(tmp_path):
    with pytest.raises(ConfigError, match="does not exist"):
        resolve_instance_dir({"PLM_INSTANCE_DIR": str(tmp_path / "missing")})

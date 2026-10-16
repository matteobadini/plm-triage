"""Resolution of database credentials and of the instance directory."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

KEYRING_SERVICE = "plm-triage"
DEFAULT_PORT = 1433
DEFAULT_TDS_VERSION = "7.3"

# Field name -> suffix used by both env prefixes (PLM_DB_<X>, PLM_UC_DB_<X>) and keyring username.
CREDENTIAL_FIELDS = ("host", "port", "database", "user", "password")

KeyringGetter = Callable[[str, str], "str | None"]


class ConfigError(Exception):
    """Raised when configuration is missing or invalid; message is actionable and secret-free."""


@dataclass(frozen=True)
class DbSettings:
    host: str
    port: int
    database: str
    user: str
    password: str = field(repr=False)
    tds_version: str = DEFAULT_TDS_VERSION
    # Where each value came from (env | userConfig | keyring | default); never the value itself.
    sources: Mapping[str, str] = field(default_factory=dict, compare=False)

    def redacted(self) -> dict[str, str]:
        return {
            "host": self.host,
            "port": str(self.port),
            "database": self.database,
            "user": self.user,
            "password": "<set>" if self.password else "<missing>",
            "tds_version": self.tds_version,
            **{f"{k}_source": v for k, v in self.sources.items()},
        }


def _usable(value: str | None) -> str | None:
    """Return value unless empty or an unexpanded `${...}` placeholder from userConfig."""
    if value is None:
        return None
    value = value.strip()
    if not value or value.startswith("${"):
        return None
    return value


def _default_keyring_get(service: str, key: str) -> str | None:
    try:
        import keyring

        return keyring.get_password(service, key)
    except Exception:
        # No usable backend (e.g. headless Linux): treat as "not stored".
        return None


def resolve_db_settings(
    env: Mapping[str, str] | None = None,
    keyring_get: KeyringGetter | None = None,
) -> DbSettings:
    """Resolve each field independently: PLM_DB_* > PLM_UC_DB_* > OS keyring."""
    env = os.environ if env is None else env
    keyring_get = keyring_get or _default_keyring_get

    values: dict[str, str] = {}
    sources: dict[str, str] = {}
    for name in CREDENTIAL_FIELDS:
        suffix = name.upper()
        candidates: list[tuple[str, Callable[[], str | None]]] = [
            ("env", lambda s=suffix: env.get(f"PLM_DB_{s}")),
            ("userConfig", lambda s=suffix: env.get(f"PLM_UC_DB_{s}")),
            ("keyring", lambda n=name: keyring_get(KEYRING_SERVICE, n)),
        ]
        for source, getter in candidates:
            value = _usable(getter())
            if value is not None:
                values[name] = value
                sources[name] = source
                break

    if "port" not in values:
        values["port"] = str(DEFAULT_PORT)
        sources["port"] = "default"

    missing = [n for n in CREDENTIAL_FIELDS if n not in values]
    if missing:
        raise ConfigError(
            "Missing database settings: "
            + ", ".join(missing)
            + ". Set them in the plugin options (userConfig), run `plm-db set-credentials` "
            "in your own terminal, or export PLM_DB_<FIELD> for headless runs."
        )

    try:
        port = int(values["port"])
    except ValueError:
        raise ConfigError(f"Invalid database port (source: {sources['port']}).") from None

    tds = (
        _usable(env.get("PLM_DB_TDS_VERSION"))
        or _usable(env.get("PLM_UC_DB_TDS_VERSION"))
        or DEFAULT_TDS_VERSION
    )
    return DbSettings(
        host=values["host"],
        port=port,
        database=values["database"],
        user=values["user"],
        password=values["password"],
        tds_version=tds,
        sources=sources,
    )


def resolve_instance_dir(env: Mapping[str, str] | None = None) -> Path:
    """PLM_INSTANCE_DIR > PLM_UC_INSTANCE_DIR (userConfig `instance_dir`)."""
    env = os.environ if env is None else env
    raw = _usable(env.get("PLM_INSTANCE_DIR")) or _usable(env.get("PLM_UC_INSTANCE_DIR"))
    if raw is None:
        raise ConfigError(
            "Instance directory not configured. Set the plugin option `instance_dir` to the "
            "local clone of your team's private instance repo, or export PLM_INSTANCE_DIR."
        )
    path = Path(raw).expanduser()
    if not path.is_dir():
        raise ConfigError(f"Instance directory does not exist: {path}")
    return path


def catalog_dir(instance_dir: Path) -> Path:
    return instance_dir / "catalog"


def audit_log_path(instance_dir: Path) -> Path:
    return instance_dir / "logs" / "queries.jsonl"

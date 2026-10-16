"""`plm-db` CLI: store credentials in the OS keyring and check the configuration."""

from __future__ import annotations

import argparse
import getpass
import sys

from .catalog import CatalogError, load_catalog
from .config import (
    DEFAULT_PORT,
    KEYRING_SERVICE,
    ConfigError,
    catalog_dir,
    resolve_db_settings,
    resolve_instance_dir,
)
from .db import Executor, QueryError


def set_credentials() -> int:
    import keyring

    print(f"Credentials are stored in the OS keyring (service `{KEYRING_SERVICE}`).")
    values = {
        "host": input("Host: ").strip(),
        "port": input(f"Port [{DEFAULT_PORT}]: ").strip() or str(DEFAULT_PORT),
        "database": input("Database: ").strip(),
        "user": input("User: ").strip(),
        "password": getpass.getpass("Password (hidden): "),
    }
    empty = [k for k, v in values.items() if not v]
    if empty:
        print(f"Aborted: empty values for {', '.join(empty)}.", file=sys.stderr)
        return 2
    try:
        for key, value in values.items():
            keyring.set_password(KEYRING_SERVICE, key, value)
    except Exception as exc:
        print(
            f"Keyring unavailable ({type(exc).__name__}). Use PLM_DB_* env vars.", file=sys.stderr
        )
        return 1
    print("Saved. Run `plm-db check` to verify.")
    return 0


INSTANCE_DIR_HINT = (
    'hint: PowerShell: $env:PLM_INSTANCE_DIR="C:\\percorso\\istanza"  |  '
    'bash: export PLM_INSTANCE_DIR="/percorso/istanza"'
)


def check() -> int:
    status = 0
    try:
        instance = resolve_instance_dir().resolve()
    except ConfigError as exc:
        # Not fatal: the DB connection can still be tested without the instance dir.
        print(f"instance_dir: WARNING {exc}")
        print(INSTANCE_DIR_HINT)
    else:
        print(f"instance_dir: {instance}")
        try:
            queries = load_catalog(catalog_dir(instance))
            print(f"catalog: {len(queries)} queries OK")
        except CatalogError as exc:
            print(f"catalog: ERROR {exc}")
            status = 1
    try:
        settings = resolve_db_settings()
    except ConfigError as exc:
        print(f"credentials: ERROR {exc}")
        return 1
    for key, value in settings.redacted().items():
        print(f"{key}: {value}")
    try:
        info = Executor(settings).ping()
    except QueryError as exc:
        print(f"ping: ERROR {exc}")
        return 1
    print(f"ping: OK ({info['duration_ms']} ms, database {info['database']})")
    return status


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="plm-db", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "set-credentials", help="prompt for DB credentials and store them in the keyring"
    )
    sub.add_parser("check", help="verify instance dir, catalog, credentials and connectivity")
    args = parser.parse_args(argv)
    sys.exit(set_credentials() if args.command == "set-credentials" else check())

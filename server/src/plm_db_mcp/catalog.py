"""Loading and validation of the named-query catalog (.sql files with a YAML header)."""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_MAX_ROWS = 50
MAX_ROWS_CAP = 500
DEFAULT_TIMEOUT_S = 15
TIMEOUT_CAP_S = 60
ISOLATION_LEVELS = ("read_committed", "read_uncommitted")
PARAM_TYPES = ("int", "str", "date", "enum")

FORBIDDEN_KEYWORDS = (
    "INTO", "EXEC", "EXECUTE", "WAITFOR", "OPENROWSET", "OPENQUERY", "OPENDATASOURCE",
    "INSERT", "UPDATE", "DELETE", "MERGE", "DROP", "ALTER", "CREATE", "TRUNCATE", "GRANT",
    "DENY", "REVOKE", "BACKUP", "RESTORE", "DBCC", "KILL", "SHUTDOWN", "RECONFIGURE",
    "USE", "SET", "DECLARE", "BEGIN", "COMMIT", "ROLLBACK", "SAVE",
    "IF", "WHILE", "GOTO", "RETURN", "RAISERROR", "THROW", "PRINT",
    "WRITETEXT", "UPDATETEXT", "READTEXT", "BULK", "OPENXML",
)  # fmt: skip
# Also rejected: identifiers starting with xp_/sp_ (system procedures such as sp_executesql).
# `USE` is allowed only in the query hints `OPTION (USE HINT(...))` and `USE PLAN`.

_HEADER_RE = re.compile(r"\A\s*/\*\s*---[ \t]*\r?\n(.*?)\r?\n[ \t]*---\s*\*/", re.DOTALL)
_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_FORBIDDEN_RE = re.compile(
    r"\b(?!USE\s+(?:HINT|PLAN)\b)(" + "|".join(FORBIDDEN_KEYWORDS) + r"|(?:xp|sp)_\w*)\b",
    re.IGNORECASE,
)
_WORD_OR_PAREN_RE = re.compile(r"\w+|[()]")
_SET_OPERATORS = {"UNION", "ALL", "EXCEPT", "INTERSECT"}
# A single T-SQL token that must be kept or masked as a unit.
_TOKEN_RE = re.compile(
    r"""
      (?P<str>N?'(?:[^']|'')*')          # string literal ('' escapes a quote)
    | (?P<line>--[^\n]*)                 # line comment
    | (?P<block>/\*.*?\*/)               # block comment
    | (?P<ident>\[(?:[^\]]|\]\])*\]|"(?:[^"]|"")*")  # quoted identifier
    | (?P<sysvar>@@\w+)
    | (?P<var>@\w+)
    """,
    re.DOTALL | re.VERBOSE,
)
_HEADER_KEYS = {
    "name", "description", "when_to_use", "params", "max_rows", "timeout_s", "isolation",
}  # fmt: skip
_PARAM_KEYS = {"type", "required", "max_len", "pattern", "values", "description"}


class CatalogError(Exception):
    """Invalid catalog file or invalid query parameters."""


@dataclass(frozen=True)
class ParamSpec:
    name: str
    type: str
    required: bool = True
    max_len: int | None = None
    pattern: str | None = None
    values: tuple[str, ...] = ()
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"type": self.type, "required": self.required}
        if self.max_len is not None:
            out["max_len"] = self.max_len
        if self.pattern is not None:
            out["pattern"] = self.pattern
        if self.values:
            out["values"] = list(self.values)
        if self.description:
            out["description"] = self.description
        return out


@dataclass(frozen=True)
class Query:
    name: str
    description: str
    when_to_use: str
    params: dict[str, ParamSpec]
    max_rows: int
    timeout_s: int
    isolation: str
    source_sql: str  # body as written, with @param
    sql: str  # body for pymssql, with %(param)s
    path: Path = field(compare=False)

    def summary(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "when_to_use": self.when_to_use}

    def describe(self) -> dict[str, Any]:
        return {
            **self.summary(),
            "params": {n: p.to_dict() for n, p in self.params.items()},
            "max_rows": self.max_rows,
            "timeout_s": self.timeout_s,
            "isolation": self.isolation,
            "sql": self.source_sql,
        }


def _bounded_int(header: dict[str, Any], key: str, default: int, cap: int) -> int:
    value = header.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= cap:
        raise CatalogError(f"`{key}` must be an integer between 1 and {cap}")
    return value


def _parse_param(name: str, raw: Any) -> ParamSpec:
    if not _NAME_RE.match(name):
        raise CatalogError(f"invalid parameter name `{name}`")
    if not isinstance(raw, dict):
        raise CatalogError(f"parameter `{name}` must be a mapping")
    unknown = set(raw) - _PARAM_KEYS
    if unknown:
        raise CatalogError(f"parameter `{name}`: unknown keys {sorted(unknown)}")
    ptype = raw.get("type")
    if ptype not in PARAM_TYPES:
        raise CatalogError(f"parameter `{name}`: type must be one of {list(PARAM_TYPES)}")
    if ptype != "str" and ("max_len" in raw or "pattern" in raw):
        raise CatalogError(f"parameter `{name}`: max_len/pattern apply only to type str")
    values = raw.get("values")
    if ptype == "enum":
        if (
            not isinstance(values, list)
            or not values
            or not all(isinstance(v, str) for v in values)
        ):
            raise CatalogError(f"parameter `{name}`: enum needs a non-empty list of string values")
    elif values is not None:
        raise CatalogError(f"parameter `{name}`: values apply only to type enum")
    max_len = raw.get("max_len")
    if max_len is not None and (isinstance(max_len, bool) or not isinstance(max_len, int)):
        raise CatalogError(f"parameter `{name}`: max_len must be an integer")
    pattern = raw.get("pattern")
    if pattern is not None:
        try:
            re.compile(pattern)
        except (re.error, TypeError) as exc:
            raise CatalogError(f"parameter `{name}`: invalid pattern ({exc})") from None
    required = raw.get("required", True)
    if not isinstance(required, bool):
        raise CatalogError(f"parameter `{name}`: required must be true or false")
    return ParamSpec(
        name=name,
        type=ptype,
        required=required,
        max_len=max_len,
        pattern=pattern,
        values=tuple(values or ()),
        description=str(raw.get("description", "")),
    )


def _translate_body(body: str, declared: set[str]) -> str:
    """Check the SQL body and map `@param` to pymssql `%(param)s`.

    Keyword checks are defense in depth only: database permissions are the real boundary.
    """
    if "%(" in body:
        # pymssql would treat a literal `%(` as a placeholder.
        raise CatalogError("literal `%(` is not allowed in the SQL body")
    code_parts: list[str] = []  # body with literals/comments/identifiers masked
    out: list[str] = []
    used: set[str] = set()
    pos = 0
    for m in _TOKEN_RE.finditer(body):
        code_parts.append(body[pos : m.start()])
        out.append(body[pos : m.start()])
        pos = m.end()
        token = m.group(0)
        if m.lastgroup == "var":
            pname = token[1:]
            if pname not in declared:
                raise CatalogError(f"undeclared variable `{token}`")
            used.add(pname)
            code_parts.append(" 0 ")
            out.append(f"%({pname})s")
        elif m.lastgroup == "sysvar":
            code_parts.append(" 0 ")
            out.append(token)
        else:
            code_parts.append(" ")
            out.append(token)
    code_parts.append(body[pos:])
    out.append(body[pos:])
    code = "".join(code_parts)

    unused = declared - used
    if unused:
        raise CatalogError(f"declared but unused parameters: {sorted(unused)}")
    stripped = code.strip()
    if stripped.endswith(";"):
        stripped = stripped[:-1].rstrip()
    if ";" in stripped:
        raise CatalogError("multiple statements are not allowed")
    first = stripped.split(None, 1)[0].upper() if stripped else ""
    if first not in ("SELECT", "WITH"):
        raise CatalogError("query must start with SELECT or WITH")
    bad = _FORBIDDEN_RE.search(stripped)
    if bad:
        raise CatalogError(f"forbidden keyword `{bad.group(1).upper()}`")
    _check_single_select(stripped)
    return "".join(out).strip()


def _check_single_select(code: str) -> None:
    """Reject a second statement written without `;` (e.g. `SELECT 1 SELECT 2`).

    `code` has comments, strings and identifiers masked. At parenthesis depth 0 a SELECT is
    allowed only as the main statement (after an optional `WITH ... AS (...)` chain) or right
    after a set operator; SELECTs inside parentheses (subqueries, CTE bodies) are unrestricted.
    """
    depth = 0
    seen_main = False
    prev = ""
    for token in _WORD_OR_PAREN_RE.findall(code):
        word = token.upper()
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
            if depth < 0:
                raise CatalogError("unbalanced parentheses")
        elif word == "SELECT" and depth == 0:
            if seen_main and prev not in _SET_OPERATORS:
                raise CatalogError("multiple statements are not allowed")
            seen_main = True
        prev = word
    if depth != 0:
        raise CatalogError("unbalanced parentheses")
    if not seen_main:
        raise CatalogError("query must contain a top-level SELECT")


def parse_query(text: str, path: Path) -> Query:
    m = _HEADER_RE.match(text)
    if not m:
        raise CatalogError("missing YAML header in a leading `/* --- ... --- */` block")
    try:
        header = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        raise CatalogError(f"invalid YAML header: {exc}") from None
    if not isinstance(header, dict):
        raise CatalogError("YAML header must be a mapping")
    unknown = set(header) - _HEADER_KEYS
    if unknown:
        raise CatalogError(f"unknown header keys {sorted(unknown)}")
    for key in ("name", "description", "when_to_use"):
        if not isinstance(header.get(key), str) or not header[key].strip():
            raise CatalogError(f"`{key}` is required and must be a non-empty string")
    name = header["name"]
    if not _NAME_RE.match(name):
        raise CatalogError(f"invalid query name `{name}` (lowercase letters, digits, _)")
    raw_params = header.get("params") or {}
    if not isinstance(raw_params, dict):
        raise CatalogError("`params` must be a mapping")
    params = {pname: _parse_param(str(pname), spec) for pname, spec in raw_params.items()}
    isolation = header.get("isolation", "read_committed")
    if isolation not in ISOLATION_LEVELS:
        raise CatalogError(f"`isolation` must be one of {list(ISOLATION_LEVELS)}")
    source_sql = text[m.end() :].strip()
    return Query(
        name=name,
        description=header["description"].strip(),
        when_to_use=header["when_to_use"].strip(),
        params=params,
        max_rows=_bounded_int(header, "max_rows", DEFAULT_MAX_ROWS, MAX_ROWS_CAP),
        timeout_s=_bounded_int(header, "timeout_s", DEFAULT_TIMEOUT_S, TIMEOUT_CAP_S),
        isolation=isolation,
        source_sql=source_sql,
        sql=_translate_body(source_sql, set(params)),
        path=path,
    )


def load_query_file(path: Path) -> Query:
    try:
        return parse_query(path.read_text(encoding="utf-8"), path)
    except CatalogError as exc:
        raise CatalogError(f"{path.name}: {exc}") from None


def load_catalog(directory: Path) -> dict[str, Query]:
    """Load every `*.sql` in directory; files starting with `_` (examples, drafts) are skipped."""
    if not directory.is_dir():
        raise CatalogError(f"catalog directory not found: {directory}")
    queries: dict[str, Query] = {}
    errors: list[str] = []
    for path in sorted(directory.glob("*.sql")):
        if path.name.startswith("_"):
            continue
        try:
            query = load_query_file(path)
        except CatalogError as exc:
            errors.append(str(exc))
            continue
        if query.name in queries:
            errors.append(f"{path.name}: duplicate query name `{query.name}`")
            continue
        queries[query.name] = query
    if errors:
        raise CatalogError("invalid catalog:\n- " + "\n- ".join(errors))
    return queries


def validate_params(query: Query, params: dict[str, Any] | None) -> dict[str, Any]:
    """Check caller-supplied params against the query spec and return driver-ready values."""
    params = params or {}
    unknown = set(params) - set(query.params)
    if unknown:
        raise CatalogError(f"unknown parameters for `{query.name}`: {sorted(unknown)}")
    result: dict[str, Any] = {}
    for name, spec in query.params.items():
        value = params.get(name)
        if value is None:
            if spec.required:
                raise CatalogError(f"missing required parameter `{name}`")
            result[name] = None
            continue
        result[name] = _coerce(spec, value)
    return result


def _coerce(spec: ParamSpec, value: Any) -> Any:
    name = spec.name
    if spec.type == "int":
        if isinstance(value, bool):
            raise CatalogError(f"`{name}` must be an integer")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and re.fullmatch(r"-?\d{1,18}", value.strip()):
            return int(value)
        raise CatalogError(f"`{name}` must be an integer")
    if spec.type == "date":
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value.strip()):
            raise CatalogError(f"`{name}` must be an ISO date string (YYYY-MM-DD)")
        try:
            return dt.date.fromisoformat(value.strip())
        except ValueError:
            raise CatalogError(f"`{name}` must be an ISO date string (YYYY-MM-DD)") from None
    if not isinstance(value, str):
        raise CatalogError(f"`{name}` must be a string")
    if spec.type == "enum":
        if value not in spec.values:
            raise CatalogError(f"`{name}` must be one of {list(spec.values)}")
        return value
    if spec.max_len is not None and len(value) > spec.max_len:
        raise CatalogError(f"`{name}` exceeds max_len {spec.max_len}")
    if spec.pattern is not None and not re.fullmatch(spec.pattern, value):
        raise CatalogError(f"`{name}` does not match the required pattern")
    return value

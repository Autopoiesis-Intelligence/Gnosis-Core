from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Iterator, Mapping

from .handoff import ContextHandoff
from .model import TaskContext

TASK_STATES = frozenset({
    "proposed", "active", "blocked", "awaiting_review",
    "corrective", "verified", "accepted", "closed",
})
VERIFICATION_STATES = frozenset({
    "reported", "implemented", "runtime_verified",
    "independently_verified", "accepted", "rejected",
})

TASK_STATE_TRANSITIONS = {
    "proposed": frozenset({"active", "blocked", "closed"}),
    "active": frozenset({"blocked", "awaiting_review", "corrective", "verified", "closed"}),
    "blocked": frozenset({"active", "corrective", "closed"}),
    "awaiting_review": frozenset({"active", "blocked", "corrective", "verified", "accepted"}),
    "corrective": frozenset({"active", "blocked", "awaiting_review", "closed"}),
    "verified": frozenset({"active", "corrective", "accepted", "closed"}),
    "accepted": frozenset({"corrective", "closed"}),
    "closed": frozenset(),
}

CONTEXT_SCHEMA = """
CREATE TABLE IF NOT EXISTS task_contexts (
    context_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    organization_scope TEXT,
    user_scope TEXT NOT NULL,
    objective TEXT NOT NULL,
    current_task_state TEXT NOT NULL,
    required_inputs TEXT NOT NULL,
    context_references TEXT NOT NULL,
    evidence_references TEXT NOT NULL,
    implementation_state TEXT NOT NULL,
    verification_state TEXT NOT NULL,
    unresolved_findings TEXT NOT NULL,
    next_permitted_action TEXT NOT NULL,
    available_capabilities TEXT NOT NULL,
    allowed_data_sources TEXT NOT NULL,
    allowed_output_destinations TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    revision INTEGER NOT NULL CHECK(revision >= 0)
);
"""


class ContextRevisionConflict(RuntimeError):
    pass


class ContextNotFound(KeyError):
    pass


_COLLECTION_FIELDS = (
    "required_inputs",
    "context_references",
    "evidence_references",
    "unresolved_findings",
    "available_capabilities",
    "allowed_data_sources",
    "allowed_output_destinations",
)


def _assert_json_value(value: Any, field_name: str, path: str) -> None:
    """Reject values that JSON would silently coerce or cannot represent."""
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if isfinite(value):
            return
        raise ValueError(f"{field_name} contains a non-finite number at {path}")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _assert_json_value(item, field_name, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{field_name} contains a non-string object key at {path}")
            _assert_json_value(item, field_name, f"{path}.{key}")
        return
    raise ValueError(f"{field_name} contains a non-JSON value at {path}")


def _json(value: tuple[Any, ...], field_name: str) -> str:
    if not isinstance(value, tuple):
        raise ValueError(f"{field_name} must be a tuple of JSON values")
    for index, item in enumerate(value):
        _assert_json_value(item, field_name, f"[{index}]")
    return json.dumps(
        list(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


@contextmanager
def _transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Keep Context writes transactional without importing Core/Memory-adjacent Storage."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.rollback()
        raise
    else:
        conn.commit()


def _decode(value: str) -> tuple[Any, ...]:
    decoded = json.loads(value)
    if not isinstance(decoded, list):
        raise ValueError("context collection must be a JSON list")
    return tuple(decoded)


class TaskContextRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.executescript(CONTEXT_SCHEMA)

    def create_context(self, context: TaskContext) -> TaskContext:
        self._validate(context)
        with _transaction(self._conn):
            self._conn.execute(
                """INSERT INTO task_contexts
                (context_id,project_id,task_id,organization_scope,user_scope,objective,current_task_state,
                 required_inputs,context_references,evidence_references,implementation_state,verification_state,
                 unresolved_findings,next_permitted_action,available_capabilities,allowed_data_sources,
                 allowed_output_destinations,created_at,updated_at,revision)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                self._params(context),
            )
        return context

    def get_context(self, context_id: str) -> TaskContext:
        row = self._conn.execute(
            "SELECT * FROM task_contexts WHERE context_id=?", (context_id,)
        ).fetchone()
        if row is None:
            raise ContextNotFound(context_id)
        return self._from_row(row)

    def update_context(
        self, context_id: str, expected_revision: int, patch: Mapping[str, Any]
    ) -> TaskContext:
        if isinstance(expected_revision, bool) or not isinstance(expected_revision, int):
            raise ValueError("expected_revision must be an integer")
        if expected_revision < 0:
            raise ValueError("expected_revision must be non-negative")

        current = self.get_context(context_id)
        if current.revision != expected_revision:
            raise ContextRevisionConflict(
                f"stale revision: expected {expected_revision}, current {current.revision}"
            )

        immutable = {
            "context_id", "project_id", "task_id", "user_scope",
            "organization_scope", "created_at", "updated_at", "revision",
        }
        allowed = set(current.__dataclass_fields__) - immutable
        if set(patch) - allowed:
            raise ValueError("patch contains immutable or unknown fields")

        patch_values = dict(patch)
        patch_values["updated_at"] = datetime.now(timezone.utc).isoformat()
        updated = replace(current, **patch_values, revision=current.revision + 1)
        next_state = updated.current_task_state
        if next_state != current.current_task_state and next_state not in TASK_STATE_TRANSITIONS[current.current_task_state]:
            raise ValueError(
                f"invalid task state transition: {current.current_task_state!r} -> {next_state!r}"
            )
        self._validate(updated)
        p = self._params(updated)
        with _transaction(self._conn):
            result = self._conn.execute(
                """UPDATE task_contexts SET project_id=?,task_id=?,organization_scope=?,
                user_scope=?,objective=?,current_task_state=?,required_inputs=?,context_references=?,
                evidence_references=?,implementation_state=?,verification_state=?,unresolved_findings=?,
                next_permitted_action=?,available_capabilities=?,allowed_data_sources=?,
                allowed_output_destinations=?,updated_at=?,revision=?
                WHERE context_id=? AND revision=?""",
                (p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12],
                 p[13], p[14], p[15], p[16], p[18], p[19], context_id, expected_revision),
            )
            if result.rowcount != 1:
                raise ContextRevisionConflict("stale revision")
        return updated

    def reconstruct_context(self, context_id: str) -> ContextHandoff:
        return ContextHandoff.from_context(self.get_context(context_id))

    @staticmethod
    def _validate(context: TaskContext) -> None:
        string_fields = (
            "context_id", "project_id", "task_id", "user_scope", "objective",
            "current_task_state", "implementation_state", "verification_state",
            "next_permitted_action", "created_at", "updated_at",
        )
        for field_name in string_fields:
            if not isinstance(getattr(context, field_name), str):
                raise ValueError(f"{field_name} must be a string")
        if context.organization_scope is not None and not isinstance(context.organization_scope, str):
            raise ValueError("organization_scope must be a string or None")
        if not context.context_id or not context.project_id or not context.task_id:
            raise ValueError("context identity fields are required")
        if not context.user_scope:
            raise ValueError("user_scope is required")
        if context.current_task_state not in TASK_STATES:
            raise ValueError(f"invalid current_task_state: {context.current_task_state!r}")
        if context.verification_state not in VERIFICATION_STATES:
            raise ValueError(f"invalid verification_state: {context.verification_state!r}")
        if isinstance(context.revision, bool) or not isinstance(context.revision, int):
            raise ValueError("revision must be an integer")
        if context.revision < 0:
            raise ValueError("revision must be non-negative")
        for field_name in _COLLECTION_FIELDS:
            value = getattr(context, field_name)
            if not isinstance(value, tuple):
                raise ValueError(f"{field_name} must be a tuple of JSON values")
            _json(value, field_name)

    @staticmethod
    def _params(c: TaskContext) -> tuple[Any, ...]:
        return (
            c.context_id, c.project_id, c.task_id, c.organization_scope, c.user_scope, c.objective,
            c.current_task_state, _json(c.required_inputs, "required_inputs"), _json(c.context_references, "context_references"),
            _json(c.evidence_references, "evidence_references"), c.implementation_state, c.verification_state,
            _json(c.unresolved_findings, "unresolved_findings"), c.next_permitted_action, _json(c.available_capabilities, "available_capabilities"),
            _json(c.allowed_data_sources, "allowed_data_sources"), _json(c.allowed_output_destinations, "allowed_output_destinations"),
            c.created_at, c.updated_at, c.revision,
        )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> TaskContext:
        return TaskContext(
            context_id=row["context_id"], project_id=row["project_id"], task_id=row["task_id"],
            user_scope=row["user_scope"], objective=row["objective"], current_task_state=row["current_task_state"],
            required_inputs=_decode(row["required_inputs"]), context_references=_decode(row["context_references"]),
            evidence_references=_decode(row["evidence_references"]), implementation_state=row["implementation_state"],
            verification_state=row["verification_state"], unresolved_findings=_decode(row["unresolved_findings"]),
            next_permitted_action=row["next_permitted_action"], available_capabilities=_decode(row["available_capabilities"]),
            allowed_data_sources=_decode(row["allowed_data_sources"]), allowed_output_destinations=_decode(row["allowed_output_destinations"]),
            organization_scope=row["organization_scope"], created_at=row["created_at"],
            updated_at=row["updated_at"], revision=row["revision"],
        )

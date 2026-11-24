"""Bounded pending-event handling for SCDR03 development, not source custody."""
from __future__ import annotations

import hashlib
import json

MAX_PENDING_ROWS = 2
MAX_STAGED_ROWS = 3
MAX_QUARANTINE_BYTES = 4096
ZERO_DIGEST = "0" * 64


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def checked_rows(rows, normalize, *, limit=MAX_PENDING_ROWS):
    """Copy validated public rows; reject oversized, duplicate or malformed pending state."""
    if type(rows) is not list or len(rows) > limit:
        raise ValueError("SCDR_NUM05_QUARANTINE_ROW_LIMIT")
    clean = []
    ids = set()
    for row in rows:
        item = normalize(row)
        identifier = item["id"]
        if identifier in ids:
            raise ValueError("SCDR_NUM05_QUARANTINE_DUPLICATE")
        ids.add(identifier)
        clean.append(item)
    if len(_encode(clean)) > MAX_QUARANTINE_BYTES:
        raise ValueError("SCDR_NUM05_QUARANTINE_BYTE_LIMIT")
    return clean


def stage_row(rows, row, normalize, *, frozen_count, max_frozen):
    """Reject before accepting any event if no archive slot remains."""
    if frozen_count >= max_frozen:
        raise ValueError("SCDR_NUM05_FROZEN_CAPACITY_EXHAUSTED")
    return checked_rows([*rows, row], normalize, limit=MAX_STAGED_ROWS)


def account_unassigned(rows, count, head):
    """Account for rejected pending events, not retention or an authenticated ledger."""
    for row in rows:
        head = hashlib.sha256(_encode([head, row, "UNASSIGNED_INTERRUPTED"])).hexdigest()
        count += 1
    return count, head


def validate_accounting(count, head, events_seen):
    if (type(count) is not int or type(events_seen) is not int
            or not 0 <= count <= events_seen or type(head) is not str
            or len(head) != 64 or any(c not in "0123456789abcdef" for c in head)
            or (count == 0 and head != ZERO_DIGEST)
            or (count > 0 and head == ZERO_DIGEST)):
        raise ValueError("SCDR_NUM05_QUARANTINE_ACCOUNTING")

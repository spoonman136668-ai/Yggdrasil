"""Append-only, fail-closed PUBLIC development source-action custody.

External source owner operates the original environment. This journal sees only
public fields and a source *identity*, never hidden environment state, seeds,
RNG, transition matrices, or oracles. A durable INTENT is fsynced before each
source-side effect; a public RESULT is fsynced after each confirmed return.
Unknown effects are not reissued. This is engineering recovery infrastructure,
NOT independent authentication, protected first-use permission, or accepted
scientific evidence. The filesystem journal is hash-chained but NOT signed.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re

from .itd02_local_ring_memory_dev import ACTIONS, OBSERVATIONS

SCHEMA = "ygg.itd02.public-fit-source-custody.dev.v1"
MAX_STEPS = 512
MAX_JOURNAL_BYTES = 512_000
ZERO = "0" * 64


class SourceCustodyDenied(ValueError):
    pass


def _need(ok, code):
    if not ok:
        raise SourceCustodyDenied("YGG_PUBLIC_CUSTODY_" + code)


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _hash(value):
    return hashlib.sha256(_encode(value)).hexdigest()


def _read_checked(path, limit):
    _need(path.is_file() and not path.is_symlink(), "FILE_MISSING_OR_SYMLINK")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        raw = os.read(fd, limit + 1)
        _need(len(raw) <= limit, "FILE_OVERSIZE")
        return raw
    finally:
        os.close(fd)


def _append(fd, record):
    raw = _encode(record) + b"\n"
    # One writer owns an O_EXCL-created journal for the lifetime of a session.
    # A short/torn append is fatal, and inspect() will refuse the journal.
    while raw:
        count = os.write(fd, raw)
        _need(count > 0, "JOURNAL_WRITE_FAILED")
        raw = raw[count:]
    os.fsync(fd)


def _atomic_checkpoint(directory, payload):
    name = directory / "learned-checkpoint.bin"
    _need(type(payload) is bytes and 0 < len(payload) <= 65536,
          "CHECKPOINT_SIZE")
    _need(not name.exists() and not name.is_symlink(), "CHECKPOINT_ALREADY_EXISTS")
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        rest = payload
        while rest:
            count = os.write(fd, rest)
            _need(count > 0, "CHECKPOINT_WRITE_FAILED")
            rest = rest[count:]
        os.fsync(fd)
    finally:
        os.close(fd)
    return hashlib.sha256(payload).hexdigest()


def inspect_custody(directory, *, expected_source_sha256=None):
    """Read-only cold-process check; NEVER replays or reconstructs a step."""
    root = Path(directory)
    _need(root.is_dir() and not root.is_symlink(), "INVALID_DIRECTORY")
    raw = _read_checked(root / "public-events.jsonl", MAX_JOURNAL_BYTES)
    _need(raw and raw.endswith(b"\n"), "TORN_EVENT_STREAM")
    lines = raw.splitlines()
    _need(1 <= len(lines) <= 2 * MAX_STEPS + 4, "EVENT_COUNT")
    prev = ZERO
    previous_kind = None
    events = []
    for index, line in enumerate(lines):
        _need(0 < len(line) <= 2048, "EVENT_SIZE")
        try:
            record = json.loads(line)
        except (UnicodeDecodeError, ValueError) as exc:
            raise SourceCustodyDenied("YGG_PUBLIC_CUSTODY_INVALID_EVENT_JSON") from exc
        _need(type(record) is dict and set(record) ==
              {"seq", "prev", "event", "digest"}, "EVENT_FIELDS")
        body = {"seq": record["seq"], "prev": record["prev"],
                "event": record["event"]}
        _need(type(record["seq"]) is int and record["seq"] == index and
              record["prev"] == prev and
              _hash(body) == record["digest"], "EVENT_CHAIN_BROKEN")
        event = record["event"]
        _need(type(event) is dict and type(event.get("kind")) is str,
              "INVALID_EVENT_PAYLOAD")
        kind = event["kind"]
        if index == 0:
            _need(kind == "header" and set(event) ==
                  {"kind", "schema", "source_sha256", "episode", "max_steps",
                   "role"}, "INVALID_HEADER")
            _need(event["schema"] == SCHEMA and
                  type(event["source_sha256"]) is str and
                  re.fullmatch("[0-9a-f]{64}", event["source_sha256"]) and
                  type(event["episode"]) is str and
                  re.fullmatch("[a-zA-Z0-9_-]{1,60}", event["episode"]) and
                  type(event["max_steps"]) is int and
                  1 <= event["max_steps"] <= MAX_STEPS and
                  event["role"] == "OWNER_PUBLIC_FIT_DEVELOPMENT_ONLY",
                  "HEADER_IDENTITY")
            if expected_source_sha256 is not None:
                _need(event["source_sha256"] == expected_source_sha256,
                      "SOURCE_IDENTITY_CHANGED")
        else:
            permitted = {
                "header": ("reset_intent",),
                "reset_intent": ("reset_result",),
                "reset_result": ("step_intent",),
                "step_intent": ("step_result",),
                "step_result": ("step_intent", "checkpoint_intent"),
                "checkpoint_intent": ("checkpoint_result",),
                "checkpoint_result": (),
            }
            _need(kind in permitted[previous_kind], "INVALID_EVENT_SEQUENCE")
            if kind == "reset_intent":
                _need(set(event) == {"kind"}, "RESET_INTENT_FIELDS")
            if kind == "reset_result":
                _need(set(event) == {"kind", "observation"} and
                      type(event["observation"]) is str and
                      event["observation"] in OBSERVATIONS,
                      "RESET_PUBLIC_FIELDS")
            if kind == "step_intent":
                _need(set(event) == {"kind", "action", "index"} and
                      event["action"] in ACTIONS and
                      type(event["index"]) is int and
                      event["index"] == sum(x["kind"] == "step_intent" for x in events),
                      "STEP_INTENT_FIELDS")
            if kind == "step_result":
                _need(set(event) == {"kind", "observation", "reward",
                                     "terminal", "truncated"} and
                      type(event["observation"]) is str and
                      event["observation"] in OBSERVATIONS and
                      type(event["reward"]) is int and
                      event["reward"] in (-3, 0, 10) and
                      type(event["terminal"]) is bool and
                      type(event["truncated"]) is bool and
                      not (event["terminal"] and event["truncated"]),
                      "STEP_PUBLIC_FIELDS")
                step_index = sum(x["kind"] == "step_intent" for x in events)
                # This external journal does not infer a task terminal.
                _need(step_index <= events[0]["max_steps"],
                      "SOURCE_BUDGET_EXCEEDED")
            if kind == "checkpoint_intent":
                _need(previous_kind == "step_result" and
                      (events[-1]["terminal"] or events[-1]["truncated"]) and
                      set(event) == {"kind", "sha256"} and
                      type(event["sha256"]) is str and
                      re.fullmatch("[0-9a-f]{64}", event["sha256"]),
                      "CHECKPOINT_INTENT_FIELDS")
            if kind == "checkpoint_result":
                _need(set(event) == {"kind", "sha256"} and
                      event["sha256"] == events[-1]["sha256"],
                      "CHECKPOINT_RESULT_FIELDS")
            if previous_kind == "step_result" and kind == "step_intent":
                _need(not (events[-1]["terminal"] or events[-1]["truncated"]),
                      "ACTION_AFTER_SOURCE_END")
        events.append(event)
        prev = record["digest"]
        previous_kind = kind
    status = "COMMITTED" if previous_kind == "checkpoint_result" else "QUARANTINE"
    if status == "COMMITTED":
        check = _read_checked(root / "learned-checkpoint.bin", 65536)
        _need(hashlib.sha256(check).hexdigest() == events[-1]["sha256"],
              "CHECKPOINT_INTEGRITY")
    return {"status": status, "head": prev, "event_count": len(events),
            "source_sha256": events[0]["source_sha256"],
            "episode": events[0]["episode"],
            "steps": sum(x["kind"] == "step_result" for x in events),
            "checkpoint_verified": status == "COMMITTED"}


class JournaledPublicSourceDev:
    """One fresh public source episode; no automatic replay on re-instantiation."""

    def __init__(self, directory, source, *, episode_id, source_sha256,
                 max_steps, role):
        _need(type(episode_id) is str and
              re.fullmatch("[a-zA-Z0-9_-]{1,60}", episode_id),
              "EPISODE_ID")
        _need(type(source_sha256) is str and
              re.fullmatch("[0-9a-f]{64}", source_sha256), "SOURCE_SHA")
        _need(type(max_steps) is int and 1 <= max_steps <= MAX_STEPS,
              "SOURCE_STEP_BUDGET")
        _need(role == "OWNER_PUBLIC_FIT_DEVELOPMENT_ONLY",
              "NO_PUBLIC_FIT_OWNER_ROLE")
        _need(callable(getattr(source, "reset_public", None)) and
              callable(getattr(source, "step_public", None)),
              "SOURCE_METHODS")
        root = Path(directory)
        _need(not root.is_symlink(), "SYMLINK_DIRECTORY")
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        _need(root.is_dir() and not root.is_symlink(), "INVALID_DIRECTORY")
        name = root / "public-events.jsonl"
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     getattr(os, "O_NOFOLLOW", 0), 0o600)
        self.directory = root
        self.source = source
        self.fd = fd
        self.blocked = False
        self.state = "header"
        self.steps = 0
        self.ended = False
        self.seq = 0
        self.prev = ZERO
        self.max_steps = max_steps
        try:
            self._record({"kind": "header", "schema": SCHEMA,
                          "source_sha256": source_sha256, "episode": episode_id,
                          "max_steps": max_steps, "role": role})
        except Exception:
            self.blocked = True
            os.close(fd)
            self.fd = None
            raise

    def _record(self, event):
        _need(not self.blocked and self.fd is not None, "SESSION_QUARANTINED")
        body = {"seq": self.seq, "prev": self.prev, "event": event}
        entry = dict(body, digest=_hash(body))
        try:
            _append(self.fd, entry)
        except Exception:
            self.blocked = True
            raise
        self.prev = entry["digest"]
        self.seq += 1
        self.state = event["kind"]

    def reset_public(self):
        _need(not self.blocked and self.state == "header", "RESET_NOT_ELIGIBLE")
        self._record({"kind": "reset_intent"})
        self.blocked = True
        observation = self.source.reset_public()
        _need(type(observation) is str and observation in OBSERVATIONS,
              "INVALID_SOURCE_OBSERVATION")
        self.blocked = False
        self._record({"kind": "reset_result", "observation": observation})
        return observation

    def step_public(self, action):
        _need(not self.blocked and
              self.state in ("reset_result", "step_result") and
              self.steps < self.max_steps and not self.ended and
              type(action) is str and action in ACTIONS,
              "STEP_NOT_ELIGIBLE")
        self._record({"kind": "step_intent", "action": action,
                      "index": self.steps})
        self.blocked = True
        outcome = self.source.step_public(action)
        _need(type(outcome) is tuple and len(outcome) in (3, 4),
              "SOURCE_OUTCOME_SHAPE")
        public, reward, terminal = outcome[:3]
        truncated = outcome[3] if len(outcome) == 4 else False
        _need(type(public) is str and public in OBSERVATIONS and
              type(reward) is int and reward in (-3, 0, 10) and
              type(terminal) is bool and type(truncated) is bool and
              not (terminal and truncated),
              "SOURCE_OUTCOME_PUBLIC_FIELDS")
        # A bounded continuing benchmark MUST explicitly declare its end.
        # Expiration without terminal/truncated is not a checkpoint boundary.
        self.steps += 1
        self.ended = terminal or truncated
        self.blocked = False
        self._record({"kind": "step_result", "observation": public,
                      "reward": reward, "terminal": terminal,
                      "truncated": truncated})
        return (public, reward, terminal, truncated)

    def commit_checkpoint(self, payload):
        _need(not self.blocked and self.state == "step_result",
              "CHECKPOINT_NOT_ELIGIBLE")
        cold = inspect_custody(self.directory)
        _need(cold["status"] == "QUARANTINE", "CHECKPOINT_ALREADY_COMMITTED")
        # Require an AUTHENTIC source terminal or truthful owner truncation.
        last = json.loads(_read_checked(
            self.directory / "public-events.jsonl", MAX_JOURNAL_BYTES
        ).splitlines()[-1])["event"]
        _need(last["terminal"] or last["truncated"], "SOURCE_NOT_FINISHED")
        _need(type(payload) is bytes and 0 < len(payload) <= 65536,
              "CHECKPOINT_SIZE")
        expected = hashlib.sha256(payload).hexdigest()
        self._record({"kind": "checkpoint_intent", "sha256": expected})
        self.blocked = True
        observed = _atomic_checkpoint(self.directory, payload)
        _need(observed == expected, "CHECKPOINT_HASH_MISMATCH")
        self.blocked = False
        self._record({"kind": "checkpoint_result", "sha256": expected})
        receipt = inspect_custody(self.directory)
        _need(receipt["status"] == "COMMITTED", "POST_COMMIT_VERIFICATION")
        return receipt

    def execute_one(self, session):
        """Run one finite model-owned episode. No original source permission."""
        _need(session.max_steps >= self.max_steps, "SESSION_SHORTER_THAN_OWNER")
        try:
            result = session.run_episode(self)
            receipt = self.commit_checkpoint(result["checkpoint"])
            return {**{k: v for k, v in result.items() if k != "checkpoint"},
                    "custody": receipt}
        except BaseException:
            self.blocked = True
            raise

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

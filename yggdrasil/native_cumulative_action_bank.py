"""NKR-12 opt-in bounded native memory for already learned public intervention laws.

This is a storage and cold-retrieval adapter for the existing NKR-11 native
learner, not an additional causal fitter, a task-ID discoverer, or accepted
Yggdrasil runtime behavior. The caller supplies the 7-active/9-retained
address and actual source-pinned public action outcomes. No hidden source
oracle, evaluation labels, tokens, gradients or frontier model are used.

All construction and updates are immutable and return a NEW bank.
"""
from __future__ import annotations

import hashlib
import json
import re

from yggdrasil.public_causal_cells import PublicCausalCells
from yggdrasil.native_intervention_repair import (
    NativeInterventionRepair, canonical, digest,
)

SCHEMA = "yggdrasil.nkr12.cumulative-native-bank.v1"
MAX_SLOTS = 16
MAX_CHECKPOINT_BYTES = 262144


def _slot(address, retained):
    # The approved native address space is 7 active + 9 retained.
    return PublicCausalCells._address(address, retained)


def _check_member(model):
    if not isinstance(model, NativeInterventionRepair):
        raise ValueError("NKR12_NATIVE_MEMBER_REQUIRED")
    raw = model.checkpoint()
    if len(raw) > 65536 or digest(raw) != model.checkpoint_sha256:
        raise ValueError("NKR12_MEMBER_CUSTODY_MISMATCH")
    try:
        doc = json.loads(raw.decode("ascii"))
    except (ValueError, UnicodeError) as exc:
        raise ValueError("NKR12_MEMBER_INVALID") from exc
    if (type(doc) is not dict or doc.get("scientific_pass") is not False
            or doc.get("accepted_native") is not False
            or doc.get("source_mode") != "engineering_fixture_only"):
        raise ValueError("NKR12_MEMBER_UNQUALIFIED")
    sources = [doc["warm_id"]]
    if doc["repair_id"] is not None:
        sources.append(doc["repair_id"])
    refs = [row[0] for row in (doc["warm_records"] + doc["repair_records"])]
    return raw, tuple(sources), tuple(refs)


class NativeCumulativeActionBank:
    """16 native slots retaining immutable NKR-11 causal checkpoints.

    The explicit slot is *not* a learned identity or a task-retrieval claim.
    Sources and observation refs are globally non-rebindable between slots.
    """

    __slots__ = ("_members", "_raw", "_sha")

    def __init__(self, members=None):
        values = {} if members is None else dict(members)
        if len(values) > MAX_SLOTS:
            raise ValueError("NKR12_SLOT_CAPACITY")
        seen_sources, seen_refs = set(), set()
        records = []
        for slot, model in sorted(values.items()):
            if type(slot) is not int or not 0 <= slot < MAX_SLOTS:
                raise ValueError("NKR12_ADDRESS_INVALID")
            raw, sources, refs = _check_member(model)
            if seen_sources.intersection(sources) or seen_refs.intersection(refs):
                raise ValueError("NKR12_GLOBAL_SOURCE_OR_EVIDENCE_REBOUND")
            if len(set(sources)) != len(sources) or len(set(refs)) != len(refs):
                raise ValueError("NKR12_MEMBER_SOURCE_REBOUND")
            seen_sources.update(sources)
            seen_refs.update(refs)
            records.append([slot, model.checkpoint_sha256, raw.decode("ascii")])
        data = {
            "schema": SCHEMA,
            "slots": records,
            "scientific_pass": False,
            "native_accepted": False,
            "mode": "engineering_fixture_only",
        }
        packed = canonical(data)
        envelope = canonical({"data": data, "sha256": digest(packed)})
        if len(envelope) > MAX_CHECKPOINT_BYTES:
            raise ValueError("NKR12_CHECKPOINT_CAPACITY_EXCEEDED")
        self._members = values
        self._raw = envelope
        self._sha = digest(envelope)

    @property
    def checkpoint_sha256(self):
        return self._sha

    @property
    def checkpoint_bytes(self):
        return len(self._raw)

    @property
    def stored_slots(self):
        return tuple(sorted(self._members))

    def checkpoint(self):
        return self._raw

    @classmethod
    def restore(cls, raw, expected_sha256):
        if (type(raw) is not bytes or len(raw) > MAX_CHECKPOINT_BYTES
                or type(expected_sha256) is not str
                or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None
                or digest(raw) != expected_sha256):
            raise ValueError("NKR12_CHECKPOINT_SHA_OR_SIZE_INVALID")
        try:
            obj = json.loads(raw.decode("ascii"))
            if type(obj) is not dict or set(obj) != {"data", "sha256"}:
                raise ValueError("envelope")
            data = obj["data"]
            if (type(data) is not dict
                    or set(data) != {"schema", "slots", "scientific_pass",
                                    "native_accepted", "mode"}
                    or data["schema"] != SCHEMA
                    or data["scientific_pass"] is not False
                    or data["native_accepted"] is not False
                    or data["mode"] != "engineering_fixture_only"
                    or digest(canonical(data)) != obj["sha256"]
                    or canonical(obj) != raw
                    or type(data["slots"]) is not list
                    or len(data["slots"]) > MAX_SLOTS):
                raise ValueError("schema")
            members = {}
            last = -1
            for item in data["slots"]:
                if type(item) is not list or len(item) != 3:
                    raise ValueError("slot")
                slot, sha, serialized = item
                if (type(slot) is not int or slot <= last or slot >= MAX_SLOTS
                        or type(serialized) is not str):
                    raise ValueError("slot order")
                last = slot
                raw_member = serialized.encode("ascii")
                members[slot] = NativeInterventionRepair(raw_member, sha)
            fresh = cls(members)
            if fresh.checkpoint() != raw:
                raise ValueError("noncanonical restoration")
            return fresh
        except (TypeError, KeyError, IndexError, ValueError, UnicodeError,
                OverflowError) as exc:
            raise ValueError("NKR12_CHECKPOINT_REJECTED") from exc

    def _model(self, address, retained):
        return self._members.get(_slot(address, retained))

    def prior(self, address, context, action, *, retained=False):
        member = self._model(address, retained)
        return None if member is None else member.prior(context, action)

    def predict(self, address, context, action, *, retained=False):
        member = self._model(address, retained)
        if member is None:
            return {
                "classification": "UNKNOWN_ABSTAIN",
                "public_outcome": None,
                "native_accepted": False,
                "scientific_pass": False,
            }
        return member.predict(context, action)

    def install_public(self, address, raw, sha256, *, retained=False):
        slot = _slot(address, retained)
        if slot in self._members:
            raise ValueError("NKR12_SLOT_ALREADY_OCCUPIED_NO_OVERWRITE")
        candidate = NativeInterventionRepair.from_warmup(raw, sha256)
        next_members = dict(self._members)
        next_members[slot] = candidate
        bank = type(self)(next_members)
        return bank, {
            "classification": "NEW_NATIVE_MEMORY_SLOT_STAGED_NOT_ACCEPTED",
            "slot": slot,
            "stored_slots": len(bank._members),
            "checkpoint_sha256": bank.checkpoint_sha256,
            "native_accepted": False,
            "scientific_pass": False,
        }

    def repair_public(self, address, raw, sha256, *, retained=False):
        slot = _slot(address, retained)
        current = self._members.get(slot)
        if current is None:
            raise ValueError("NKR12_UNKNOWN_SLOT_CANNOT_REPAIR")
        candidate, receipt = current.stage_public_interventions(raw, sha256)
        if candidate is current:
            return self, receipt
        next_members = dict(self._members)
        next_members[slot] = candidate
        bank = type(self)(next_members)
        return bank, {
            **receipt,
            "slot": slot,
            "bank_checkpoint_sha256": bank.checkpoint_sha256,
            "native_accepted": False,
            "scientific_pass": False,
        }

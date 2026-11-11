"""WSP17 four-slot numerical synaptic storage, routing and masked writes.

Task keys are supplied context. No learned task discovery or symbolic task
program dictionary. More memory capacity is explicitly paid for, not free.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/"WSP-15"))
from structural import (PlasticNand, LENGTHS, checked_context, context,
                        forward, threshold)

SLOTS = 4
WIDTH = sum(LENGTHS)
MAGIC = b"WSP17"
ARCH = hashlib.sha256(b"WSP17|4x(75NAND+3key+1occupied)|numeric-first-free|v1").hexdigest()


def flattened(rows):
    test = PlasticNand()
    test.rows = rows
    if not test.canonical():
        raise ValueError("WSP17_BAD_PAYLOAD")
    return [v for row in rows for v in row]


def expanded(flat):
    rows, offset = [], 0
    for n in LENGTHS:
        rows.append(flat[offset:offset+n])
        offset += n
    return rows


class SynapticBank:
    def __init__(self):
        self.occupied = [0]*SLOTS
        self.keys = [[0]*3 for _ in range(SLOTS)]
        self.synapses = [[0]*WIDTH for _ in range(SLOTS)]

    def canonical(self):
        if (type(self.occupied) is not list or len(self.occupied) != SLOTS
                or any(type(v) is not int or v not in (0, 1) for v in self.occupied)
                or type(self.keys) is not list or len(self.keys) != SLOTS
                or type(self.synapses) is not list or len(self.synapses) != SLOTS):
            return False
        seen = set()
        for occ, key, flat in zip(self.occupied, self.keys, self.synapses):
            if (type(key) is not list or len(key) != 3
                    or any(type(v) is not int or v not in (0, 1) for v in key)
                    or type(flat) is not list or len(flat) != WIDTH
                    or any(type(v) is not int or v not in (0, 1) for v in flat)):
                return False
            if occ:
                if tuple(key) in seen:
                    return False
                seen.add(tuple(key))
                probe = PlasticNand(); probe.rows = expanded(flat)
                if not probe.canonical():
                    return False
            elif any(key) or any(flat):
                return False
        return True

    def hits(self, key):
        checked_context(key)
        if not self.canonical():
            raise ValueError("WSP17_BAD_BANK")
        return [occ*threshold(-sum(a+b-2*a*b for a, b in zip(key, stored)))
                for occ, stored in zip(self.occupied, self.keys)]

    def write(self, key, rows):
        payload = flattened(rows)
        matches = self.hits(key)
        exists = sum(matches)
        already = 0
        claims = []
        for match, occ in zip(matches, self.occupied):
            claim = match+(1-exists)*(1-occ)*(1-already)
            claims.append(claim)
            already += claim
        # All evidence-dependent slot decisions are numeric gates, not host
        # dictionary lookup, index search or if-based task program selection.
        self.synapses = [[old+claim*(new-old) for old, new in zip(flat, payload)]
                         for claim, flat in zip(claims, self.synapses)]
        self.keys = [[old+claim*(new-old) for old, new in zip(stored, key)]
                     for claim, stored in zip(claims, self.keys)]
        self.occupied = [old+claim*(1-old) for old, claim in zip(self.occupied, claims)]
        return sum(claims)

    def read(self, key):
        matches = self.hits(key)
        present = sum(matches)
        flat = [sum(hit*stored[k] for hit, stored in zip(matches, self.synapses))
                for k in range(WIDTH)]
        return present, expanded(flat)

    def predict(self, key, x):
        checked_context(x)
        present, rows = self.read(key)
        value = forward(rows, x)
        return value if present else None  # external abstention formatting only

    def snapshot(self):
        if not self.canonical():
            raise ValueError("WSP17_BAD_BANK")
        body = json.dumps({"schema": "wsp17.synaptic-bank.v1", "architecture": ARCH,
                           "occupied": self.occupied, "keys": self.keys, "synapses": self.synapses},
                          sort_keys=True, separators=(",", ":")).encode("ascii")
        prefix = MAGIC+len(body).to_bytes(4, "big")+body
        return prefix+hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, raw):
        if (type(raw) is not bytes or not 41 <= len(raw) <= 4096 or raw[:5] != MAGIC
                or int.from_bytes(raw[5:9], "big") != len(raw)-41
                or hashlib.sha256(raw[:-32]).digest() != raw[-32:]):
            raise ValueError("WSP17_CHECKPOINT_REJECTED")
        try:
            d = json.loads(raw[9:-32].decode("ascii"))
            if (type(d) is not dict or set(d) != {"schema", "architecture", "occupied", "keys", "synapses"}
                    or d["schema"] != "wsp17.synaptic-bank.v1" or d["architecture"] != ARCH):
                raise ValueError("schema")
            obj = cls()
            obj.occupied, obj.keys, obj.synapses = d["occupied"], d["keys"], d["synapses"]
            if not obj.canonical() or obj.snapshot() != raw:
                raise ValueError("canonical")
            return obj
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError, OverflowError):
            raise ValueError("WSP17_CHECKPOINT_REJECTED") from None

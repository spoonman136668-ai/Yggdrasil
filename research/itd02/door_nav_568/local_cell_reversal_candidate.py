"""Experimental R7 local-cell reversal adaptation with bounded fast state.

Each cell independently stores two completed public sensory/outcome
correlations and a slowly consolidated history. Confidence is withheld
unless both fresh local correlations agree. No global label buffer, learned
shared weights, hidden regime input, or change-point oracle.
"""
import hashlib
import json
from native_cells_r7 import Colony, LocalCell

class ReversalCell(LocalCell):
    def __init__(self):
        super().__init__()
        self.recent = ()

    def feel(self, public_sensor, public_label):
        super().feel(public_sensor, public_label)
        correlation = (1 if public_sensor else -1) * (1 if public_label else -1)
        self.recent = (self.recent + (correlation,))[-2:]

    def recent_signal(self, sensor):
        if len(self.recent) != 2 or self.recent[0] != self.recent[1]:
            return None
        return self.recent[0] * (1 if sensor else -1)

class ReversalColony(Colony):
    def __init__(self):
        super().__init__()
        self.cells = {ctx: [ReversalCell() for _ in range(4)] for ctx in ("A","B")}

    def predict_public(self, context, sensors):
        self._validate(context, sensors)
        votes = [cell.recent_signal(sensor) for cell, sensor in
                 zip(self.cells[context], sensors)]
        if any(v is None for v in votes):
            return None
        # Local cell votes carry the output; neighbor communication remains
        # a bounded four-cell ring as in R7.
        result = 0.0
        for i, vote in enumerate(votes):
            result += vote + 0.03 * (votes[(i-1)%4] + votes[(i+1)%4])/2
        return result > 0 if result != 0 else None

    def checkpoint(self):
        body = {
            "schema": "ygg.r7.local_reversal.v1",
            "cells": {ctx: [{"fast": c.fast, "slow": c.slow,
                              "updates": c.updates, "recent": list(c.recent)}
                             for c in self.cells[ctx]] for ctx in ("A","B")},
            "feedback_updates": self.feedback_updates,
            "neighbor_messages": self.neighbor_messages,
        }
        payload = json.dumps(body, sort_keys=True, separators=(",",":"),allow_nan=False).encode()
        raw = json.dumps({"payload":body,"sha256":hashlib.sha256(payload).hexdigest()},
                         sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        if len(raw) > 32768:
            raise ValueError("LOCAL_CELL_CHECKPOINT_CAP")
        return raw

    @classmethod
    def restore(cls, blob):
        if type(blob) is not bytes or not 0 < len(blob) <= 32768:
            raise ValueError("CHECKPOINT_INVALID")
        data = json.loads(blob)
        if type(data) is not dict or set(data) != {"payload","sha256"}:
            raise ValueError("CHECKPOINT_FIELDS_INVALID")
        body = data["payload"]
        payload = json.dumps(body,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        if hashlib.sha256(payload).hexdigest() != data["sha256"]:
            raise ValueError("CHECKPOINT_HASH_INVALID")
        if body.get("schema") != "ygg.r7.local_reversal.v1" or set(body["cells"]) != {"A","B"}:
            raise ValueError("CHECKPOINT_SCHEMA_INVALID")
        result = cls()
        for ctx in ("A","B"):
            records = body["cells"][ctx]
            if len(records) != 4:
                raise ValueError("CHECKPOINT_CELL_COUNT_INVALID")
            for cell, rec in zip(result.cells[ctx], records):
                if (set(rec) != {"fast","slow","updates","recent"} or
                    type(rec["fast"]) is not int or not -512 <= rec["fast"] <= 512 or
                    type(rec["updates"]) is not int or rec["updates"] < 0 or
                    type(rec["slow"]) not in (int,float) or
                    type(rec["recent"]) is not list or len(rec["recent"]) > 2 or
                    any(type(v) is not int or v not in (-1,1) for v in rec["recent"])):
                    raise ValueError("CHECKPOINT_CELL_STATE_INVALID")
                cell.fast, cell.slow, cell.updates = rec["fast"],rec["slow"],rec["updates"]
                cell.recent = tuple(rec["recent"])
        result.feedback_updates = body["feedback_updates"]
        result.neighbor_messages = body["neighbor_messages"]
        return result

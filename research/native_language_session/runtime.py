"""Bounded structured-data R7 session. No language or science capability claim."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
from research.native.itd01.r7.native_cells import Colony

SOURCE_BLOB = "4c492a494ac5b25d5e9c49b98185be6a2c966b2f"
SCHEMA = "yggdrasil.native-learned-session.v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_identity():
    path = Path(__file__).resolve().parents[1] / "native/itd01/r7/native_cells.py"
    raw = path.read_bytes()
    if hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() != SOURCE_BLOB:
        raise ValueError("NATIVE_SOURCE_DRIFT")


def decode(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= 65536:
        raise ValueError("SESSION_SIZE_INVALID")
    def unique(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("DUPLICATE_JSON_FIELD")
            out[k] = v
        return out
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))


class NativeSession:
    def __init__(self):
        source_identity()
        self.native = Colony()
        self.sequence = 0
        self.pending = None

    def predict(self, context, sensors):
        if self.pending is not None:
            raise ValueError("FEEDBACK_PENDING")
        # The original method validates public context/sensor shapes.
        prediction = self.native.predict(context, sensors)
        query = {"sequence": self.sequence, "context": context,
                 "sensors": list(sensors),
                 "native_state_sha256": hashlib.sha256(self.native.checkpoint()).hexdigest()}
        query_id = digest(query)
        self.pending = (query_id, context, tuple(sensors))
        return {"query_id": query_id, "prediction": prediction}

    def feedback(self, query_id, public_outcome, delay_steps):
        if self.pending is None or query_id != self.pending[0]:
            raise ValueError("UNSELECTED_OR_REPEATED_FEEDBACK")
        if type(public_outcome) is not bool or type(delay_steps) is not int or delay_steps < 2:
            raise ValueError("COMPLETED_PUBLIC_FEEDBACK_REQUIRED")
        if self.sequence >= 1000000:
            raise ValueError("SESSION_UPDATE_CAP_REACHED")
        _, context, sensors = self.pending
        self.native.learn_completed_public_feedback(context, sensors, public_outcome, delay_steps)
        self.sequence += 1
        self.pending = None

    def checkpoint(self):
        if self.pending is not None:
            raise ValueError("FEEDBACK_PENDING")
        payload = {"schema": SCHEMA, "source_blob": SOURCE_BLOB,
                   "sequence": self.sequence,
                   "native": decode(self.native.checkpoint())}
        return canonical({"payload": payload, "sha256": digest(payload)})

    @classmethod
    def restore(cls, raw):
        doc = decode(raw)
        if type(doc) is not dict or set(doc) != {"payload", "sha256"}:
            raise ValueError("SESSION_FIELDS_INVALID")
        p = doc["payload"]
        if (type(p) is not dict or set(p) != {"schema", "source_blob", "sequence", "native"}
                or p["schema"] != SCHEMA or p["source_blob"] != SOURCE_BLOB
                or doc["sha256"] != digest(p) or type(p["sequence"]) is not int
                or not 0 <= p["sequence"] <= 1000000):
            raise ValueError("SESSION_IDENTITY_OR_INTEGRITY_INVALID")
        native_doc = p["native"]
        if type(native_doc) is not dict or set(native_doc) != {"payload", "sha256"}:
            raise ValueError("NATIVE_ENVELOPE_INVALID")
        body = native_doc["payload"]
        if (type(body) is not dict or set(body) != {
                "schema", "cells", "feedback_updates", "neighbor_messages"}
                or type(body["cells"]) is not dict or set(body["cells"]) != {"A", "B"}
                or type(body["feedback_updates"]) is not int
                or type(body["neighbor_messages"]) is not int
                or body["feedback_updates"] != p["sequence"]
                or body["neighbor_messages"] != 8 * p["sequence"]):
            raise ValueError("NATIVE_COUNTER_IDENTITY_INVALID")
        updates = 0
        for cells in body["cells"].values():
            if type(cells) is not list or len(cells) != 4:
                raise ValueError("NATIVE_CELL_COUNT_INVALID")
            per_context = []
            for cell in cells:
                if (type(cell) is not dict or set(cell) != {"fast", "slow", "updates"}
                        or type(cell["fast"]) is not int or not -512 <= cell["fast"] <= 512
                        or type(cell["updates"]) is not int or not 0 <= cell["updates"] <= p["sequence"]
                        or type(cell["slow"]) not in (int, float)
                        or not math.isfinite(cell["slow"]) or not -512 <= cell["slow"] <= 512):
                    raise ValueError("NATIVE_CELL_STATE_INVALID")
                updates += cell["updates"]
                per_context.append(cell["updates"])
            if len(set(per_context)) != 1:
                raise ValueError("NATIVE_LOCAL_UPDATE_COUNT_INVALID")
        if updates != 4 * p["sequence"]:
            raise ValueError("NATIVE_UPDATE_COUNT_INVALID")
        session = cls()
        session.native = Colony.restore(canonical(native_doc))
        session.sequence = p["sequence"]
        return session


def main():
    import sys
    session = NativeSession()
    restored = False
    while True:
        line = sys.stdin.buffer.readline(65537)
        if not line:
            break
        if len(line) > 65536:
            print("REQUEST_SIZE_OR_STREAM_ERROR", file=sys.stderr)
            return 1
        try:
            request = decode(line)
            if type(request) is not dict or type(request.get("op")) is not str:
                raise ValueError("REQUEST_INVALID")
            op = request["op"]
            fields = {"predict": {"op", "context", "sensors"},
                      "feedback": {"op", "query_id", "public_outcome", "delay_steps"},
                      "checkpoint": {"op"}, "restore": {"op", "checkpoint"}}
            if op not in fields or set(request) != fields[op]:
                raise ValueError("REQUEST_FIELDS_INVALID")
            if op == "predict":
                result = session.predict(request["context"], request["sensors"])
            elif op == "feedback":
                session.feedback(request["query_id"], request["public_outcome"], request["delay_steps"])
                result = {"updates": session.sequence}
            elif op == "checkpoint":
                result = {"checkpoint": decode(session.checkpoint())}
            else:
                if restored or session.sequence or session.pending is not None:
                    raise ValueError("SILENT_STATE_REPLACEMENT_DENIED")
                session = NativeSession.restore(canonical(request["checkpoint"]))
                restored = True
                result = {"restored": True}
            print(canonical({"ok": True, "result": result, "language_capability": False}).decode(), flush=True)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            print(canonical({"ok": False, "error": str(exc), "language_capability": False}).decode(), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())

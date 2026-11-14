"""WSP89 direct-written numerical source-conditioned fact weights.

Externally supplied QIDs/PIDs are grounded by the source collector, not parsed
from natural language. Citation evidence is held in an explicit journal, NOT
pretended to be entirely encoded in numeric weights.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import time

VERIFIED = "wikidata_cc0_verified_snapshot"
DECOY = "simulated_untrusted_decoy"
CORRECTION = "counterfactual_authoritative_correction"
GAINS = {VERIFIED: 1.0, DECOY: 0.1, CORRECTION: 1.0}
SNAPSHOT_SCHEMA = "wsp89.direct-source-backed-weights.v1"
ID_RX = re.compile(r"^Q[1-9][0-9]*$")
PROPERTY_RX = re.compile(r"^P[1-9][0-9]*$")

def canonical(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)

def require_id(value: object, *, property_id: bool = False) -> str:
    if not isinstance(value, str) or not (
        PROPERTY_RX if property_id else ID_RX
    ).fullmatch(value):
        raise ValueError("unsupported Wikidata identifier")
    return value

def require_row(row: dict) -> None:
    if not isinstance(row, dict):
        raise ValueError("claim must be a record")
    require_id(row.get("subject"))
    require_id(row.get("predicate"), property_id=True)
    require_id(row.get("object"))
    if row.get("source_type") not in GAINS:
        raise ValueError("unregistered evidence class")
    if (not isinstance(row.get("source_url"), str) or
        not row["source_url"] or len(row["source_url"]) > 512 or
        not isinstance(row.get("statement_id"), str) or
        not row["statement_id"] or len(row["statement_id"]) > 160):
        raise ValueError("source proof and statement identifier required")
    if row["source_type"] == VERIFIED:
        if not (type(row.get("revision")) is int and row["revision"] > 0 and
                row["source_url"] ==
                "https://www.wikidata.org/wiki/Special:EntityData/" +
                row["subject"] + ".json?revision=" + str(row["revision"]) and
                row["statement_id"].startswith(row["subject"] + "$")):
            raise ValueError("unverified Wikidata source identity")
    else:
        if row.get("revision") is not None or not row["source_url"].startswith("counterfactual:wsp89:"):
            raise ValueError("simulation claims cannot impersonate Wikidata")

def key(subject: str, predicate: str) -> str:
    return require_id(subject) + "/" + require_id(predicate, property_id=True)

class DirectEvidenceWeights:
    def __init__(self) -> None:
        self.weights: dict[str, dict[str, float]] = {}
        self.journal: list[dict] = []
        self.active_by_id: dict[str, int] = {}

    def assert_evidence(self, row: dict) -> None:
        require_row(row)
        if row["statement_id"] in self.active_by_id:
            raise ValueError("duplicate active statement")
        k = key(row["subject"], row["predicate"])
        obj = row["object"]
        self.weights.setdefault(k, {})
        self.weights[k][obj] = self.weights[k].get(obj, 0.0) + GAINS[row["source_type"]]
        self.journal.append({"operation": "assert", "claim": copy.deepcopy(row)})
        self.active_by_id[row["statement_id"]] = len(self.journal) - 1

    def retract_evidence(self, statement_id: str) -> None:
        if statement_id not in self.active_by_id:
            raise ValueError("cannot retract unknown or already retracted source statement")
        idx = self.active_by_id.pop(statement_id)
        row = self.journal[idx]["claim"]
        k = key(row["subject"], row["predicate"])
        obj = row["object"]
        self.weights[k][obj] -= GAINS[row["source_type"]]
        if abs(self.weights[k][obj]) < 1e-8:
            self.weights[k].pop(obj)
        self.journal.append({"operation": "retract", "target_statement_id": statement_id})

    def answer(self, subject: str, predicate: str) -> dict | None:
        k = key(subject, predicate)
        scores = self.weights.get(k, {})
        values = tuple(sorted(obj for obj, weight in scores.items() if weight >= 0.5))
        if not values:
            return None
        claims = []
        for sid, position in sorted(self.active_by_id.items()):
            row = self.journal[position]["claim"]
            if (key(row["subject"], row["predicate"]) == k and
                row["object"] in values and row["source_type"] != DECOY):
                claims.append({
                    "value": row["object"], "source_url": row["source_url"],
                    "statement_id": row["statement_id"],
                    "source_type": row["source_type"],
                    "revision": row.get("revision"),
                })
        return {"values": values, "citations": tuple(sorted(claims,
            key=lambda r: (r["value"], r["statement_id"])))}

    def snapshot(self) -> str:
        payload = {"weights": self.weights, "journal": self.journal}
        raw = canonical(payload)
        return canonical({"schema": SNAPSHOT_SCHEMA, "payload": payload,
                          "sha256": hashlib.sha256(raw.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls, snapshot: str) -> "DirectEvidenceWeights":
        envelope = json.loads(snapshot)
        if envelope.get("schema") != SNAPSHOT_SCHEMA:
            raise ValueError("unknown snapshot schema")
        payload = envelope.get("payload")
        if (not isinstance(payload, dict) or
            hashlib.sha256(canonical(payload).encode("ascii")).hexdigest()
            != envelope.get("sha256")):
            raise ValueError("snapshot checksum invalid")
        restored = cls()
        for event in payload["journal"]:
            if event["operation"] == "assert":
                restored.assert_evidence(event["claim"])
            elif event["operation"] == "retract":
                restored.retract_evidence(event["target_statement_id"])
            else:
                raise ValueError("unknown evidence event")
        if restored.weights != payload["weights"]:
            raise ValueError("snapshot numerical weights disagree with journal")
        return restored

    def numeric_weight_slots(self) -> int:
        return sum(len(row) for row in self.weights.values())

    def evidence_count(self) -> int:
        return len(self.journal)


class SymbolicEvidenceControl:
    """Independent event-sourced symbolic control: no numerical weights."""
    def __init__(self) -> None:
        self.active: dict[str, dict] = {}

    def assert_evidence(self, row: dict) -> None:
        require_row(row)
        if row["statement_id"] in self.active:
            raise ValueError("duplicate statement")
        self.active[row["statement_id"]] = dict(row)

    def retract_evidence(self, statement_id: str) -> None:
        if statement_id not in self.active:
            raise ValueError("missing statement")
        del self.active[statement_id]

    def answer(self, subject: str, predicate: str) -> dict | None:
        require_id(subject)
        require_id(predicate, property_id=True)
        selected = sorted(
            (r for r in self.active.values()
             if r["subject"] == subject and r["predicate"] == predicate
             and r["source_type"] != DECOY),
            key=lambda r: (r["object"], r["statement_id"])
        )
        if not selected:
            return None
        return {
            "values": tuple(sorted({r["object"] for r in selected})),
            "citations": tuple({
                "value": r["object"], "source_url": r["source_url"],
                "statement_id": r["statement_id"], "source_type": r["source_type"],
                "revision": r.get("revision")
            } for r in selected)
        }


class FullyTrainedSigmoidControl:
    """Conventional supervised one-hot multi-label sigmoid head; no citation ledger.

    It receives exactly the same resolved authoritative source observations,
    including simulated corrections, and trains all key/object logits to fit.
    This is a non-generative lookup-level neural comparator, not an LLM.
    """
    def __init__(self) -> None:
        self.params: dict[str, dict[str, float]] = {}
        self.targets: dict[str, set[str]] = {}
        self.epochs = 500
        self.rate = 2.0
        self.training_accuracy = 0.0
        self.mean_bce = float("inf")

    def fit(self, rows: list[dict]) -> None:
        truth: dict[str, set[str]] = {}
        objects = set()
        for row in rows:
            require_row(row)
            if row["source_type"] == DECOY:
                continue
            k = key(row["subject"], row["predicate"])
            truth.setdefault(k, set()).add(row["object"])
            objects.add(row["object"])
        if not truth or not objects:
            raise ValueError("conventional control needs verified observed claims")
        universe = sorted(objects)
        self.params = {k: {obj: 0.0 for obj in universe} for k in truth}
        self.targets = truth
        for _ in range(self.epochs):
            for k, weights in self.params.items():
                expected = truth[k]
                for obj in universe:
                    w = weights[obj]
                    probability = 1.0 / (1.0 + math.exp(-w))
                    y = float(obj in expected)
                    weights[obj] = w + self.rate * (y - probability)
        scored = 0
        correct = 0
        loss = 0.0
        for k, weights in self.params.items():
            for obj, w in weights.items():
                y = float(obj in truth[k])
                probability = 1.0 / (1.0 + math.exp(-w))
                correct += (probability >= 0.5) == bool(y)
                scored += 1
                loss -= y * math.log(max(probability, 1e-15))
                loss -= (1 - y) * math.log(max(1 - probability, 1e-15))
        self.training_accuracy = correct / scored
        self.mean_bce = loss / scored

    def answer(self, subject: str, predicate: str) -> tuple[str, ...] | None:
        k = key(subject, predicate)
        if k not in self.params:
            return None
        result = tuple(sorted(x for x, w in self.params[k].items() if w > 0))
        return result if result else None

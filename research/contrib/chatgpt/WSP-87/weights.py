"""Directly written numerical relational weights; no text tokens or gradient steps."""
from __future__ import annotations

import hashlib
import json
import unicodedata


def identity(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("grounded identifier required")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized.encode("utf-8")) > 256:
        raise ValueError("invalid grounded identifier size")
    return normalized


class NumericKnowledge:
    """Store observed edges as executable real-valued matrix weights.

    Identity binding is an externally grounded interface, not word learning.
    A length-two inference is the numeric product of two learned edge matrices.
    """

    def __init__(self):
        self.entities: list[str] = []
        self.relations: list[str] = []
        self._ids: dict[str, int] = {}
        self.weights: dict[str, list[list[float]]] = {}

    def _entity(self, value: str) -> int:
        value = identity(value)
        if value not in self._ids:
            i = len(self.entities)
            self.entities.append(value)
            self._ids[value] = i
            for matrix in self.weights.values():
                for row in matrix:
                    row.append(0.0)
                matrix.append([0.0] * (i + 1))
        return self._ids[value]

    def observe(self, relation: str, source: str, target: str, present: bool = True):
        relation, source, target = identity(relation), identity(source), identity(target)
        if not isinstance(present, bool):
            raise ValueError("present must be boolean")
        if not present and (relation not in self.weights or
                            source not in self._ids or target not in self._ids):
            raise ValueError("cannot retract an ungrounded fact")
        a, b = self._entity(source), self._entity(target)
        if relation not in self.weights:
            self.relations.append(relation)
            self.weights[relation] = [[0.0] * len(self.entities)
                                      for _ in self.entities]
        self.weights[relation][a][b] = 1.0 if present else 0.0

    def predict(self, relation: str, source: str, target: str, hops: int) -> bool | None:
        relation, source, target = identity(relation), identity(source), identity(target)
        if hops not in (1, 2):
            raise ValueError("only exact one- or two-hop queries are defined")
        if (relation not in self.weights or source not in self._ids or
                target not in self._ids):
            return None
        i, j = self._ids[source], self._ids[target]
        m = self.weights[relation]
        strength = (m[i][j] if hops == 1 else
                    sum(m[i][k] * m[k][j] for k in range(len(self.entities))))
        return strength >= 0.5

    def snapshot(self) -> str:
        payload = {"entities": self.entities, "relations": self.relations,
                   "weights": self.weights}
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        digest = hashlib.sha256(raw.encode("ascii")).hexdigest()
        return json.dumps({"schema": "wsp87.numeric-knowledge-snapshot.v1",
                           "sha256": digest, "payload": payload},
                          sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    @classmethod
    def restore(cls, document: str) -> "NumericKnowledge":
        envelope = json.loads(document)
        if envelope.get("schema") != "wsp87.numeric-knowledge-snapshot.v1":
            raise ValueError("unknown weight snapshot schema")
        payload = envelope["payload"]
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        if hashlib.sha256(raw.encode("ascii")).hexdigest() != envelope.get("sha256"):
            raise ValueError("weight snapshot checksum mismatch")
        entities = payload["entities"]
        relations = payload["relations"]
        weights = payload["weights"]
        if (not isinstance(entities, list) or not isinstance(relations, list)
                or len(entities) != len(set(entities))
                or len(relations) != len(set(relations))
                or set(weights) != set(relations)):
            raise ValueError("invalid weight schema")
        if any(identity(e) != e for e in entities + relations):
            raise ValueError("invalid canonical identifier")
        n = len(entities)
        for relation in relations:
            matrix = weights[relation]
            if (len(matrix) != n or any(len(row) != n for row in matrix)
                    or any(type(value) is not float or value not in (0.0, 1.0)
                           for row in matrix for value in row)):
                raise ValueError("malformed numeric weights")
        restored = cls()
        restored.entities = list(entities)
        restored.relations = list(relations)
        restored._ids = {e: i for i, e in enumerate(entities)}
        restored.weights = {r: [list(row) for row in weights[r]] for r in relations}
        return restored

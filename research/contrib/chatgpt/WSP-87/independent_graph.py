"""Independent symbolic graph control: no import of numeric learner or world."""
from __future__ import annotations

import unicodedata


def canonical(name: str) -> str:
    if not isinstance(name, str) or not name:
        raise ValueError("grounded name required")
    value = unicodedata.normalize("NFC", name)
    if len(value.encode("utf-8")) > 256:
        raise ValueError("identifier too long")
    return value


class SymbolicGraph:
    def __init__(self):
        self.entities: set[str] = set()
        self.relations: set[str] = set()
        self.edges: set[tuple[str, str, str]] = set()

    def observe(self, relation: str, source: str, target: str, present: bool = True):
        r, a, b = canonical(relation), canonical(source), canonical(target)
        if not isinstance(present, bool):
            raise ValueError("bad truth value")
        if not present and (r not in self.relations or
                            a not in self.entities or b not in self.entities):
            raise ValueError("unknown fact retraction")
        self.entities.update((a, b))
        self.relations.add(r)
        if present:
            self.edges.add((r, a, b))
        else:
            self.edges.discard((r, a, b))

    def predict(self, relation: str, source: str, target: str, hops: int) -> bool | None:
        r, a, b = canonical(relation), canonical(source), canonical(target)
        if hops not in (1, 2):
            raise ValueError("hop bound")
        if r not in self.relations or a not in self.entities or b not in self.entities:
            return None
        if hops == 1:
            return (r, a, b) in self.edges
        return any((r, a, middle) in self.edges and
                   (r, middle, b) in self.edges for middle in self.entities)

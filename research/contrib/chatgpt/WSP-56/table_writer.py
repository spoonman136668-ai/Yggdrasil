"""WSP56 source-blind, zero-gradient finite-operation table writer.

Learner input is only public (before, acoustic_bits, after, charged_costs).
No generator/source import, prewired physical operator functions, phase labels,
or oracle word roles. A restrictive 4-bit fixed-width segment and finite-state
register prior is charged, rather than presented as universal language learning.
"""
from __future__ import annotations
from itertools import permutations
from hashlib import sha256
import json

ORDERS = tuple(permutations((0, 1, 2)))
MAX_ACTIONS = 60
MAX_SNAPSHOT_BYTES = 1000000


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def validate_state(state):
    if (type(state) is not tuple or len(state) != 8 or
            any(type(x) is not int or x < 0 or x >= 7 for x in state)):
        raise ValueError("invalid public physical state")
    return state


def validate_bits(bits):
    if (type(bits) is not str or len(bits) not in (8, 12) or
            set(bits) - {"0", "1"}):
        raise ValueError("invalid binary acoustic signal")
    return bits


class TableWriter:
    gradient_steps = 0

    def __init__(self):
        self.rows = []
        self.lexical_models = []
        self.nodes = 0
        self.incomplete = False

    def observe(self, row):
        if len(self.rows) >= MAX_ACTIONS:
            raise ValueError("action limit exceeded")
        before = validate_state(row.before)
        after = validate_state(row.after)
        bits = validate_bits(row.acoustic_bits)
        if (type(row.action_cost) is not int or row.action_cost != 1 or
                type(row.reset_cost) is not int or row.reset_cost != 0):
            raise ValueError("incorrect action/reset charge")
        self.rows.append((before, bits, after))
        self._reconstruct()

    @staticmethod
    def _lexical_model(unary_rows, entity_slot):
        """Recover entities and all four operator truth tables without codebook."""
        entities = {}
        operations = {}
        for before, bits, after in unary_rows:
            changed = [i for i in range(8) if before[i] != after[i]]
            if len(changed) != 1:
                return None
            e = changed[0]
            words = (bits[:4], bits[4:])
            eword, oword = words[entity_slot], words[1 - entity_slot]
            if eword in entities and entities[eword] != e:
                return None
            entities[eword] = e
            table = operations.setdefault(oword, {})
            old = table.get(before[e])
            if old is not None and old != after[e]:
                return None
            table[before[e]] = after[e]
        if (len(entities) != 8 or len(set(entities.values())) != 8 or
                len(operations) != 4 or set(entities) & set(operations) or
                any(len(t) != 7 for t in operations.values())):
            return None
        return {
            "entity_slot": entity_slot,
            "entities": entities,
            "operations": {
                w: [table[x] for x in range(7)]
                for w, table in sorted(operations.items())
            }
        }

    def _reconstruct(self):
        self.nodes = 0
        unary = [r for r in self.rows if len(r[1]) == 8]
        if len(unary) < 28:
            self.lexical_models = []
            return
        # No training/action-phase count enters predictions. Presence of 28
        # complete one-step observations is an explicit source-family prior.
        models = []
        for slot in (0, 1):
            self.nodes += len(unary)
            found = self._lexical_model(unary, slot)
            if found is not None:
                models.append(found)
        self.lexical_models = models

    @staticmethod
    def _infer(before, bits, model, grammar):
        if len(bits) != 12:
            return None
        pieces = (bits[:4], bits[4:8], bits[8:12])
        eword, word1, word2 = (pieces[grammar[0]], pieces[grammar[1]],
                               pieces[grammar[2]])
        if (eword not in model["entities"] or
                word1 not in model["operations"] or
                word2 not in model["operations"]):
            return None
        e = model["entities"][eword]
        table1 = model["operations"][word1]
        table2 = model["operations"][word2]
        result = list(before)
        result[e] = table2[table1[before[e]]]
        return tuple(result)

    def _regime_candidates(self, model):
        """Find longest recent evidence-consistent suffix, not a phase marker."""
        pair_rows = [r for r in self.rows if len(r[1]) == 12]
        if len(pair_rows) < 6:
            return ()
        compatible = set(ORDERS)
        suffix = 0
        for before, bits, after in reversed(pair_rows):
            local = {
                order for order in compatible
                if self._infer(before, bits, model, order) == after
            }
            self.nodes += len(compatible)
            if not local:
                break
            compatible = local
            suffix += 1
        if suffix < 6:
            return ()
        return tuple(sorted(compatible))

    def predict(self, before, bits):
        before = validate_state(before)
        bits = validate_bits(bits)
        if len(bits) != 12 or not self.lexical_models or self.incomplete:
            return None
        # Never request an external phase selector; every prediction depends
        # exclusively on what the charged physical history establishes.
        answers = set()
        for model in self.lexical_models:
            allowed = self._regime_candidates(model)
            if not allowed:
                return None
            for grammar in allowed:
                answers.add(self._infer(before, bits, model, grammar))
        return next(iter(answers)) if len(answers) == 1 else None

    def current_grammars(self):
        return [(m["entity_slot"], self._regime_candidates(m))
                for m in self.lexical_models]

    def numeric_weight_count(self):
        return sum(sum(len(table) for table in m["operations"].values())
                   for m in self.lexical_models)

    def snapshot(self):
        payload = {
            "schema": "wsp56.table-writer.v1",
            "rows": [[list(b), raw, list(a)] for b, raw, a in self.rows],
            "models": self.lexical_models,
            "incomplete": self.incomplete,
            "gradient_steps": self.gradient_steps
        }
        body = canonical(payload)
        env = canonical({"payload": payload, "sha256": sha256(body.encode("ascii")).hexdigest()})
        if len(env.encode("ascii")) > MAX_SNAPSHOT_BYTES:
            raise OverflowError("snapshot exceeds ceiling")
        return env

    @classmethod
    def restore(cls, text):
        if type(text) is not str or len(text) > MAX_SNAPSHOT_BYTES:
            raise ValueError("invalid snapshot length")
        try:
            data = json.loads(text)
            if type(data) is not dict or set(data) != {"payload", "sha256"}:
                raise ValueError("invalid envelope")
            payload = data["payload"]
            if (type(payload) is not dict or
                    payload.get("schema") != "wsp56.table-writer.v1" or
                    sha256(canonical(payload).encode("ascii")).hexdigest() != data["sha256"]):
                raise ValueError("invalid hash/schema")
            rows = payload["rows"]
            if type(rows) is not list or len(rows) > MAX_ACTIONS:
                raise ValueError("invalid evidence rows")
            obj = cls()
            for items in rows:
                if type(items) is not list or len(items) != 3:
                    raise ValueError("invalid evidence structure")
                b, bits, a = items
                class Row:
                    pass
                row = Row()
                row.before, row.acoustic_bits, row.after = tuple(b), bits, tuple(a)
                row.action_cost, row.reset_cost = 1, 0
                obj.observe(row)
            if obj.snapshot() != text:
                raise ValueError("noncanonical or inconsistent evidence snapshot")
            return obj
        except (TypeError, KeyError, IndexError, UnicodeError, json.JSONDecodeError) as ex:
            raise ValueError("malformed snapshot") from ex

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii")) * 8

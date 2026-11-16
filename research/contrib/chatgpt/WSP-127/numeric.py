"""Source-blind non-gradient rank-eight numerical causal relation learning.

Generic rank<=8 GF(2) algebra is an explicit supplied prior. Factor masks
and row codes are allocated from actual paid evidence, never source labels.
"""
from __future__ import annotations
from hashlib import sha256
import json

SCHEMA = "wsp127.direct-rank8.v1"

def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

def _hash(value):
    return sha256(_canon(value).encode("utf8")).hexdigest()

def _independent(mask, pivots):
    x = mask
    for bit in sorted(pivots, reverse=True):
        if (x >> bit) & 1:
            x ^= pivots[bit]
    return x

def _pivot_columns(basis):
    # A deterministic independent set of 8 columns of the observed row basis.
    selected = []
    echelon = {}
    for col in range(64):
        signature = sum(((row >> col) & 1) << j
                        for j, row in enumerate(basis))
        residual = _independent(signature, echelon)
        if residual:
            echelon[residual.bit_length() - 1] = residual
            selected.append(col)
        if len(selected) == len(basis):
            break
    return tuple(selected)

class Law:
    def __init__(self, law_id, policy):
        self.id = law_id
        self.policy = policy
        self.events = []
        self.seen = set()
        self.cells = [{} for _ in range(64)]
        self.full = {}
        self.factors = {}
        self.receipt = None
        self.cache = None

    def basis(self):
        return tuple(self.factors[p] for p in sorted(self.factors, reverse=True))

    def rank(self):
        return len(self.factors)

    def columns(self):
        pivots = _pivot_columns(self.basis())
        return pivots + tuple(c for c in range(64) if c not in pivots)[:8-len(pivots)]

    def choose_pair(self):
        n = len(self.events)
        if n >= 1024:
            return None
        if self.policy == "fixed":
            if n < 576:
                return n // 64, n % 64
            if n < 1016:
                return 9 + (n - 576) // 8, self.columns()[(n - 576) % 8]
        else:
            # Complete consecutive rows until eight distinct basis directions
            # have been WITNESSED or another full row cannot fit in budget.
            if self.rank() < 8 and n // 64 < 64:
                full = n // 64
                progress = n % 64
                if progress or 1024 - n >= 64:
                    return full, progress
            if self.rank() == 8:
                pivot_cols = _pivot_columns(self.basis())
                if len(pivot_cols) != 8:
                    raise ValueError("WSP127_PIVOT_RANK_INCONSISTENT")
                for row in range(64):
                    for col in pivot_cols:
                        if col not in self.cells[row]:
                            return row, col
        for row in range(64):
            for col in range(64):
                if col not in self.cells[row]:
                    return row, col
        raise AssertionError("WSP127_ACTION_UNDERBUDGET")

    def ingest(self, event):
        if (type(event) is not list or len(event) != 7 or
                any(type(x) is not int for x in event[:6]) or
                event[1] != self.id or
                not 0 <= event[3] < 64 or not 0 <= event[4] < 64 or
                event[5] not in (0, 1) or
                type(event[6]) is not str or len(event[6]) != 64):
            raise ValueError("WSP127_BAD_EVENT")
        seed, law, subject, a, b, bit, receipt = event
        if (a, b) != self.choose_pair() or (a, b) in self.seen:
            raise ValueError("WSP127_UNFROZEN_ACTION_ORDER")
        self.events.append(event[:])
        self.seen.add((a, b))
        self.cells[a][b] = bit
        if len(self.cells[a]) == 64:
            mask = sum(value << col for col, value in self.cells[a].items())
            self.full[a] = mask
            residual = _independent(mask, self.factors)
            if residual:
                if len(self.factors) >= 8:
                    raise ValueError("WSP127_RANK_EXCEEDS_SUPPLIED_PRIOR")
                self.factors[residual.bit_length() - 1] = residual
        self.cache = None

    def _compile(self):
        predictions = [None] * 64
        for row, value in self.full.items():
            predictions[row] = value
        if self.rank() == 8:
            basis = self.basis()
            all_rows = []
            for code in range(256):
                value = 0
                for j in range(8):
                    if code & (1 << j):
                        value ^= basis[j]
                all_rows.append(value)
            for row in range(64):
                if predictions[row] is not None or not self.cells[row]:
                    continue
                observed = self.cells[row]
                options = [value for value in all_rows
                           if all(((value >> c) & 1) == bit
                                  for c, bit in observed.items())]
                if len(options) == 1:
                    predictions[row] = options[0]
                elif not options:
                    raise ValueError("WSP127_EVIDENCE_OUTSIDE_RANK8")
        self.cache = predictions

    def infer_pair(self, a, b):
        if b in self.cells[a]:
            return self.cells[a][b]
        if self.cache is None:
            self._compile()
        value = self.cache[a]
        return None if value is None else ((value >> b) & 1)

    def payload(self):
        return {"events": self.events, "factors": {str(k): self.factors[k]
                for k in sorted(self.factors)}, "full": {str(k): self.full[k]
                for k in sorted(self.full)}, "policy": self.policy}

class DirectRankEight:
    def __init__(self, policy="adaptive"):
        if policy not in ("adaptive", "fixed"):
            raise ValueError("WSP127_UNKNOWN_POLICY")
        self.policy = policy
        self.states = {}

    def _state(self, law):
        if type(law) is not int or not 0 <= law < 128:
            raise ValueError("WSP127_INVALID_LAW")
        if law not in self.states:
            self.states[law] = Law(law, self.policy)
        return self.states[law]

    def choose(self, view, available):
        if (getattr(view, "cohort", None) != "fit" or
                view.seed != 135000 + view.law_id):
            raise PermissionError("WSP127_ACTIONS_FIT_ONLY")
        pair = self._state(view.law_id).choose_pair()
        if pair is None:
            return None
        subject = view.subject(*pair)
        if subject not in available:
            raise ValueError("WSP127_DUPLICATE_CHOICE")
        return subject

    def observe(self, view, evidence):
        if (getattr(view, "cohort", None) != "fit" or
                getattr(evidence, "seed", None) != view.seed or
                view.seed != 135000 + view.law_id or
                getattr(evidence, "law_id", None) != view.law_id or
                getattr(evidence, "subject", None) not in view.legal or
                view.pair(evidence.subject) !=
                    (getattr(evidence, "left", None), getattr(evidence, "right", None)) or
                type(getattr(evidence, "effect", None)) is not int or
                evidence.effect not in (0, 1) or
                type(getattr(evidence, "receipt", None)) is not str):
            raise ValueError("WSP127_INVALID_SOURCE_CONSEQUENCE")
        self._state(view.law_id).ingest([evidence.seed, evidence.law_id,
            evidence.subject, evidence.left, evidence.right,
            evidence.effect, evidence.receipt])

    def infer(self, view, subject):
        a, b = view.pair(subject)
        return self._state(view.law_id).infer_pair(a, b)

    def snapshot(self):
        body = {"schema": SCHEMA, "policy": self.policy,
                "states": {str(k): self.states[k].payload()
                           for k in sorted(self.states)}}
        return _canon({"payload": body, "sha256": _hash(body)})

    @classmethod
    def restore(cls, snapshot):
        try:
            obj = json.loads(snapshot)
            body = obj["payload"]
            if body["schema"] != SCHEMA or _hash(body) != obj["sha256"]:
                raise ValueError("WSP127_SNAPSHOT_DIGEST_INVALID")
            model = cls(body["policy"])
            for key in sorted(body["states"], key=int):
                if str(int(key)) != key:
                    raise ValueError("WSP127_SNAPSHOT_LAW_KEY")
                state = model._state(int(key))
                expected = body["states"][key]
                if expected["policy"] != model.policy:
                    raise ValueError("WSP127_SNAPSHOT_POLICY")
                for event in expected["events"]:
                    state.ingest(event)
                if state.payload() != expected:
                    raise ValueError("WSP127_SNAPSHOT_FABRICATED_WEIGHTS")
            return model
        except (TypeError, KeyError, IndexError, AttributeError) as exc:
            raise ValueError("WSP127_SNAPSHOT_INVALID") from exc

"""TGAP24: frozen new causal-operator transfer, research-only numeric memory.

Pre-implementation prereg: dfa9034184027d904579705e8ffbb8f630799c1d.
Independent contributor only. Never reads owner source, original hidden worlds,
canonical native learner or protected first-use. No token input.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from pathlib import Path

from tgap21_same_address_dev import TwoSlotMemory, canonical, digest
from write_quarantine_memory_dev import (
    QuarantineWriteMemory, CommonPosteriorReader
)

PREREG = "dfa9034184027d904579705e8ffbb8f630799c1d"
SCHEMA = "yggdrasil.tgap24.unfamiliar-operator-transfer-result.v1"
PROTOCOL = "yggdrasil.tgap24.unfamiliar-operator-transfer-prequential-frozen-dev.v1"
SOURCE = "engineering_fixture_only"
FIT = (10101, "fit", 96)
HELD = (
    (10201, "held_xor"), (10207, "held_xor"), (10211, "held_xor"),
    (10301, "held_and"), (10303, "held_and"), (10313, "held_and"),
    (10401, "held_xnor"), (10409, "held_xnor"), (10427, "held_xnor"),
    (10501, "held_nor"), (10513, "held_nor"), (10529, "held_nor"),
)
OPERATORS = ("fit", "held_xor", "held_and", "held_xnor", "held_nor")
ARMS = ("quarantine_fit", "immediate_fit", "quarantine_no_fit",
        "context_beta_fit", "context_rolling_fit", "pooled_beta_fit",
        "operator_bayesian", "source_only")


def require(cond, code):
    if not cond:
        raise ValueError("YGG_TGAP24_" + code)


def public(t):
    require(type(t) is int and 0 <= t < 96, "STEP")
    return t % 4, (t // 4) % 2


def hidden_best(op, c):
    require(op in OPERATORS and type(c) is int and 0 <= c < 4,
            "OPERATOR")
    x0, x1 = c & 1, (c >> 1) & 1
    return {
        "fit": x0,
        "held_xor": x0 ^ x1,
        "held_and": x0 & x1,
        "held_xnor": 1 ^ x0 ^ x1,
        "held_nor": 1 ^ (x0 | x1),
    }[op]


def witnessed(seed, op, t, c, a):
    require(type(seed) is int and seed >= 0 and
            op in OPERATORS and
            (c, a) == public(t), "PRIVATE_CUSTODY")
    best = hidden_best(op, c)
    coin = int.from_bytes(
        hashlib.sha256(
            f"tgap24:private:noise:v1:{seed}:{op}:{t}".encode("ascii")
        ).digest()[:8], "big") / (1 << 64)
    return int(coin < (.8 if a == best else .2))


class ContextBank:
    """Four independent public-context banks of bounded KNOW23 memory.

    The original numeric memory has no context interface; this is an explicit
    research capacity increase, not an asserted improvement to native Yggdrasil.
    All context/action observations, not hidden operator labels, drive writes.
    """
    def __init__(self, kind, *, with_reader=False):
        require(kind in ("quarantine", "immediate"), "BANK_KIND")
        self.kind = kind
        constructor = (QuarantineWriteMemory if kind == "quarantine"
                       else TwoSlotMemory)
        self.mem = [constructor() for _ in range(4)]
        self.cursor = [0, 0, 0, 0]
        self.global_step = 0
        self.readers = ([CommonPosteriorReader(m) for m in self.mem]
                        if with_reader else [])

    def forecast(self, c, a):
        require(type(c) is int and 0 <= c < 4 and
                type(a) is int and a in (0, 1) and
                self.readers, "FORECAST")
        return self.readers[c].forecast(a)

    def observe(self, t, c, a, y, *, source_mode=SOURCE):
        require(source_mode == SOURCE and
                type(t) is int and t == self.global_step and
                (c, a) == public(t) and
                type(y) is int and y in (0, 1), "REPLAY_OR_SOURCE")
        if self.readers:
            self.readers[c].observe(self.cursor[c], a, y, source_mode=source_mode)
        else:
            self.mem[c].observe(self.cursor[c], a, y, source_mode=source_mode)
        self.cursor[c] += 1
        self.global_step += 1
        require(sum(self.cursor) == self.global_step, "EVENT_ACCOUNTING")

    def finish_fit(self):
        require(self.global_step == 96 and
                self.cursor == [24, 24, 24, 24], "FIT_EVENTS")
        if self.kind == "quarantine":
            for m in self.mem:
                m.finish_episode()
        require(all(not getattr(m, "pending", []) for m in self.mem),
                "UNFLUSHED")

    def public_world_clone(self):
        require(all(not getattr(m, "pending", []) for m in self.mem),
                "UNCLOSED_FIT")
        copybank = copy.deepcopy(self)
        copybank.mem = [m.new_public_world() for m in self.mem]
        copybank.cursor = [0, 0, 0, 0]
        copybank.global_step = 0
        copybank.readers = [CommonPosteriorReader(m) for m in copybank.mem]
        return copybank

    def state_bytes(self):
        """Canonical custody for all four context memory blobs, no weights."""
        return canonical({"schema": "yggdrasil.tgap24.bank.cold.v1",
                          "kind": self.kind,
                          "cursors": self.cursor,
                          "global_step": self.global_step,
                          "contexts": [json.loads(m.checkpoint())
                                       for m in self.mem]})

    @classmethod
    def cold_restore(cls, blob, sha):
        require(type(blob) is bytes and len(blob) <= 65536
                and digest(blob) == sha, "BANK_DIGEST")
        def reject_duplicate(pairs):
            obj = {}
            for key, value in pairs:
                require(key not in obj, "DUPLICATE_KEY")
                obj[key] = value
            return obj
        try:
            v = json.loads(blob, object_pairs_hook=reject_duplicate)
            require(type(v) is dict and set(v) == {
                "schema", "kind", "cursors", "global_step", "contexts"
            } and v["schema"] == "yggdrasil.tgap24.bank.cold.v1"
                    and v["kind"] in ("quarantine", "immediate")
                    and type(v["contexts"]) is list
                    and len(v["contexts"]) == 4
                    and type(v["cursors"]) is list
                    and len(v["cursors"]) == 4
                    and all(type(k) is int and 0 <= k <= 24
                            for k in v["cursors"])
                    and type(v["global_step"]) is int
                    and v["global_step"] == sum(v["cursors"])
                    and 0 <= v["global_step"] <= 96
                    and canonical(v) == blob, "BANK_SCHEMA")
            b = cls(v["kind"])
            cls_m = (QuarantineWriteMemory
                     if v["kind"] == "quarantine" else TwoSlotMemory)
            b.mem = [cls_m.restore(
                canonical(doc), digest(canonical(doc)))
                for doc in v["contexts"]]
            b.cursor = v["cursors"]
            b.global_step = v["global_step"]
            require(all(m.next_step == b.cursor[i]
                        for i, m in enumerate(b.mem))
                    and b.state_bytes() == blob, "BANK_RESTORE")
            return b
        except (KeyError, TypeError, ValueError, UnicodeError) as exc:
            raise ValueError("YGG_TGAP24_BAD_BANK") from exc


class ContextBeta:
    def __init__(self, rolling=False):
        self.rolling = rolling
        self.cells = [[[] for _ in range(2)] for _ in range(4)]

    def predict(self, c, a):
        z = self.cells[c][a]
        return (1 + sum(z)) / (2 + len(z))

    def observe(self, c, a, y):
        self.cells[c][a].append(y)
        if self.rolling:
            self.cells[c][a] = self.cells[c][a][-8:]


class PooledBeta:
    def __init__(self):
        self.events = []
    def predict(self, c, a):
        rows = [y for x, y in self.events if x == a]
        return (1 + sum(rows)) / (2 + len(rows))
    def observe(self, c, a, y):
        self.events.append((a, y))


class BayesianOperator:
    """Strong prior-rich oracle-family comparator; never sees private op."""
    def __init__(self):
        self.logw = [0.0] * len(OPERATORS)

    def predict(self, c, a):
        w = self._weights()
        return sum(p * (.8 if a == hidden_best(op,c) else .2)
                   for p, op in zip(w, OPERATORS))

    def _weights(self):
        largest = max(self.logw)
        expv = [math.exp(v-largest) for v in self.logw]
        normal = sum(expv)
        return [v/normal for v in expv]

    def observe(self, c, a, y):
        for i, op in enumerate(OPERATORS):
            p = .8 if a == hidden_best(op,c) else .2
            self.logw[i] += math.log(p if y else 1-p)


def fit():
    q = ContextBank("quarantine")
    o = ContextBank("immediate")
    beta = ContextBeta()
    rolling = ContextBeta(rolling=True)
    pooled = PooledBeta()
    prior = BayesianOperator()
    for t in range(FIT[2]):
        c, a = public(t)
        y = witnessed(FIT[0], FIT[1], t, c, a)
        q.observe(t, c, a, y)
        o.observe(t, c, a, y)
        beta.observe(c,a,y)
        rolling.observe(c,a,y)
        pooled.observe(c,a,y)
        prior.observe(c,a,y)
    q.finish_fit()
    o.finish_fit()
    qbytes, obytes = q.state_bytes(), o.state_bytes()
    qcold = ContextBank.cold_restore(qbytes,digest(qbytes))
    ocold = ContextBank.cold_restore(obytes,digest(obytes))
    require(qbytes == qcold.state_bytes() and
            obytes == ocold.state_bytes(), "FIT_COLD")
    old = tuple(qcold.mem[c].slot_prediction(s,a)
                for c in range(4) for s in (0,1) for a in (0,1))
    return {"q":qcold,"o":ocold,"beta":beta,"rolling":rolling,
            "pooled":pooled,"bayes":prior,"old_all_slots":old,
            "old_slot0":tuple(qcold.mem[c].slot_prediction(0,a)
                              for c in range(4) for a in (0,1)),
            "fit_qbytes":len(qbytes),"fit_obytes":len(obytes)}


def eval_world(fitted, world):
    require(world in HELD and type(world) is tuple, "HELD_WORLD")
    seed, op = world
    states = {
        "quarantine_fit": fitted["q"].public_world_clone(),
        "immediate_fit": fitted["o"].public_world_clone(),
        "quarantine_no_fit": ContextBank("quarantine").public_world_clone(),
        "context_beta_fit": copy.deepcopy(fitted["beta"]),
        "context_rolling_fit": copy.deepcopy(fitted["rolling"]),
        "pooled_beta_fit": copy.deepcopy(fitted["pooled"]),
        "operator_bayesian": BayesianOperator(), # independent held-class prior
    }
    scores = {k: [] for k in ARMS}
    for t in range(64):
        c,a=public(t)
        y=witnessed(seed,op,t,c,a)
        for name in ARMS:
            if name=="source_only":
                p=.5
            elif name in ("quarantine_fit","immediate_fit","quarantine_no_fit"):
                p=states[name].forecast(c,a)
            else:
                p=states[name].predict(c,a)
            require(type(p) is float and 0<=p<=1
                    and math.isfinite(p), "PROBABILITY")
            if t>=24:
                scores[name].append((p-y)**2)
            if name=="source_only":
                continue
            if name in ("quarantine_fit","immediate_fit","quarantine_no_fit"):
                states[name].observe(t,c,a,y)
            else:
                states[name].observe(c,a,y)
    for name in ("quarantine_fit","immediate_fit","quarantine_no_fit"):
        bank=states[name]
        for k,m in enumerate(bank.mem):
            raw=m.checkpoint()
            cls=type(m)
            require(cls.restore(raw,digest(raw)).checkpoint()==raw,
                    "HELD_COLD")
    old=tuple(states["quarantine_fit"].mem[c].slot_prediction(0,a)
              for c in range(4) for a in (0,1))
    return {
        "loss_sums":{name:sum(row) for name,row in scores.items()},
        "operator":op, "evaluated":len(scores["quarantine_fit"]),
        "old_slot0_drift":sum(x!=y for x,y in zip(old,fitted["old_slot0"])),
        "qbytes":len(states["quarantine_fit"].state_bytes()),
        "internal_delays":sum(m.replayed_internal
                              for m in states["quarantine_fit"].mem),
    }


def proof():
    started=time.monotonic()
    p=json.loads(Path(__file__).with_name("tgap24_protocol.json")
                 .read_text("utf-8"))
    expected=[(seed,op) for op,seeds in
              p["world"]["held"]["seeds_by_operator"].items()
              for seed in seeds]
    require(p["schema"]==PROTOCOL
            and p["world"]["fit"]=={
                "seed":10101,"operator":"fit","steps":96}
            and expected==list(HELD)
            and p["world"]["held"]["worlds"]==12
            and p["world"]["held"]["scored_total"]==480
            and p["world"]["held"]["warmup_total"]==288
            and p["frozen_predicates"]["H1"].endswith(">=0.01000"),
            "FROZEN_PROTOCOL")
    fitted=fit()
    worlds=[eval_world(fitted,w) for w in HELD]
    require(sum(w["evaluated"] for w in worlds)==480,"SCORING_BUDGET")
    overall={name:round(sum(w["loss_sums"][name]
                            for w in worlds)/480,8)
             for name in ARMS}
    by_op={op:{name:round(
        sum(w["loss_sums"][name] for w in worlds if w["operator"]==op)/120,8)
        for name in ARMS} for op in OPERATORS[1:]}
    old_drift={str(op):sum(w["old_slot0_drift"] for w in worlds
                           if w["operator"]==op)
               for op in OPERATORS[1:]}
    prior_margin=round(overall["immediate_fit"]-overall["quarantine_fit"],8)
    beta_margin=round(overall["context_beta_fit"]-overall["quarantine_fit"],8)
    nofit_margin=round(overall["quarantine_no_fit"]-
                       overall["quarantine_fit"],8)
    hs={
        "H1_vs_immediate_at_least_point01":prior_margin>=.01000,
        "H2_vs_contextual_beta":beta_margin>=0,
        "H3_fitted_vs_unfitted_at_least_point01":nofit_margin>=.01000,
        "H4_zero_old_FIT_contextual_drift":
            all(w["old_slot0_drift"]==0 for w in worlds)
    }
    passed=sum(hs.values())
    return {
        "schema":SCHEMA,"prereg_commit":PREREG,
        "mode":SOURCE,"fit_witnessed":96,"held_warmup":288,
        "held_scored":480,"held_worlds":12,
        "held_brier":overall,"held_operator_brier":by_op,
        "old_FIT_context_slot0_drift_by_operator":old_drift,
        "frozen_hypotheses":hs,
        "margins":{"H1":prior_margin,"H2":beta_margin,"H3":nofit_margin},
        "development_verdict":(
            "DEV_TRANSFER_SUPPORTED" if passed==4 else
            "DEV_MIXED_TRANSFER" if passed else "OPERATOR_TRANSFER_NO_GO"),
        "fit_banks_checkpoint_bytes":{"quarantine":fitted["fit_qbytes"],
                                       "immediate":fitted["fit_obytes"]},
        "max_held_q_bank_bytes":max(w["qbytes"] for w in worlds),
        "total_held_internal_delayed_commits":sum(w["internal_delays"] for w in worlds),
        "engineering_gate":"PASS",
        "scientific_gate":"SCIENCE_NO_GO_SYNTHETIC",
        "native_modified":False,"original_first_use":False,
        "deploy":"NONE",
        "isolated_wall_seconds":round(time.monotonic()-started,6)
    }


if __name__=="__main__":
    print("YGG_TGAP24_RECEIPT="+json.dumps(proof(),sort_keys=True))

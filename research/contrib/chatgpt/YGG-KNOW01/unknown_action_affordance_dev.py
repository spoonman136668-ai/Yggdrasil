"""KNOW26: discover anonymous action effects from witnessed consequences.

Preregistered at ba8d9a071a251f3061ac907c4cf5c611726d2221.
Research-only synthetic exact Bayes, NOT accepted native Yggdrasil.
Unknown action mapping is only an evaluator/simulator argument and is never
available to nonprivileged learner constructors, forecasts or observations.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import time
from pathlib import Path

PREREG = "ba8d9a071a251f3061ac907c4cf5c611726d2221"
SCHEMA = "yggdrasil.know26.action-affordance-transfer-result.v1"
PROTO = "yggdrasil.know26.unknown-action-affordance-transfer-frozen-dev.v1"
MODEL_SCHEMA = "yggdrasil.know26.mapping-law-posterior.dev.v1"
MODE = "engineering_fixture_only"
ALL_MAPS = tuple((0,) + m for m in itertools.permutations((1, 2, 4)))
TRUE_MAPS = ((0, 4, 1, 2), (0, 1, 4, 2), (0, 2, 1, 4))
FIT_LAWS = ((13011, "xor02", 36), (13027, "xor12", 36),
            (13049, "and02", 36))
HELD_LAWS = ("parity3", "majority3", "xor01_and2", "xnor01_xor2")
HELD_SEEDS = (13331, 13347)
POLICIES = ("fit_joint_bayes", "no_fit_joint_bayes", "fit_MAP_256",
            "no_fit_MAP_256", "known_mapping_256",
            "known_held_law_family", "context_action_beta",
            "uninformed_p05")
P_TRUE = .85
P_FALSE = .15


def require(ok, code):
    if not ok:
        raise ValueError("YGG_KNOW26_" + code)


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, separators=(",", ":")).encode("ascii")


def digest(v):
    return hashlib.sha256(v).hexdigest()


def context(t):
    require(type(t) is int and 0 <= t < 36, "PUBLIC_STEP")
    return t % 4


def causal_bit(law, c):
    require(type(c) is int and 0 <= c < 8 and
            law in tuple(x[1] for x in FIT_LAWS)+HELD_LAWS,
            "PRIVATE_LAW")
    x0, x1, x2 = c & 1, (c >> 1) & 1, (c >> 2) & 1
    return {
        "xor02": x0 ^ x2,
        "xor12": x1 ^ x2,
        "and02": x0 & x2,
        "parity3": x0 ^ x1 ^ x2,
        "majority3": int(x0 + x1 + x2 >= 2),
        "xor01_and2": (x0 ^ x1) & x2,
        "xnor01_xor2": (1 ^ x0 ^ x1) ^ x2,
    }[law]


def truth_table(law):
    return sum(causal_bit(law, c) << c for c in range(8))


HELD_FAMILY = tuple(truth_table(law) for law in HELD_LAWS)


def frozen_protocol():
    p = json.loads(Path(__file__).with_name("know26_protocol.json")
                   .read_text(encoding="utf-8"))
    require(p["schema"] == PROTO and
            [tuple(x["flip"]) for x in p["mapping_cases"]] ==
            list(TRUE_MAPS) and
            [(x["seed"], x["law"], x["steps"])
             for x in p["fit"]["per_mapping_worlds"]] == list(FIT_LAWS)
            and p["held"]["laws"] == list(HELD_LAWS)
            and p["held"]["seeds"] == list(HELD_SEEDS)
            and p["held"]["worlds"] == 24 and
            p["held"]["steps"] == 32 and
            p["held"]["held_witnesses_per_policy"] == 768 and
            p["held"]["high_evaluator_queries_per_policy"] == 96 and
            p["fixed_tests"]["H2"].endswith("96 held high queries."),
            "FROZEN_PROTOCOL")
    return p


def private_coin(seed, t, map_id):
    require(type(map_id) is int and 0 <= map_id < 3 and
            type(seed) is int and seed in
            {s for s, _, _ in FIT_LAWS} | set(HELD_SEEDS) and
            type(t) is int and 0 <= t < 36, "PRIVATE_NOISE")
    data = f"know26:private:witness:v1:{seed}:{t}:{map_id}".encode("ascii")
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big") / 2**64


def witnessed(seed, law, t, action, map_id):
    require(type(action) is int and action in (0, 1, 2, 3) and
            ((seed, law, 36) in FIT_LAWS or
             (seed in HELD_SEEDS and law in HELD_LAWS)) and
            type(t) is int and 0 <= t < (36 if
            (seed, law, 36) in FIT_LAWS else 32), "FROZEN_SOURCE")
    target = context(t) ^ TRUE_MAPS[map_id][action]
    q = P_TRUE if causal_bit(law, target) else P_FALSE
    return int(private_coin(seed, t, map_id) < q)


def expected_brier(p, q):
    return q * (1 - q) + (p - q) ** 2


class JointHypothesis:
    """Conventional exact Bayes, six action maps × 256 Boolean truth tables."""

    def __init__(self, mapping_prior, *, allowed=None,
                 family="all", length=32):
        require(type(mapping_prior) is list and
                len(mapping_prior) == 6 and
                all(type(z) is float and math.isfinite(z)
                    and 0 <= z <= 1 for z in mapping_prior)
                and abs(sum(mapping_prior) - 1) <= 1e-10,
                "MAPPING_PRIOR")
        require(length in (32, 36) and type(length) is int,
                "LENGTH")
        self.prior = list(mapping_prior)
        self.allowed = tuple(range(6) if allowed is None else allowed)
        require(type(self.allowed) is tuple and self.allowed and
                len(self.allowed) == len(set(self.allowed)) and
                all(type(i) is int and 0 <= i < 6
                    for i in self.allowed) and
                all(self.prior[i] > 0 for i in self.allowed),
                "ALLOWED_MAPS")
        require(family in ("all", "held"), "FAMILY")
        self.family = family
        self.laws = tuple(range(256)) if family == "all" else HELD_FAMILY
        self.length = length
        self.logw = [
            [math.log(self.prior[i]) - math.log(len(self.laws))
             for _ in self.laws] for i in self.allowed
        ]
        self.events = []

    def _unnormalized(self):
        mx = max(max(z) for z in self.logw)
        rows = [[math.exp(x - mx) for x in row]
                for row in self.logw]
        den = sum(sum(row) for row in rows)
        require(den > 0 and math.isfinite(den), "WEIGHT_SUM")
        return rows, den

    def mapping_posterior(self):
        rows, den = self._unnormalized()
        posterior = [0.] * 6
        for k, i in enumerate(self.allowed):
            posterior[i] = sum(rows[k]) / den
        return posterior

    def prob(self, c, a):
        require(type(c) is int and 0 <= c < 8 and
                type(a) is int and a in (0, 1, 2, 3),
                "FORECAST_INPUT")
        rows, den = self._unnormalized()
        yes = 0.
        for k, i in enumerate(self.allowed):
            pos = c ^ ALL_MAPS[i][a]
            yes += sum(w for h, w in zip(self.laws, rows[k])
                       if (h >> pos) & 1)
        return P_FALSE + (P_TRUE-P_FALSE) * yes / den

    def observe(self, t, c, a, y, *, source_mode=MODE):
        require(source_mode == MODE and
                type(t) is int and t == len(self.events) and
                t < self.length and c == context(t) and
                type(a) is int and a in (0, 1, 2, 3) and
                type(y) is int and y in (0, 1),
                "ONE_WITNESS")
        log_yes = math.log(P_TRUE if y else 1-P_TRUE)
        log_no = math.log(P_FALSE if y else 1-P_FALSE)
        for k, i in enumerate(self.allowed):
            pos = c ^ ALL_MAPS[i][a]
            row = self.logw[k]
            for j, h in enumerate(self.laws):
                row[j] += log_yes if (h >> pos) & 1 else log_no
        self.events.append([t, c, a, y])

    def checkpoint(self):
        raw = canonical({
            "schema": MODEL_SCHEMA,
            "source_mode": MODE,
            "mapping_prior": self.prior,
            "allowed_mappings": self.allowed,
            "family": self.family, "length": self.length,
            "events": self.events,
            "accepted_native": False,
            "scientific_gain_verified": False
        })
        require(len(raw) <= 8192, "CHECKPOINT_BYTES")
        return raw

    @classmethod
    def restore(cls, raw, sha):
        require(type(raw) is bytes and 0 < len(raw) <= 8192 and
                type(sha) is str and digest(raw) == sha,
                "CHECKPOINT_SHA")
        def unique(pairs):
            seen = {}
            for k, v in pairs:
                require(k not in seen, "DUPLICATE_KEY")
                seen[k] = v
            return seen
        try:
            data = json.loads(raw.decode("ascii"),
                              object_pairs_hook=unique)
            require(type(data) is dict and set(data) == {
                "schema", "source_mode", "mapping_prior",
                "allowed_mappings", "family", "length", "events",
                "accepted_native", "scientific_gain_verified"} and
                data["schema"] == MODEL_SCHEMA and
                data["source_mode"] == MODE and
                data["accepted_native"] is False and
                data["scientific_gain_verified"] is False and
                type(data["events"]) is list and
                canonical(data) == raw, "CHECKPOINT_CONTRACT")
            m = cls(data["mapping_prior"],
                    allowed=tuple(data["allowed_mappings"]),
                    family=data["family"], length=data["length"])
            for idx, row in enumerate(data["events"]):
                require(type(row) is list and len(row) == 4 and
                        all(type(x) is int for x in row) and
                        row[0] == idx, "CHECKPOINT_EVENTS")
                m.observe(*row)
            require(m.checkpoint() == raw, "REPLAY_BYTES")
            return m
        except (TypeError, KeyError, UnicodeError, ValueError,
                OverflowError) as exc:
            raise ValueError("YGG_KNOW26_CHECKPOINT_REJECTED") from exc


class ContextActionBeta:
    def __init__(self):
        self.counts = [[[0, 0] for _ in range(4)] for _ in range(4)]
        self.events = []

    def prob(self, c, a):
        if c >= 4:
            return .5
        good, n = self.counts[c][a]
        return (good + 1) / (n + 2)

    def observe(self, t, c, a, y, *, source_mode=MODE):
        require(source_mode == MODE and
                type(t) is int and t == len(self.events)
                and t < 32 and c == context(t)
                and type(a) is int and a in (0,1,2,3)
                and type(y) is int and y in (0,1),
                "BETA_WITNESS")
        count = self.counts[c][a]
        count[0] += y
        count[1] += 1
        self.events.append([t,c,a,y])

    def checkpoint(self):
        other = ContextActionBeta()
        for row in self.events:
            other.observe(*row)
        require(other.counts == self.counts and
                other.events == self.events, "BETA_REPLAY")
        return canonical({"counts":self.counts,"events":self.events})


class Passive:
    def __init__(self):
        self.n = 0
    def prob(self, c, a):
        return .5
    def observe(self, t, c, a, y, *, source_mode=MODE):
        require(source_mode == MODE and
                type(t) is int and t == self.n and
                t < 32 and c == context(t) and
                type(a) is int and a in (0,1,2,3) and
                type(y) is int and y in (0,1), "PASSIVE_SOURCE")
        self.n += 1
    def checkpoint(self):
        return canonical({"witnessed":self.n})


def fit_source(map_id):
    require(type(map_id) is int and map_id in (0,1,2),
            "FIT_MAP_FIXTURE")
    previous_prior = [1/6.] * 6
    archived = []
    source_actions = 0
    for seed, law, steps in FIT_LAWS:
        m = JointHypothesis(previous_prior, length=36)
        for t in range(steps):
            a = t % 4
            y = witnessed(seed, law, t, a, map_id)
            m.observe(t, context(t), a, y)
            source_actions += 1
        raw = m.checkpoint()
        cold = JointHypothesis.restore(raw, digest(raw))
        require(raw == cold.checkpoint() and
                m.mapping_posterior() == cold.mapping_posterior() and
                all(m.prob(c, 0) == cold.prob(c, 0)
                    for c in range(8)), "FIT_SOURCE_COLD")
        archived.append({
            "source_sha": digest(raw),
            "readout_high": [m.prob(c,0) for c in range(4,8)],
            "raw": raw,
            "bytes": len(raw)
        })
        previous_prior = m.mapping_posterior()
    require(source_actions == 108, "FIT_BUDGET")
    return previous_prior, archived


def model_for(name, map_prior, *, private_map_id=None):
    require(name in POLICIES and type(map_prior) is list and
            len(map_prior) == 6, "POLICY")
    if name == "fit_joint_bayes":
        return JointHypothesis(map_prior)
    if name == "no_fit_joint_bayes":
        return JointHypothesis([1/6.] * 6)
    if name in ("fit_MAP_256", "no_fit_MAP_256"):
        prior = map_prior if name == "fit_MAP_256" else [1/6.] * 6
        chosen = max(range(6), key=lambda i: (prior[i], -i))
        return JointHypothesis(prior, allowed=(chosen,))
    if name in ("known_mapping_256", "known_held_law_family"):
        # Explicit privileged evaluator reference, never used by fair arms.
        require(type(private_map_id) is int and
                0 <= private_map_id < 3, "PRIVILEGED_MAPPING")
        true_idx = ALL_MAPS.index(TRUE_MAPS[private_map_id])
        onehot = [0.] * 6
        onehot[true_idx] = 1.
        return JointHypothesis(
            onehot, allowed=(true_idx,),
            family="held" if name=="known_held_law_family" else "all")
    if name == "context_action_beta":
        return ContextActionBeta()
    return Passive()


def evaluate_world(name, map_id, seed, law, map_prior):
    require(name in POLICIES and
            type(map_id) is int and 0 <= map_id < 3 and
            type(seed) is int and seed in HELD_SEEDS and
            law in HELD_LAWS, "WORLD")
    private = map_id if name in ("known_mapping_256",
                                 "known_held_law_family") else None
    model = model_for(name, map_prior, private_map_id=private)
    for t in range(32):
        a = t % 4
        y = witnessed(seed, law, t, a, map_id)
        model.observe(t, context(t), a, y)
    raw = model.checkpoint()
    if isinstance(model, JointHypothesis):
        cold = JointHypothesis.restore(raw, digest(raw))
        require(cold.checkpoint() == raw and
                all(cold.prob(c,0) == model.prob(c,0)
                    for c in range(8)), "HELD_COLD")
    high = [model.prob(c,0) for c in range(4,8)]
    low = [model.prob(c,0) for c in range(4)]
    hs = sum(expected_brier(p,P_TRUE if causal_bit(law,c) else P_FALSE)
             for c,p in zip(range(4,8),high))
    ls = sum(expected_brier(p,P_TRUE if causal_bit(law,c) else P_FALSE)
             for c,p in zip(range(4),low))
    return {"high_sum": hs, "low_sum": ls,
            "witnessed_actions": 32,
            "checkpoint_bytes":len(raw),
            "readout_high": high}


def proof():
    began=time.monotonic()
    frozen_protocol()
    fit={}
    for map_id in (0,1,2):
        posterior, archive = fit_source(map_id)
        fit[map_id]=(posterior,archive)
    all_results={}
    for name in POLICIES:
        rows=[]
        for map_id in (0,1,2):
            posterior,archive = fit[map_id]
            for law in HELD_LAWS:
                for seed in HELD_SEEDS:
                    rows.append(evaluate_world(
                        name,map_id,seed,law,posterior))
            # No held update is permitted to modify previous fitted ledger.
            for old in archive:
                cold=JointHypothesis.restore(old["raw"],old["source_sha"])
                require(cold.checkpoint()==old["raw"] and
                        [cold.prob(c,0) for c in range(4,8)] ==
                        old["readout_high"],"FIT_HELD_FIT_RETENTION")
        require(len(rows)==24 and
                sum(row["witnessed_actions"] for row in rows)==768,
                "HELD_ACTION_BUDGET")
        all_results[name]={
            "high_expected_brier":round(
                sum(z["high_sum"] for z in rows)/96,8),
            "low_expected_brier":round(
                sum(z["low_sum"] for z in rows)/96,8),
            "average_checkpoint_bytes":round(
                sum(z["checkpoint_bytes"] for z in rows)/24,2),
        }

    map_evidence={}
    for mid,(posterior,archive) in fit.items():
        true_index=ALL_MAPS.index(TRUE_MAPS[mid])
        chosen=max(range(6),key=lambda i:(posterior[i],-i))
        map_evidence[str(mid)]={
            "true_mapping_id":true_index,
            "most_likely_mapping_id":chosen,
            "correct_mapping_prob":round(posterior[true_index],8),
            "mapping_entropy":round(-sum(p*math.log2(p)
                                         for p in posterior if p>0),8),
            "all_mapping_probs":[round(p,8) for p in posterior],
            "fit_source_sha256":[a["source_sha"] for a in archive],
            "fit_checkpoint_bytes":[a["bytes"] for a in archive],
            "fit_old_readouts_cold_exact":True
        }

    fitB=all_results["fit_joint_bayes"]["high_expected_brier"]
    nofit=all_results["no_fit_joint_bayes"]["high_expected_brier"]
    fmap=all_results["fit_MAP_256"]["high_expected_brier"]
    kmap=all_results["known_mapping_256"]["high_expected_brier"]
    h={
      "H1_fit_mapping_correct_2of3":
          sum(d["correct_mapping_prob"]>.5
              for d in map_evidence.values())>=2,
      "H2_fit_over_no_fit_high_0p01":fitB<=nofit-.01,
      "H3_MAP_within_joint_0p015":fmap<=fitB+.015,
      "H4_MAP_correct_all3":
          all(d["true_mapping_id"]==d["most_likely_mapping_id"]
              for d in map_evidence.values()),
      "H5_vs_privileged_map_0p02":fitB<=kmap+.02
    }
    n=int(h["H1_fit_mapping_correct_2of3"])+int(
        h["H2_fit_over_no_fit_high_0p01"])
    verdict=("DEVELOPMENT_AFFORDANCE_TRANSFER_SUPPORTED" if n==2
             else "DEVELOPMENT_MIXED" if n else
             "DEVELOPMENT_NO_GO")
    return {
      "schema":SCHEMA,"prereg_commit":PREREG,
      "model":"conventional_exact_256_boolean_x_6_permutation_bayes",
      "fit_witnesses_per_mapping":108,
      "fit_mapping_groups":3,
      "held_worlds":24,"held_witnesses_per_policy":768,
      "high_eval_queries_per_policy":96,
      "low_eval_queries_per_policy":96,
      "mapping_fit_evidence":map_evidence,
      "held_policy_scores":all_results,
      "frozen_hypotheses":h,
      "development_verdict":verdict,
      "engineering_gate":"PASS",
      "scientific_gate":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
      "native_model_changed":False,
      "owner_checkpoint_changed":False,
      "protected_original_first_use":False,
      "deployment":"NONE",
      "isolated_cpu_wall_seconds":round(time.monotonic()-began,6)
    }


if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True,indent=2))

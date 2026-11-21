"""KNOW41 pre-first-use engineering evaluator. No original or held source access.

The prospective v2 protocol at 4823bc6807a04f0bd80df98c6d439fe08fc3bd72
corrects the source budget before opening any frozen FIT/HELD consequence.
Each independent arm chooses action and observes ONLY its own consequence
from a *shared* world-step exogenous uniform. The scorer alone sees q.
Only injected synthetic MOCK uniforms are supported here.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from know41_active_identifiability_dev import (
    ChosenActionTable, expected_milli, key, need, protocol,
)
from know41_active_models_dev import (
    ActiveBayesian, ContradictionMemory, HAZARDS, canonical,
)

V3_BLOB = "e05caf3b46209c597c3e14ce0fb259aca2d46d80"
V3_FILE = (Path(__file__).resolve().parents[3] / "roadmap" /
           "YGG_KNOW41_PREPRIMARY_H3_IMPOSSIBILITY_CORRECTION_V3_2026-11-20.json")
V2_BLOB = "8594bc3a32d7826ce8ce0b491b1f1906741bce74"
V2_FILE = (Path(__file__).resolve().parents[3] / "roadmap" /
           "YGG_KNOW41_SOURCE_BUDGET_CORRECTION_V2_2026-11-20.json")
ARMS = ("candidate", "bayesian", "bandit", "lookup", "passive", "random", "no_memory")
PHASES = ("A_first", "B_first", "A_return", "B_second")
BONUSES = (0.0, 0.5, 1.0, 2.0)


def v2():
    p = protocol()
    raw = V2_FILE.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    need(blob == V2_BLOB and p["schema"] ==
         "yggdrasil.know41.active-identifiability-proposal.v1", "V2_DRIFT")
    d = json.loads(raw)
    need(d["schema"] == "yggdrasil.know41.active-causal-synthetic-budget-correction.v2"
         and d["original_source_first_use"] == "NONE"
         and d["replacement_exogenous_source"]["max_total_new_source_uniforms"] == 9216
         and d["source_gate"]["original_causalgym_issue_426"] == "NOT_AUTHORIZED",
         "V2_POLICY")
    return d


def v3():
    v2()
    raw = V3_FILE.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    need(blob == V3_BLOB, "V3_DRIFT")
    p = json.loads(raw)
    need(p["schema"] == "yggdrasil.know41.preprimary-impossibility-correction.v3"
         and p["status"] == "PROSPECTIVE_H3_CORRECTION_BEFORE_ANY_PRIMARY_FIRST_USE"
         and p["no_held_source_first_use"] is True
         and p["prospective_change"]["new_H3_margin"] == .01
         and p["governance"]["synthetic_first_use"] == "NOT_AUTHORIZED_BY_THIS_DOCUMENT"
         and p["governance"]["original_world_issue_426"] == "NOT_AUTHORIZED",
         "V3_POLICY")
    return p


def hidden_world_uniform(*args, **kwargs):
    """Absolute safety fence. A legitimate source-owner actor is NOT installed."""
    raise ValueError("YGG_KNOW41_SOURCE_FIRST_USE_NOT_AUTHORIZED")


def expected_net_regret(graph, c, action, theta):
    """Scorer-only counterfactual expectation. Never samples other-action y."""
    q0 = expected_milli(graph, c, 0, theta) / 1000.0
    q1 = expected_milli(graph, c, 1, theta) / 1000.0
    return max(q0, q1 - .05) - ((q0, q1)[action] - .05 * action)


class GreedyLookup(ChosenActionTable):
    """Simple greedy per-context-action table, no forced action coverage."""
    def choose(self, t, c):
        need(type(t) is int and t == self.received and self.pending is None,
             "GREEDY_ORDER")
        key(c, 0)
        a = int(self.prob(c, 1) - .05 > self.prob(c, 0))
        self.pending = [t, c, a]
        return a


class StatelessPolicy:
    """Conventional passive/random/no-state controls. Observe no persistent y."""
    def __init__(self, kind, seed):
        need(kind in ("passive", "random", "no_memory") and
             type(seed) is int and seed >= 0, "POLICY_KIND")
        self.kind, self.seed = kind, seed
        self.received, self.pending = 0, None

    def choose(self, t, c):
        need(type(t) is int and t == self.received and self.pending is None,
             "POLICY_ORDER")
        key(c, 0)
        if self.kind == "passive":
            a = 0
        elif self.kind == "no_memory":
            a = int(t % 4 == 0)
        else:
            coin = hashlib.sha256(
                f"know41:independent-random-policy:v1:{self.seed}:{t}:{c}".encode()
            ).digest()
            a = int.from_bytes(coin[:8], "big") % 2
        self.pending = [t, c, a]
        return a

    def observe(self, t, c, a, y):
        need(type(y) is int and y in (0, 1) and
             self.pending == [t, c, a], "POLICY_UNWITNESSED")
        self.received += 1
        self.pending = None

    def checkpoint(self):
        return canonical({"kind": self.kind, "seed": self.seed,
                          "received": self.received, "pending": self.pending})

    @classmethod
    def cold(cls, raw):
        from know41_active_models_dev import _json
        d = _json(raw, {"kind", "seed", "received", "pending"})
        need(d["kind"] in ("passive", "random", "no_memory") and
             type(d["seed"]) is int and d["seed"] >= 0 and
             type(d["received"]) is int and 0 <= d["received"] <= 256 and
             d["pending"] is None, "POLICY_COLD")
        m = cls(d["kind"], d["seed"])
        m.received = d["received"]
        return m


def instantiate(arm, fit, seed):
    if arm == "candidate":
        return ContradictionMemory(float(fit["candidate_hazard"]))
    if arm == "bayesian":
        return ActiveBayesian(float(fit["bayesian_hazard"]),
                              float(fit["bayesian_bonus"]))
    if arm == "bandit":
        return ChosenActionTable()
    if arm == "lookup":
        return GreedyLookup()
    need(arm in ("passive", "random", "no_memory"), "UNKNOWN_ARM")
    return StatelessPolicy(arm, seed)


def validate_uniforms(uniforms):
    need(type(uniforms) is list and len(uniforms) == 256, "TAPE_LENGTH")
    need(all(type(u) is float and 0 <= u < 1 for u in uniforms),
         "TAPE_TYPE")


def create_tape(seed, injected_uniform):
    """Exactly 256 externally injected random disturbances per world.

    This does not call the private generator or sample counterfactual action y.
    The injected function must carry a separately audited source custody receipt.
    Unit tests use only ephemeral non-frozen mock seeds.
    """
    need(callable(injected_uniform) and type(seed) is int, "WITNESS")
    p = v2()
    blocked = (p["fit_worlds"]["seeds"] +
               p["held_worlds"]["theta0_seeds"] +
               p["held_worlds"]["theta1_seeds"])
    need(seed not in blocked, "FROZEN_FIRST_USE_DENIED")
    tape = [injected_uniform(seed, t, t % 8) for t in range(256)]
    validate_uniforms(tape)
    return tape


def run_world(seed, tape, fit, fork_theta=0, sham=False, fit_only=False):
    """Seven policy rollouts use one fixed exogenous tape, disjoint model states."""
    validate_uniforms(tape)
    need(type(seed) is int and type(fork_theta) is int and
         fork_theta in (0, 1) and type(sham) is bool and
         type(fit_only) is bool, "WORLD_ARGS")
    arms = {name: instantiate(name, fit, seed) for name in ARMS}
    scores = {phase: {name: [] for name in ARMS} for phase in PHASES}
    rewards = {phase: {name: [] for name in ARMS} for phase in PHASES}
    chosen = {name: 0 for name in ARMS}
    saved = {name: 0 for name in ARMS}
    cold_boundary_checks = 0
    base_bank = None
    a_preserved = True
    b_at128 = None
    b_at192 = None
    for t, u in enumerate(tape):
        c = t % 8
        phase = PHASES[t // 64]
        is_b = t // 64 in (1, 3)
        if sham:
            graph, theta = "CHAIN", 0
        elif fit_only:
            graph, theta = "CHAIN", int(is_b)
        else:
            graph, theta = ("FORK", fork_theta) if is_b else ("CHAIN", 0)
        for name, m in arms.items():
            a = m.choose(t, c)   # Uses public c and previously witnessed y only
            q = expected_milli(graph, c, a, theta) / 1000.0  # scorer/source only
            # Shared exogenous u; chosen-action consequence alone goes to model
            y = int(u < q)
            scores[phase][name].append(expected_net_regret(graph, c, a, theta))
            rewards[phase][name].append(y - .05 * a)
            m.observe(t, c, a, y)
            chosen[name] += a
        if t+1 in (64, 128, 192, 256):
            if t+1 == 64:
                base_bank = canonical(arms["candidate"].a)
            if t+1 >= 128:
                a_preserved &= canonical(arms["candidate"].a) == base_bank
            if t+1 == 128:
                b_at128 = canonical(arms["candidate"].b)
            if t+1 == 192:
                b_at192 = canonical(arms["candidate"].b)
            raw = {name: m.checkpoint() for name, m in arms.items()}
            for name, checkpoint in raw.items():
                if name == "candidate":
                    need(len(checkpoint) < 4096, "CAND_CAP")
                cold_model = type(arms[name]).cold(checkpoint)
                need(type(cold_model) is type(arms[name]), "COLD_POLICY_TYPE")
                need(cold_model.checkpoint() == checkpoint, "COLD_READBACK")
                for c0 in range(8):
                    for a0 in (0, 1):
                        if hasattr(cold_model, "prob"):
                            need(cold_model.prob(c0, a0) ==
                                 arms[name].prob(c0, a0), "COLD_PROB")
                if t + 1 < 256:
                    next_c = (t + 1) % 8
                    original_choice = arms[name].choose(t + 1, next_c)
                    restored_choice = cold_model.choose(t + 1, next_c)
                    need(original_choice == restored_choice, "COLD_ACTION")
                    # Discard both pending probes: only an actual next-step decision
                    # may authorize a consequence; no second simulated observation.
                    cold_model = type(arms[name]).cold(checkpoint)
                arms[name] = cold_model
                cold_boundary_checks += 1
                saved[name] = max(saved[name], len(checkpoint))
    need(all(m.received == 256 and m.pending is None for m in arms.values()),
         "FINAL_COUNTS")
    return {
        "seed": seed, "fork_theta": fork_theta, "fit_only": fit_only,
        "sham": sham,
        "regret": {phase: {k: sum(v) / 64 for k, v in row.items()}
                   for phase, row in scores.items()},
        "realized_reward": {phase: {k: sum(v) / 64 for k, v in row.items()}
                            for phase, row in rewards.items()},
        "action1_counts": chosen,
        "max_checkpoint_bytes": saved,
        "candidate_a_preserved": bool(a_preserved),
        "candidate_b_preserved_on_return": b_at128 == b_at192,
        "candidate_b_writes": arms["candidate"].b_writes,
        "world_unique_exogenous_draws": 256,
        "world_observations_per_arm": 256,
        "cold_boundary_checks": cold_boundary_checks,
    }


def fit_selection(seeds, injected_uniform):
    """FIT-only hyperparameter selection. No held law or seeds are consulted."""
    need(type(seeds) is list and 1 <= len(seeds) <= 12 and
         all(type(s) is int for s in seeds) and len(set(seeds)) == len(seeds),
         "FIT_SEEDS")
    # Same source tape reused for every calibration, no repeat sampling.
    tapes = {seed: create_tape(seed, injected_uniform) for seed in seeds}
    fits = []
    for h in HAZARDS:
        fits.append(("candidate", h, 0.0))
    for h in HAZARDS:
        for bonus in BONUSES:
            fits.append(("bayesian", h, bonus))
    scores = {}
    for kind, h, bonus in fits:
        vals = []
        for seed in seeds:
            m = ContradictionMemory(float(h)) if kind == "candidate" else (
                ActiveBayesian(float(h), float(bonus)))
            scores_by_phase = [0.0] * 4
            for t, u in enumerate(tapes[seed]):
                c = t % 8
                theta = int(t // 64 in (1, 3))
                a = m.choose(t, c)
                q = expected_milli("CHAIN", c, a, theta) / 1000.0
                scores_by_phase[t // 64] += expected_net_regret(
                    "CHAIN", c, a, theta)
                m.observe(t, c, a, int(u < q))
                if t+1 in (64, 128, 192, 256):
                    m = type(m).cold(m.checkpoint())
            vals.append(scores_by_phase[3] / 64)
        scores[(kind, h, bonus)] = sum(vals) / len(vals)
    selected = {}
    for kind in ("candidate", "bayesian"):
        winner = min((k for k in scores if k[0] == kind),
                     key=lambda k: (scores[k], k[1], k[2]))
        if kind == "candidate":
            selected["candidate_hazard"] = winner[1]
        else:
            selected["bayesian_hazard"] = winner[1]
            selected["bayesian_bonus"] = winner[2]
    return {"selected": selected, "fit_scores": [
        {"arm": k[0], "hazard": k[1], "bonus": k[2], "regret": v}
        for k, v in sorted(scores.items())],
        "unique_fit_exogenous_draws": len(seeds) * 256}


def compute_verdict(worlds):
    """Preserves v1 margins; reject spoofed/duplicate world receipts first."""
    need(type(worlds) is list and len(worlds) == 24, "HELD_WORLD_COUNT")
    v3_contract = v3()  # H3 v1 was algebraically impossible; no primary first use
    frozen = v2()["held_worlds"]
    theta0, theta1 = frozen["theta0_seeds"], frozen["theta1_seeds"]
    expected = {s: 0 for s in theta0}
    expected.update({s: 1 for s in theta1})
    need(len(expected) == 24 and len(theta0) == 12 and len(theta1) == 12,
         "HELD_MANIFEST_COLLISION")
    seen = set()
    for w in worlds:
        need(type(w) is dict, "HELD_ROW_TYPE")
        seed, theta = w.get("seed"), w.get("fork_theta")
        need(type(seed) is int and seed in expected and
             type(theta) is int and theta == expected[seed] and
             w.get("sham") is False and w.get("fit_only") is False,
             "HELD_CUSTODY")
        need(seed not in seen, "HELD_DUPLICATE")
        seen.add(seed)
        need(w.get("world_unique_exogenous_draws") == 256 and
             w.get("world_observations_per_arm") == 256 and
             w.get("cold_boundary_checks") == 4 * len(ARMS),
             "HELD_SAMPLE_COUNTS")
        need(type(w.get("action1_counts")) is dict and
             set(w["action1_counts"]) == set(ARMS) and
             all(type(n) is int and 0 <= n <= 256
                 for n in w["action1_counts"].values()),
             "HELD_ACTION_COUNTS")
        need(type(w.get("max_checkpoint_bytes")) is dict and
             set(w["max_checkpoint_bytes"]) == set(ARMS) and
             all(type(n) is int and 0 < n < 4096
                 for n in w["max_checkpoint_bytes"].values()),
             "HELD_CHECKPOINT_CAP")
        for metric, low, high in (("regret", 0.0, 1.0),
                                  ("realized_reward", -0.05, 1.0)):
            m = w.get(metric)
            need(type(m) is dict and set(m) == set(PHASES),
                 "HELD_METRIC_PHASE")
            for row in m.values():
                need(type(row) is dict and set(row) == set(ARMS) and
                     all(type(v) in (int, float) and low - 1e-12 <= v <= high + 1e-12
                         for v in row.values()),
                     "HELD_METRIC_VALUES")
        need(type(w.get("candidate_a_preserved")) is bool and
             type(w.get("candidate_b_preserved_on_return")) is bool and
             type(w.get("candidate_b_writes")) is int and
             0 <= w["candidate_b_writes"] <= 192, "HELD_RETENTION")
    need(seen == set(expected), "HELD_MANIFEST_INCOMPLETE")
    out = {}
    for theta in (0, 1):
        rows = [x for x in worlds if x["fork_theta"] == theta and not x["sham"]]
        need(len(rows) == 12, "HELD_COHORT")
        means = {p: {arm: sum(x["regret"][p][arm] for x in rows) / 12
                     for arm in ARMS} for p in PHASES}
        wins = sum(x["regret"]["B_second"]["candidate"] <
                   min(x["regret"]["B_second"]["bayesian"],
                       x["regret"]["B_second"]["bandit"]) for x in rows)
        out[str(theta)] = {"means": means, "paired_wins_vs_strong": wins}
    H = {}
    H["P0"] = (len(worlds) == 24 and
               sum(x["world_unique_exogenous_draws"] for x in worlds) == 6144 and
               all(x["world_observations_per_arm"] == 256 for x in worlds))
    H["P1"] = (all(expected_milli(g, c, 0, theta) == 350 for g in ("CHAIN", "FORK")
                   for c in range(8) for theta in (0, 1)) and
               sum(expected_milli("FORK", c, 1, 0) !=
                   expected_milli("FORK", c, 1, 1) for c in range(8)) >= 4)
    H["H1"] = all(
        out[str(z)]["means"]["B_second"]["candidate"] <=
        min(out[str(z)]["means"]["B_second"][a] for a in ("bayesian","bandit")) - .02
        and out[str(z)]["paired_wins_vs_strong"] >= 9 for z in (0, 1))
    H["H2"] = all(
        out[str(z)]["means"]["A_return"]["candidate"] <=
        out[str(z)]["means"]["A_return"]["bayesian"] + .02 for z in (0, 1)
    ) and all(x["candidate_a_preserved"] for x in worlds)
    H["H3"] = all(
        out[str(z)]["means"]["B_second"]["candidate"] <=
        min(out[str(z)]["means"]["B_second"][a]
            for a in ("passive","random","no_memory")) -
        v3_contract["prospective_change"]["new_H3_margin"] for z in (0, 1))
    H["H4"] = all(x["max_checkpoint_bytes"]["candidate"] < 4096 for x in worlds)
    return {"cohorts": out, "hypotheses": H,
            "protocol_version": "KNOW41_H3_V3_PREPRIMARY",
            "v1_h3_invalid_by_algebra": True,
            "classification": "DEVELOPMENT_SUPPORTED" if all(H.values())
            else "DEVELOPMENT_NO_GO",
            "scientific_gain_verified": False, "deployment": "NONE"}

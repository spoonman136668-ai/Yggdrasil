"""DG1-SL15: bounded, paid, module-wise causal memory DEV experiment.

Synthetic only. Frozen registration: 54c6a289e2c4b862a026550624d0a6e585cade40.
Never import an evaluator truth value into a learner. No native model mutation.
"""
import hashlib
import json
import random
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "dg1-sl14-20261113"))
import sl14 as p

FREEZE = "54c6a289e2c4b862a026550624d0a6e585cade40"
PARENT = "96a9e8af09cbc758d796005a32ea6bc85e4d229f"
SCHEMA = "ygg.dg1-sl15.module-retrieval.v1"
COHORTS = {
    "ABAB": tuple(range(108001, 108009)),
    "ABAC": tuple(range(108009, 108017)),
    "MIXED": tuple(range(108017, 108025)),
    "STABLE": tuple(range(108025, 108033)),
}
ARMS = (
    "module_active", "module_no_retrieval_on_active",
    "sl14_full_bank_on_active", "independent_bayes_on_active",
    "rolling_window_on_active", "module_passive",
)
PAIRED = ARMS[:5]
AUDITS, COLD = p.AUDITS, p.COLD


class World(p.World):
    """A fresh registered world; inherited physical rules unchanged from SL14."""
    def __init__(self, seed, cohort):
        if cohort not in COHORTS or seed not in COHORTS[cohort]:
            raise ValueError("SL15_UNREGISTERED_WORLD")
        self.seed, self.cohort, self.paid = seed, cohort, 0
        ra = random.Random(seed * 103 + 17)
        rb = random.Random(seed * 103 + 941)
        rc = random.Random(seed * 103 + 1789)
        self.rules_a = tuple(ra.randrange(3) for _ in range(3))
        self.rules_b = tuple(3 + rb.randrange(3) for _ in range(3))
        variants = [g for g in range(6)
                    if g not in (self.rules_a[2], self.rules_b[2])]
        self.rules_c = (self.rules_a[0], self.rules_b[1],
                        variants[rc.randrange(len(variants))])


def new_slot(birth):
    return {
        "err": [0] * 6, "n": 0, "seen": 0,
        "birth": birth, "best": 0, "second": 1,
    }


def new_module():
    return {"slots": [new_slot(1)], "active": 0, "witness": []}


class ModuleDNA:
    """Three separately retrievable causal mechanisms, not whole-context banks."""
    kind = "module-dna"

    def __init__(self, allow_retrieval=True):
        if type(allow_retrieval) is not bool:
            raise ValueError("SL15_BAD_MODE")
        self.allow_retrieval = allow_retrieval
        self.modules = [new_module() for _ in range(3)]
        self.causal_events = 0
        self.transitions = []

    def _bit(self, action, slot, x):
        return p.gate(slot["best"], p.pair(x, action))

    def predict(self, x, action):
        p.check_x(x)
        p.check_action(action)
        m = self.modules[action]
        return self._bit(action, m["slots"][m["active"]], x)

    def choose(self, x, step):
        p.check_x(x)
        if type(step) is not int or not 48 <= step < 96 or step % 5 == 4:
            raise ValueError("SL15_UNCHARGED_ACTION_SELECTION")
        scores = []
        for a, m in enumerate(self.modules):
            s = m["slots"][m["active"]]
            cur = self._bit(a, s, x)
            disagree = sum(
                self._bit(a, other, x) != cur
                for j, other in enumerate(m["slots"])
                if j != m["active"] and other["n"] >= 3
            )
            pr = p.pair(x, a)
            uncertain = p.gate(s["best"], pr) != p.gate(s["second"], pr)
            novel = not (s["seen"] & (1 << pr))
            scores.append(10 * disagree + 2 * int(uncertain) + int(novel))
        return max(range(3), key=lambda a: (scores[a], -((a-step) % 3)))

    def observe(self, x, action, changed):
        p.check_x(x)
        p.check_action(action)
        if type(changed) is not int or changed not in (0, 1):
            raise ValueError("SL15_INVALID_REAL_OUTCOME")
        if self.causal_events >= 77:
            raise ValueError("SL15_PAID_CAUSAL_LIMIT")
        m = self.modules[action]
        pair = p.pair(x, action)
        current = m["slots"][m["active"]]
        miss = int(self._bit(action, current, x) != changed)
        m["witness"].append([pair, changed, miss])
        m["witness"] = m["witness"][-4:]
        win = m["witness"]
        if (len(win) == 4 and len({ev[0] for ev in win}) >= 2
                and sum(ev[2] for ev in win) >= 3):
            active_hits = sum(
                p.gate(current["best"], q) == bit for q, bit, _ in win
            )
            candidates = []
            if self.allow_retrieval:
                for j, archived in enumerate(m["slots"]):
                    if j == m["active"] or archived["n"] < 3:
                        continue
                    hits = sum(p.gate(archived["best"], q) == bit
                               for q, bit, _ in win)
                    if hits >= 3 and hits >= active_hits + 2:
                        candidates.append((hits - active_hits, -j, j))
            target, reused = -1, 0
            if candidates:
                target, reused = max(candidates)[2], 1
            elif len(m["slots"]) < 3:
                target = len(m["slots"])
                m["slots"].append(new_slot(self.causal_events + 1))
            if target >= 0:
                source = m["active"]
                stored_rule = m["slots"][target]["best"]
                m["active"] = target
                self.transitions.append([
                    self.causal_events + 1, action, source,
                    target, reused, stored_rule,
                ])
                m["witness"] = []
        current = m["slots"][m["active"]]
        for g in range(6):
            current["err"][g] += int(p.gate(g, pair) != changed)
        current["n"] += 1
        current["seen"] |= 1 << pair
        top = sorted(range(6), key=lambda g: (current["err"][g], g))
        current["best"], current["second"] = top[:2]
        self.causal_events += 1

    def snapshot(self):
        return p.pack(self.kind, {
            "allow_retrieval": self.allow_retrieval,
            "modules": self.modules,
            "causal_events": self.causal_events,
            "transitions": self.transitions,
        })

    @classmethod
    def restore(cls, raw):
        obj = p.unpack(raw, cls.kind)
        if (type(obj) is not dict or set(obj) != {
            "allow_retrieval", "modules", "causal_events", "transitions"
        } or type(obj["allow_retrieval"]) is not bool or
            type(obj["causal_events"]) is not int or
            not 0 <= obj["causal_events"] <= 77 or
            type(obj["modules"]) is not list or len(obj["modules"]) != 3 or
            type(obj["transitions"]) is not list or
            len(obj["transitions"]) > obj["causal_events"]):
            raise ValueError("SL15_CORRUPT_MODULE_CHECKPOINT")
        total = 0
        for m in obj["modules"]:
            if (type(m) is not dict or set(m) != {"slots","active","witness"}
                or type(m["slots"]) is not list or
                not 1 <= len(m["slots"]) <= 3 or
                type(m["active"]) is not int or
                not 0 <= m["active"] < len(m["slots"]) or
                type(m["witness"]) is not list or len(m["witness"]) > 4):
                raise ValueError("SL15_CORRUPT_MODULE_METADATA")
            for ev in m["witness"]:
                if (type(ev) is not list or len(ev) != 3
                    or any(type(v) is not int for v in ev) or
                    ev[0] not in range(4) or
                    ev[1] not in (0,1) or ev[2] not in (0,1)):
                    raise ValueError("SL15_UNEARNED_WITNESS")
            for slot in m["slots"]:
                if (type(slot) is not dict or set(slot) !=
                    {"err","n","seen","birth","best","second"} or
                    type(slot["n"]) is not int or not 0 <= slot["n"] <= 77 or
                    type(slot["birth"]) is not int or
                    not 1 <= slot["birth"] <= 77 or
                    type(slot["seen"]) is not int or not 0 <= slot["seen"] < 16 or
                    type(slot["best"]) is not int or slot["best"] not in range(6) or
                    type(slot["second"]) is not int or slot["second"] not in range(6)
                    or type(slot["err"]) is not list or
                    len(slot["err"]) != 6 or
                    any(type(v) is not int or not 0 <= v <= slot["n"]
                        for v in slot["err"])):
                    raise ValueError("SL15_CORRUPT_EARNED_RULE")
                top = sorted(range(6), key=lambda g: (slot["err"][g],g))
                if [slot["best"],slot["second"]] != top[:2]:
                    raise ValueError("SL15_CORRUPT_CACHED_RULE")
                total += slot["n"]
        if total != obj["causal_events"]:
            raise ValueError("SL15_UNEARNED_CAUSAL_EVENTS")
        previous = 0
        for t in obj["transitions"]:
            if (type(t) is not list or len(t) != 6 or
                any(type(v) is not int for v in t) or
                t[0] <= previous or t[0] > obj["causal_events"] or
                t[1] not in range(3) or
                not 0 <= t[2] < len(obj["modules"][t[1]]["slots"]) or
                not 0 <= t[3] < len(obj["modules"][t[1]]["slots"]) or
                t[2] == t[3] or t[4] not in (0,1) or
                (t[4] and not obj["allow_retrieval"]) or
                t[5] not in range(6)):
                raise ValueError("SL15_BAD_SWITCH_PROVENANCE")
            previous = t[0]
        out = cls(obj["allow_retrieval"])
        out.modules = obj["modules"]
        out.causal_events = obj["causal_events"]
        out.transitions = obj["transitions"]
        if out.snapshot() != raw:
            raise ValueError("SL15_NONCANONICAL_SNAPSHOT")
        return out


def learner(arm):
    if arm in ("module_active","module_passive"):
        return ModuleDNA()
    if arm == "module_no_retrieval_on_active":
        return ModuleDNA(False)
    if arm == "sl14_full_bank_on_active":
        return p.Fingerprint()
    if arm == "independent_bayes_on_active":
        return p.IndependentBayes()
    if arm == "rolling_window_on_active":
        return p.RollingRule()
    raise ValueError("SL15_UNKNOWN_ARM")


def trial(seed, cohort, arm, policy, replay_plan=None):
    if arm not in ARMS:
        raise ValueError("SL15_UNREGISTERED_ARM")
    if replay_plan is not None and (
        type(replay_plan) is not list or len(replay_plan) != 96
    ):
        raise ValueError("SL15_INVALID_PHYSICAL_REPLAY")
    world, model = World(seed, cohort), learner(arm)
    state = seed % 64
    ledger, actions, causal_steps = [], [], []
    seen_full, seen_local = set(), set()
    audits, snap_sizes = {}, []
    cpu_ns = 0
    for step in range(96):
        if step in COLD:
            data = model.snapshot()
            restored = type(model).restore(data)
            if (data != restored.snapshot() or
                any(model.predict(x,a) != restored.predict(x,a)
                    for x in range(8) for a in range(3))):
                raise AssertionError("SL15_COLD_INFERENCE_NOT_IDENTICAL")
            model = restored
            snap_sizes.append(len(data))
        is_choice = step >= 48 and step % 5 != 4
        t0 = time.perf_counter_ns()
        if is_choice:
            if replay_plan is not None:
                action = replay_plan[step]
            elif policy == "diagnostic" and isinstance(model, ModuleDNA):
                action = model.choose(state & 7, step)
            elif policy == "passive":
                action = step % 3
            else:
                raise ValueError("SL15_ACTION_POLICY_NOT_ADMITTED")
            p.check_action(action)
        else:
            action = None
            if replay_plan is not None and replay_plan[step] is not None:
                raise ValueError("SL15_UNCHARGED_REPLAY")
        cpu_ns += time.perf_counter_ns() - t0
        kind, actual_action, after = world.step(state, step, action)
        if kind == "causal":
            x = state & 7
            changed = int(state != after)
            if after not in (state, state ^ (1 << (3 + actual_action))):
                raise AssertionError("SL15_NONPHYSICAL_CONSEQUENCE")
            t0 = time.perf_counter_ns()
            model.observe(x, actual_action, changed)
            cpu_ns += time.perf_counter_ns() - t0
            seen_full.add((x, actual_action))
            seen_local.add((actual_action, p.pair(x,actual_action)))
            causal_steps.append(step)
        ledger.append([state,kind,actual_action,after])
        actions.append(action)
        state = after
        if step+1 in AUDITS:
            audits[str(step+1)] = p.audit(
                model, world, seen_full, seen_local, step+1
            )
    if world.paid != 96 or model.causal_events != 77 or (
        sum(e[1] == "perturb" for e in ledger) != 19
    ):
        raise AssertionError("SL15_PHYSICAL_BUDGET_DRIFT")
    final = model.snapshot()
    if type(model).restore(final).snapshot() != final:
        raise AssertionError("SL15_FINAL_CHECKPOINT_DRIFT")
    if replay_plan is not None and actions != replay_plan:
        raise AssertionError("SL15_PAID_ACTION_TRACE_DRIFT")
    transitions = []
    if isinstance(model, ModuleDNA):
        for count, a, src, dst, reused, rule in model.transitions:
            birth = model.modules[a]["slots"][dst]["birth"]
            transitions.append({
                "physical_step": causal_steps[count-1],
                "module": a, "from_slot": src, "to_slot": dst,
                "archived_reuse": bool(reused), "stored_gate_at_switch": rule,
                "slot_birth_physical_step": causal_steps[birth-1],
            })
    return {
        "charged_steps": world.paid,
        "causal_observations": model.causal_events,
        "charged_input_perturbations": 19,
        "physical_ledger": ledger,
        "action_plan": actions,
        "trace_first48_sha256": p.digest(ledger[:48]),
        "trace_sha256": p.digest(ledger),
        "snapshot_bytes": snap_sizes,
        "final_snapshot_bytes": len(final),
        "final_snapshot_sha256": hashlib.sha256(final).hexdigest(),
        "transitions": transitions,
        "audits": audits,
        "cpu_ns": cpu_ns,
    }


def one_world(seed, cohort):
    candidate = trial(seed, cohort, "module_active", "diagnostic")
    arms = {"module_active": candidate}
    for arm in PAIRED[1:]:
        arms[arm] = trial(seed, cohort, arm, "replay",
                          candidate["action_plan"])
        if arms[arm]["physical_ledger"] != candidate["physical_ledger"]:
            raise AssertionError("SL15_REPLAY_PHYSICAL_INFORMATION_DRIFT")
    arms["module_passive"] = trial(
        seed, cohort, "module_passive", "passive"
    )
    if len({r["trace_first48_sha256"] for r in arms.values()}) != 1:
        raise AssertionError("SL15_COMMON_PRE48_HISTORY_MISMATCH")
    return {"seed":seed, "cohort":cohort, "arms":arms}


def return_flags(world_record):
    """Only the evaluator can classify genuine versus harmful module recall."""
    world = World(world_record["seed"], world_record["cohort"])
    transitions = world_record["arms"]["module_active"]["transitions"]
    flags = {"A2":False, "B2":False, "A4":False, "falseC":False}
    for t in transitions:
        if not t["archived_reuse"]:
            continue
        step, module = t["physical_step"], t["module"]
        rules = world.rules_a if world._phase(step) == "A" else (
            world.rules_b if world._phase(step) == "B" else world.rules_c
        )
        true_gate = rules[module]
        retrieved_gate = t["stored_gate_at_switch"]
        faithful = all(
            p.gate(retrieved_gate,q) == p.gate(true_gate,q)
            for q in range(4)
        )
        birth = t["slot_birth_physical_step"]
        if faithful and 48 <= step < 72 and birth < 24:
            flags["A2"] = True
        if faithful and 72 <= step < 96 and 24 <= birth < 48:
            flags["B2"] = True
        if faithful and 72 <= step < 96 and birth < 24:
            flags["A4"] = True
        if world_record["cohort"] == "ABAC" and step >= 72 and not faithful:
            flags["falseC"] = True
    return flags


def run():
    worlds = [one_world(seed,cohort) for cohort,seeds in COHORTS.items()
              for seed in seeds]
    keys = ("correct","wrong_confident","unseen_correct",
            "unseen_wrong_confident","unseen_local_correct",
            "unseen_local_wrong_confident")
    aggregate = {
        cohort:{
            arm:{
                str(t):{
                    key:sum(w["arms"][arm]["audits"][str(t)][key]
                        for w in worlds if w["cohort"] == cohort)
                    for key in keys
                } for t in AUDITS
            } for arm in ARMS
        } for cohort in COHORTS
    }
    counts = {
        "ABAB_A2":sum(return_flags(w)["A2"] for w in worlds
                      if w["cohort"] == "ABAB"),
        "ABAB_B2":sum(return_flags(w)["B2"] for w in worlds
                      if w["cohort"] == "ABAB"),
        "MIXED_A4":sum(return_flags(w)["A4"] for w in worlds
                       if w["cohort"] == "MIXED"),
        "ABAC_falseC":sum(return_flags(w)["falseC"] for w in worlds
                          if w["cohort"] == "ABAC"),
    }
    cand,no,full,bayes,rolling=ARMS[:5]
    v=lambda co,arm,t,key="correct":aggregate[co][arm][str(t)][key]
    cpu_bayes=statistics.median(
        w["arms"][cand]["cpu_ns"]/max(1,w["arms"][bayes]["cpu_ns"])
        for w in worlds
    )
    cpu_no=statistics.median(
        w["arms"][cand]["cpu_ns"]/max(1,w["arms"][no]["cpu_ns"])
        for w in worlds
    )
    primary={
        "ABAB_A2_true_module_reactivation":counts["ABAB_A2"]>=5,
        "ABAB_B2_true_module_reactivation":counts["ABAB_B2"]>=5,
        "ABAB_B2_final_vs_no_retrieval":v("ABAB",cand,96)>=v("ABAB",no,96)+12,
        "ABAB_B2_final_vs_SL14_bank":v("ABAB",cand,96)>=v("ABAB",full,96)+6,
        "ABAB_B2_final_vs_independent_bayes":
            v("ABAB",cand,96)>=v("ABAB",bayes,96)+4,
        "ABAB_B2_final_vs_rolling":v("ABAB",cand,96)>=v("ABAB",rolling,96)+4,
        "ABAB_B2_unseen_vs_bayes":
            v("ABAB",cand,96,"unseen_correct")>=
            v("ABAB",bayes,96,"unseen_correct")+2,
        "ABAC_false_module_reactivation":counts["ABAC_falseC"]<=2,
        "ABAC_final_vs_SL14_bank":v("ABAC",cand,96)>=v("ABAC",full,96)+12,
        "ABAC_final_no_retrieval_guardrail":
            v("ABAC",cand,96)>=v("ABAC",no,96)-8,
        "MIXED_A4_true_module_reactivation":counts["MIXED_A4"]>=4,
        "MIXED_final_vs_no_retrieval":
            v("MIXED",cand,96)>=v("MIXED",no,96)+8,
        "STABLE_nonregression":v("STABLE",cand,96)>=v("STABLE",no,96)-8,
        "STABLE_wrong_confident_guardrail":
            v("STABLE",cand,96,"wrong_confident")<=
            v("STABLE",no,96,"wrong_confident")+8,
        "median_cpu_ratio_vs_independent_bayes":cpu_bayes<=2.5,
        "median_cpu_ratio_vs_no_retrieval":cpu_no<=1.8,
    }
    charged=sum(r["charged_steps"] for w in worlds
                for r in w["arms"].values())
    observed=sum(r["causal_observations"] for w in worlds
                 for r in w["arms"].values())
    if (len(worlds)!=32 or charged!=18432 or observed!=14784 or
        any(max(r["snapshot_bytes"]+[r["final_snapshot_bytes"]])>8192
            or r["charged_input_perturbations"]!=19
            for w in worlds for r in w["arms"].values())):
        raise AssertionError("SL15_REGISTERED_PAID_BUDGET_VIOLATION")
    mixed = (
        counts["ABAB_A2"]>0 or counts["ABAB_B2"]>0 or
        v("ABAB",cand,96)>v("ABAB",no,96) or
        v("ABAC",cand,96)>v("ABAC",full,96)
    )
    return {
        "schema":SCHEMA,"freeze_sha":FREEZE,"parent_sha":PARENT,
        "world_count":len(worlds),"arms":list(ARMS),
        "charged_steps":charged,"paid_causal_observations":observed,
        "charged_input_perturbations":charged-observed,
        "primary_gates":primary,"primary_pass":all(primary.values()),
        "classification":"DEV_SIGNAL_NOT_SCIENCE" if all(primary.values()) else (
            "MIXED_DEV" if mixed else "NEGATIVE_DEV"),
        "scientific_acceptance":"UNVERIFIED","native_model_changed":False,
        "same_paid_physical_information_within_replay":True,
        "passive_policy_has_different_information":True,
        "archive_reuse_counts":counts,
        "median_cpu_ratio_candidate_vs_bayes":cpu_bayes,
        "median_cpu_ratio_candidate_vs_no_retrieval":cpu_no,
        "aggregate":aggregate,"worlds":worlds,
    }


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,separators=(",",":")))

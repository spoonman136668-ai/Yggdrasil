"""DG1-SL06: paid action selection for three-context causal memory.

Freeze: 2d3e530cf21e0a87596246eff648832c66737058.
All pre-cold physical trajectories are identical. Post-cold, each arm selects
real charged interventions; they diverge as part of the experimental variable.
Hidden phase/seed and evaluator audits NEVER enter learner/action selection.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
FREEZE = "2d3e530cf21e0a87596246eff648832c66737058"
PARENT = "6e88c22f63ebd9bf3b69becf33a8d27ee447abe1"
SCHEMA = "ygg.dg1-sl06.paid-active-causal-memory.v1"
COHORTS = {
    "ABCA": tuple(range(99001, 99009)),
    "ABCB": tuple(range(99009, 99017)),
    "STABLE": tuple(range(99017, 99025)),
    "ABCD_OOD": tuple(range(99025, 99033)),
}
ARMS = (
    "native_active",
    "native_passive",
    "native_random",
    "native_active_no_gate",
    "conventional_active",
    "conventional_passive",
    "two_bank_active",
)
FLIPS = (6, 14, 22, 30, 38, 46, 54, 62, 70, 78)
AUDITS = (60, 64, 72, 80)

def load(relative, name):
    path = BASE / relative
    spec = importlib.util.spec_from_file_location(name, path)
    instance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(instance)
    return instance

sl05 = load("dg1-sl05-20261113/sl05.py", "sl06_frozen_sl05")
hc09 = sl05.native
conventional_rules = sl05.control

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")

class World(sl05.World):
    """Frozen SL05 physics with a separate, registered prospective seed range.

    World step takes an agent-selected actual paid causal action only after 60.
    The physics/hidden regime stays sealed in the evaluator-owned environment.
    """
    def __init__(self, seed, group):
        if group not in COHORTS or seed not in COHORTS[group]:
            raise ValueError("SL06_UNREGISTERED_WORLD")
        self.seed = seed
        self.group = "STATIONARY" if group == "STABLE" else group
        self.paid = 0
        self.rules = [[0] * 4 for _ in range(3)]
        for action in range(4):
            used = set()
            for phase in range(3):
                r = random.Random(seed * 131 + phase * 719 + action * 47)
                h = r.randrange(40)
                while h in used:
                    h = (h + 1) % 40
                used.add(h)
                self.rules[phase][action] = h

    def step(self, state, step, chosen=None):
        hc09.valid_state(state)
        if type(step) is not int or step != self.paid or not 0 <= step < 80:
            raise ValueError("SL06_INVALID_PAID_STEP")
        self.paid += 1
        if step in FLIPS:
            bit = (self.seed // 7 + step // 8) % 4
            return "flip", bit, state ^ (1 << bit)
        if step < 60:
            if chosen is not None:
                raise ValueError("SL06_PRE60_ACTION_OVERRIDE")
            action = step % 4
        else:
            hc09.valid_action(chosen)
            action = chosen
        return "causal", action, self._truth(state, action, self.phase(step))

    def audit_truth(self, state, action, completed):
        if completed not in AUDITS:
            raise ValueError("SL06_UNREGISTERED_AUDIT")
        return self._truth(state, action, self.phase(completed - 1))

def banks_of(model):
    if isinstance(model, sl05.ColdThreeBank):
        return model.banks
    if isinstance(model, sl05.ConventionalHMM3):
        return model.banks
    # The frozen two-bank SL03 learner carries its real masks here.
    if isinstance(model, sl05.sl04.sl03.Learner):
        return model.model.banks
    raise ValueError("SL06_UNKNOWN_BANK_CONTAINER")

def native_information_action(model, state):
    """Select an action from physical-rule disagreement, not the simulator."""
    hc09.valid_state(state)
    banks = banks_of(model)
    if not 1 <= len(banks) <= 3:
        raise ValueError("SL06_BANK_CAPACITY")
    priority = []
    for action in range(4):
        exact_zero = exact_one = 0
        uncertainty = 0
        for bank in banks:
            z, o = hc09.counts(bank[action], state)
            exact_zero += int(z > 0 and o == 0)
            exact_one += int(o > 0 and z == 0)
            uncertainty += z * o
        priority.append((exact_zero * exact_one, uncertainty, -action))
    return max(range(4), key=lambda a: priority[a])

def conventional_information_action(model, state):
    """Independent posterior-weighted competing active-intervention policy."""
    hc09.valid_state(state)
    if not isinstance(model, sl05.ConventionalHMM3):
        raise ValueError("SL06_CONVENTIONAL_MODEL_EXPECTED")
    score = []
    for action in range(4):
        mixture_mean = 0.0
        within_uncertainty = 0.0
        for bank, weight in zip(model.banks, model.weights):
            z, o = conventional_rules.posterior_counts(bank[action], state)
            n = z + o
            prob = o / n if n else 0.5
            mixture_mean += weight * prob
            within_uncertainty += weight * (prob * (1.0 - prob))
        disagreement = mixture_mean * (1.0 - mixture_mean)
        score.append((disagreement, within_uncertainty, -action))
    return max(range(4), key=lambda a: score[a])

def choose(arm, learner, state, step):
    """Pure decision, no world/seed, no free observations or physics calls."""
    hc09.valid_state(state)
    if type(step) is not int or not 60 <= step < 80:
        raise ValueError("SL06_PROBE_OUTSIDE_WINDOW")
    if arm in ("native_active", "native_active_no_gate", "two_bank_active"):
        return native_information_action(learner, state)
    if arm == "conventional_active":
        return conventional_information_action(learner, state)
    if arm in ("native_passive", "conventional_passive"):
        return step % 4
    if arm == "native_random":
        return random.Random(777 + step).randrange(4)
    raise ValueError("SL06_UNKNOWN_ACTION_POLICY")

def learner_for(arm):
    if arm in ("native_active", "native_passive", "native_random"):
        return sl05.ColdThreeBank(True, False)
    if arm == "native_active_no_gate":
        return sl05.ColdThreeBank(False, False)
    if arm in ("conventional_active", "conventional_passive"):
        return sl05.ConventionalHMM3(True)
    if arm == "two_bank_active":
        return sl05.make_arm("frozen_sl04_two_bank")
    raise ValueError("SL06_UNKNOWN_LEARNER")

def restore(arm, snapshot):
    if arm in ("native_active", "native_passive", "native_random",
               "native_active_no_gate"):
        obj = sl05.ColdThreeBank.restore(snapshot)
        if obj.evict or obj.gate != (arm != "native_active_no_gate"):
            raise ValueError("SL06_COLD_ARM_IDENTITY")
        return obj
    if arm in ("conventional_active", "conventional_passive"):
        obj = sl05.ConventionalHMM3.restore(snapshot)
        if not obj.replay:
            raise ValueError("SL06_CONTROL_ARM_IDENTITY")
        return obj
    if arm == "two_bank_active":
        return sl05.restore_arm("frozen_sl04_two_bank", snapshot)
    raise ValueError("SL06_UNKNOWN_ARM_RESTORE")

def audit(model, environment, seen, stage):
    verdict = {k: 0 for k in ("correct", "wrong_confident", "abstained",
                              "unseen_correct", "unseen_wrong_confident",
                              "unseen_abstained")}
    for state in range(16):
        for action in range(4):
            expected = environment.audit_truth(state, action, stage)
            got = model.predict(state, action)
            key = ("abstained" if got is None else
                   "correct" if got == expected else "wrong_confident")
            verdict[key] += 1
            if (state, action) not in seen:
                verdict["unseen_" + key] += 1
    return verdict

def experiment(seed, group):
    """Independent post-cold branches with equal paid physical budgets."""
    outputs = {}
    prehistory_hashes = {}
    for arm in ARMS:
        env = World(seed, group)
        model = learner_for(arm)
        state = seed % 16
        seen = set()
        ledger = []
        prequential = {"correct": 0, "wrong_confident": 0, "abstained": 0}
        early_return = {"correct": 0, "wrong_confident": 0, "abstained": 0}
        stages = {}
        frozen = False
        checkpoint_sizes = {}
        cpu_ns = 0
        for step in range(80):
            if step == 60:
                checkpoint = model.snapshot()
                cold = restore(arm, checkpoint)
                if checkpoint != cold.snapshot() or any(
                    model.predict(s, a) != cold.predict(s, a)
                    for s in range(16) for a in range(4)
                ):
                    raise AssertionError("SL06_COLD_RESTORE_DIVERGENCE")
                frozen = True
                checkpoint_sizes["60"] = len(checkpoint)
                model = cold
            selected = choose(arm, model, state, step) \
                       if step >= 60 and step not in FLIPS else None
            before = state
            kind, action, after = env.step(state, step, selected)
            ledger.append([before, kind, action, after])
            if kind == "causal":
                t0 = time.perf_counter_ns()
                got = model.predict(before, action)
                key = ("abstained" if got is None else
                       "correct" if got == after else "wrong_confident")
                prequential[key] += 1
                if step >= 60:
                    early_return[key] += 1
                model.observe(before, action, after)
                cpu_ns += time.perf_counter_ns() - t0
                seen.add((before, action))
            state = after
            if (step + 1) % 8 == 0:
                t0 = time.perf_counter_ns()
                model.rest()
                cpu_ns += time.perf_counter_ns() - t0
            if (step + 1) in AUDITS:
                stages[str(step+1)] = audit(model, env, seen, step+1)
        if not frozen or env.paid != 80 or sum(e[1]=="flip" for e in ledger)!=10:
            raise AssertionError("SL06_ACTION_OR_COLD_CUSTODY")
        raw = model.snapshot()
        cold = restore(arm, raw)
        if raw != cold.snapshot() or any(
            model.predict(s,a)!=cold.predict(s,a)
            for s in range(16) for a in range(4)
        ):
            raise AssertionError("SL06_FINAL_COLD_DIVERGENCE")
        checkpoint_sizes["80"] = len(raw)
        if len(raw)>8192:
            raise AssertionError("SL06_SERIALIZED_MEMORY_LIMIT")
        first = hashlib.sha256(canonical(ledger[:60])).hexdigest()
        prehistory_hashes[arm] = first
        outputs[arm] = {
            "charged_actions": env.paid, "causal_observations": 70,
            "paid_flips": 10,
            "pre_cold_trajectory_sha256": first,
            "full_physical_trajectory_sha256": hashlib.sha256(canonical(ledger)).hexdigest(),
            "post_cold_action_sequence": [e[2] for e in ledger[60:] if e[1]=="causal"],
            "final_physical_state": state,
            "cold_restored": frozen,
            "checkpoint_bytes": checkpoint_sizes,
            "prequential": prequential,
            "early_post_cold_prequential": early_return,
            "audits": stages,
            "cpu_inference_update_rest_ns": cpu_ns,
        }
    if len(set(prehistory_hashes.values())) != 1:
        raise AssertionError("SL06_PRE_COLD_SHARED_INFO_FAIL")
    return {"seed":seed, "group":group, "pre_cold_trajectory_sha256":
            next(iter(prehistory_hashes.values())), "arms":outputs}

def run():
    worlds = [experiment(seed, group) for group, seeds in COHORTS.items()
              for seed in seeds]
    keys = ("correct","wrong_confident","abstained",
            "unseen_correct","unseen_wrong_confident","unseen_abstained")
    total = {group:{arm:{k:sum(
            w["arms"][arm]["audits"]["80"][k] for w in worlds if w["group"]==group)
                 for k in keys} for arm in ARMS} for group in COHORTS}
    early = {group:{arm:{k:sum(
            w["arms"][arm]["early_post_cold_prequential"][k] for w in worlds
            if w["group"] == group)
            for k in ("correct","wrong_confident","abstained")}
            for arm in ARMS} for group in COHORTS}
    primary_arm="native_active"
    controls=("native_passive","native_random","conventional_active")
    envelope={
        group:{
            "correct":max(total[group][a]["correct"] for a in controls),
            "unseen_correct":max(total[group][a]["unseen_correct"] for a in controls),
            "wrong_confident":min(total[group][a]["wrong_confident"] for a in controls),
            "early_correct":max(early[group][a]["correct"] for a in controls)
        } for group in COHORTS
    }
    x = total["ABCA"][primary_arm]
    y = total["ABCB"][primary_arm]
    z = total["STABLE"][primary_arm]
    oo = total["ABCD_OOD"][primary_arm]
    passed = (
        x["correct"] >= envelope["ABCA"]["correct"] + 16 and
        x["unseen_correct"] >= envelope["ABCA"]["unseen_correct"] + 8 and
        x["wrong_confident"] <= envelope["ABCA"]["wrong_confident"] + 4 and
        y["correct"] >= envelope["ABCB"]["correct"] + 16 and
        y["wrong_confident"] <= envelope["ABCB"]["wrong_confident"] + 4 and
        z["correct"] >= envelope["STABLE"]["correct"] - 16 and
        z["wrong_confident"] <= envelope["STABLE"]["wrong_confident"] + 4 and
        oo["wrong_confident"] <= envelope["ABCD_OOD"]["wrong_confident"] + 4 and
        early["ABCA"][primary_arm]["correct"] >= envelope["ABCA"]["early_correct"] + 8
    )
    both_gain = (x["correct"] > envelope["ABCA"]["correct"] and
                 y["correct"] > envelope["ABCB"]["correct"])
    category = ("DEV_SIGNAL_NOT_SCIENCE" if passed else
                "MIXED_DEV" if both_gain else "NEGATIVE_DEV")
    return {
        "schema":SCHEMA,
        "prereg_sha":FREEZE,"source_parent":PARENT,
        "classification":category,"primary_pass":passed,
        "scientific_acceptance":"UNVERIFIED",
        "native_specific_advantage_proven":False,
        "sleep_timing_advantage_proven":False,
        "same_budget_not_same_post_cold_information":True,
        "paired_shared_pre_cold_actions":True,
        "physical_actions_total_all_arms":sum(
            o["charged_actions"] for w in worlds for o in w["arms"].values()),
        "causal_observations_total_all_arms":sum(
            o["causal_observations"] for w in worlds for o in w["arms"].values()),
        "world_count":len(worlds), "competing_control_envelope":envelope,
        "aggregate_final":total,"aggregate_early_return":early,
        "worlds":worlds,
    }

if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,separators=(",",":")))

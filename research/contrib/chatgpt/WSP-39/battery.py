"""WSP39 preregistered DEV/PRIMARY full-capability ceiling assay."""
import argparse
import hashlib
import json
import random
import time
from model import ACTIONS, NumericModel, StrongGF2Control, direct_acquire, literal_observation_only

LEVELS = (1024, 512, 256, 128, 64)
FAMILIES = ("affine", "interaction_ood")
BUDGETS = ("basis_full", "basis_half")
SEEDS = {"DEV": (41, 43), "PRIMARY": (1049, 1051, 1061, 1063)}


def stable_int(*parts):
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode("ascii")).digest()[:8], "big")


class Teacher:
    """Hidden evaluator; only probe(action,state) crosses the learner boundary."""
    def __init__(self, cohort, world, width, family):
        if cohort not in SEEDS or world not in SEEDS[cohort] or width not in LEVELS or family not in FAMILIES:
            raise ValueError("WSP39_BAD_WORLD")
        self.width = width
        self.family = family
        self.rows = []
        self.biases = []
        for action in range(ACTIONS):
            rng = random.Random(stable_int("WSP39-V1", cohort, world, width, family, action))
            group = []
            bias = 0
            for out in range(width):
                sources = set()
                for _ in range(4):
                    sources.add(rng.randrange(width))
                mask = 0
                for src in sources:
                    mask |= 1 << src
                group.append(mask)
                if rng.randrange(2):
                    bias |= 1 << out
            self.rows.append(tuple(group))
            self.biases.append(bias)
        self.rows = tuple(self.rows)
        self.biases = tuple(self.biases)

    def step(self, action, state):
        if type(action) is not int or not 0 <= action < ACTIONS or type(state) is not int or state < 0 or state.bit_length() > self.width:
            raise ValueError("WSP39_BAD_EVALUATOR_INPUT")
        val = self.biases[action]
        for i, mask in enumerate(self.rows[action]):
            if (mask & state).bit_count() & 1:
                val ^= 1 << i
        if self.family == "interaction_ood" and (state & 3) == 3:
            val ^= 1
        return val

    def rollout(self, start, sequence):
        for action in sequence:
            start = self.step(action, start)
        return start

    def mutate(self, action, output_bit, input_bit):
        rows = list(self.rows)
        one = list(rows[action])
        one[output_bit] ^= (1 << input_bit)
        rows[action] = tuple(one)
        self.rows = tuple(rows)


def trial(cohort, seed, width, family, budget):
    teacher = Teacher(cohort, seed, width, family)
    basis = tuple(range(width if budget == "basis_full" else width // 2))
    audited = []
    def probe(action, state):
        if state != 0 and (state.bit_count() != 1 or state.bit_length() - 1 not in basis):
            raise AssertionError("WSP39_PROBE_OUTSIDE_BUDGET")
        result = teacher.step(action, state)
        audited.append((action, -1 if state == 0 else state.bit_length() - 1, result))
        return result
    t0 = time.perf_counter()
    learned, transcript = direct_acquire(width, probe, basis)
    acquire_seconds = time.perf_counter() - t0
    if transcript != tuple(audited) or len(transcript) != ACTIONS * (1 + len(basis)):
        raise AssertionError("WSP39_PROBE_CUSTODY")
    t0 = time.perf_counter()
    baseline = StrongGF2Control(width, transcript)
    baseline_build_s = time.perf_counter() - t0
    literal = literal_observation_only(width, transcript)
    t0 = time.perf_counter()
    snapshot = learned.snapshot()
    restored = NumericModel.restore(snapshot)
    restore_seconds = time.perf_counter() - t0
    if restored.snapshot() != snapshot or restored.rows != learned.rows:
        raise AssertionError("WSP39_COLD_MISMATCH")
    rng = random.Random(stable_int("WSP39-HOLDOUT", cohort, seed, width, family, budget))
    trace = hashlib.sha256()
    primitive_bits = primitive_correct = primitive_exact = primitive_samples = 0
    multi_bits = multi_correct = multi_exact = multi_samples = 0
    baseline_equal = true_seen = zero_baseline_bits = zero_baseline_exact = identity_baseline_bits = identity_baseline_exact = 0
    timing_numeric = timing_control = 0.0
    # Includes deliberately hard pair interaction x0=x1=1 plus varied states.
    states = [3] + [rng.getrandbits(width) for _ in range(7)]
    for state in states:
        for action in range(ACTIONS):
            t = time.perf_counter(); actual = restored.apply(action, state); timing_numeric += time.perf_counter() - t
            t = time.perf_counter(); ref = baseline.apply(action, state); timing_control += time.perf_counter() - t
            expected = teacher.step(action, state)
            if actual != ref:
                raise AssertionError("WSP39_MATCHED_ID_DIVERGENCE")
            baseline_equal += 1
            zero_baseline_bits += width - expected.bit_count()
            zero_baseline_exact += int(expected == 0)
            identity_baseline_bits += width - (state ^ expected).bit_count()
            identity_baseline_exact += int(state == expected)
            true_seen += int((action, state) in literal)
            primitive_bits += width
            primitive_correct += width - (actual ^ expected).bit_count()
            primitive_exact += int(actual == expected)
            primitive_samples += 1
            trace.update(bytes((action, int(actual == expected))))
    for k in range(8):
        state = rng.getrandbits(width)
        length = (2, 3, 4)[k % 3]
        actions = tuple(rng.randrange(ACTIONS) for _ in range(length))
        value = restored.rollout(state, actions)
        expected = teacher.rollout(state, actions)
        multi_bits += width
        multi_correct += width - (value ^ expected).bit_count()
        multi_exact += int(value == expected)
        multi_samples += 1
        trace.update(bytes((length, int(value == expected))))
    planner_success = planner_found = planner_trials = baseline_plan_equal = 0
    planning_s = baseline_planning_s = 0.0
    for _ in range(3):
        start = rng.getrandbits(width)
        hidden_route = tuple(rng.randrange(ACTIONS) for _ in range(3))
        goal = teacher.rollout(start, hidden_route)
        t = time.perf_counter()
        proposed = restored.plan(start, goal)
        planning_s += time.perf_counter() - t
        t = time.perf_counter()
        reference_plan = baseline.plan(start, goal)
        baseline_planning_s += time.perf_counter() - t
        baseline_plan_equal += int(proposed == reference_plan)
        if proposed != reference_plan:
            raise AssertionError("WSP39_INDEPENDENT_PLANNER_DIVERGENCE")
        planner_trials += 1
        if proposed is not None:
            planner_found += 1
            if restored.rollout(start, proposed) != goal:
                raise AssertionError("WSP39_PLANNER_INTERNAL_INCONSISTENCY")
            planner_success += int(teacher.rollout(start, proposed) == goal)
        trace.update(bytes((int(proposed is not None), int(proposed is not None and teacher.rollout(start, proposed) == goal))))
    # Exact local repair from two *new* genuine observations, both permitted for full and half.
    action = seed % ACTIONS
    output_bit = 0
    input_bit = 0
    before_zero = teacher.step(action, 0)
    before_basis = teacher.step(action, 1 << input_bit)
    teacher.mutate(action, output_bit, input_bit)
    after_zero = teacher.step(action, 0)
    after_basis = teacher.step(action, 1 << input_bit)
    if before_zero != after_zero or (before_basis ^ after_basis) != (1 << output_bit):
        raise AssertionError("WSP39_INTERVENTION_NOT_OBSERVABLE")
    inferred_bit = ((after_basis ^ after_zero) >> output_bit) & 1
    patched = restored.patch(action, output_bit, input_bit, inferred_bit)
    if (patched.rows[action][output_bit] ^ restored.rows[action][output_bit]) != (1 << input_bit):
        raise AssertionError("WSP39_NOT_SINGLE_WEIGHT_REPAIR")
    if patched.biases != restored.biases:
        raise AssertionError("WSP39_REPAIR_CHANGED_BIAS")
    if sum(a != b for aa, bb in zip(patched.rows, restored.rows) for a, b in zip(aa, bb)) != 1:
        raise AssertionError("WSP39_REPAIR_CROSSTALK")
    if NumericModel.restore(patched.snapshot()).snapshot() != patched.snapshot():
        raise AssertionError("WSP39_REPAIR_NOT_DURABLE")
    if budget == "basis_full" and family == "affine":
        challenge = rng.getrandbits(width)
        if patched.apply(action, challenge) != teacher.step(action, challenge):
            raise AssertionError("WSP39_REPAIR_LOST_KNOWN_RULE")
    # Fail-closed checkpoint, no source oracle access.
    for bad in (snapshot[:-1], snapshot + b"!", snapshot[:-1] + bytes([snapshot[-1] ^ 1])):
        try:
            NumericModel.restore(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("WSP39_CHECKPOINT_TAMPER_ACCEPTED")
    # Preserve an independently acquired second world through edits to the first.
    alternatives = [v for v in SEEDS[cohort] if v != seed]
    other_teacher = Teacher(cohort, alternatives[0], width, "affine")
    second, second_transcript = direct_acquire(width, other_teacher.step, (0,))
    bank = {"primary_before": snapshot, "independent_world": second.snapshot()}
    bank["primary_after"] = patched.snapshot()
    if bank["primary_before"] != snapshot or NumericModel.restore(bank["independent_world"]).snapshot() != second.snapshot():
        raise AssertionError("WSP39_MEMORY_INTERFERENCE")
    if len(second_transcript) != 8:
        raise AssertionError("WSP39_SECOND_WORLD_PROBE_BUDGET")
    # Expected inability to derive absent columns and nonlinear interactions.
    if budget == "basis_half":
        omitted = 1 << (width - 1)
        fresh = Teacher(cohort, seed, width, family)
        mismatch = any(restored.apply(a, omitted) != fresh.step(a, omitted) for a in range(ACTIONS))
        if not mismatch:
            raise AssertionError("WSP39_MISSING_COLUMN_CONTROL_INEFFECTIVE")
    if family == "interaction_ood":
        fresh = Teacher(cohort, seed, width, family)
        if all(restored.apply(a, 3) == fresh.step(a, 3) for a in range(ACTIONS)):
            raise AssertionError("WSP39_NONLINEAR_OOD_CONTROL_INEFFECTIVE")
    return {"dimension": width, "family": family, "budget": budget, "world": seed,
            "probe_count": len(transcript), "capacity_bits": ACTIONS * (width * width + width),
            "snapshot_bytes": len(snapshot), "primitive_correct_bits": primitive_correct,
            "primitive_total_bits": primitive_bits, "primitive_exact_states": primitive_exact,
            "primitive_states": primitive_samples, "multi_correct_bits": multi_correct,
            "multi_total_bits": multi_bits, "multi_exact_states": multi_exact,
            "multi_states": multi_samples, "planner_success": planner_success,
            "planner_found": planner_found, "planner_trials": planner_trials,
            "novel_lookup_hits": true_seen, "baseline_parity_count": baseline_equal,
            "baseline_planner_parity_count": baseline_plan_equal,
            "zero_bits_correct": zero_baseline_bits, "zero_states_exact": zero_baseline_exact,
            "identity_bits_correct": identity_baseline_bits, "identity_states_exact": identity_baseline_exact,
            "independent_world_retained": True, "cold": True, "repair": True, "negative_guards": True, "trace": trace.hexdigest(),
            "times_seconds": {"acquire": round(acquire_seconds, 6), "baseline_build": round(baseline_build_s, 6),
                              "cold": round(restore_seconds, 6), "numeric_inference": round(timing_numeric, 6),
                              "baseline_inference": round(timing_control, 6), "planning": round(planning_s, 6),
                              "baseline_planning": round(baseline_planning_s, 6)}}


def run(cohort="DEV"):
    if cohort not in SEEDS:
        raise ValueError("WSP39_BAD_COHORT")
    start = time.perf_counter()
    records = []
    for width in LEVELS:
        for family in FAMILIES:
            for budget in BUDGETS:
                for seed in SEEDS[cohort]:
                    records.append(trial(cohort, seed, width, family, budget))
    def applicable(r):
        return r["family"] == "affine" and r["budget"] == "basis_full"
    known = [r for r in records if applicable(r)]
    ok = all(r["primitive_exact_states"] == r["primitive_states"] and
             r["multi_exact_states"] == r["multi_states"] and
             r["planner_success"] == r["planner_trials"] for r in known)
    controls = all(r["baseline_parity_count"] == r["primitive_states"] and
                   r["baseline_planner_parity_count"] == r["planner_trials"] and
                   r["independent_world_retained"] and r["cold"] and r["repair"] and r["negative_guards"] for r in records)
    nonlin = [r for r in records if r["family"] == "interaction_ood" and r["budget"] == "basis_full"]
    partial = [r for r in records if r["family"] == "affine" and r["budget"] == "basis_half"]
    negative_worked = (sum(r["primitive_exact_states"] for r in nonlin) < sum(r["primitive_states"] for r in nonlin)
                       and sum(r["primitive_exact_states"] for r in partial) < sum(r["primitive_states"] for r in partial))
    if not (ok and controls and negative_worked):
        raise AssertionError("WSP39_INVALID_ASSAY")
    speed = []
    for width in LEVELS:
        comparable = [r for r in known if r["dimension"] == width]
        n = sum(r["times_seconds"]["numeric_inference"] + r["times_seconds"]["planning"] for r in comparable)
        b = sum(r["times_seconds"]["baseline_inference"] + r["times_seconds"]["baseline_planning"] for r in comparable)
        speed.append({"width": width, "numeric_plus_planning_seconds": round(n, 6),
                      "control_inference_seconds": round(b, 6), "ratio": round(n/max(b,1e-9), 4),
                      "cost_competitive": n <= 2*b})
    eligible = [r["width"] for r in speed if r["cost_competitive"]]
    digest = hashlib.sha256(json.dumps([{k:v for k,v in r.items() if k not in ("times_seconds",)} for r in records], sort_keys=True).encode()).hexdigest()
    return {"schema": "wsp39.maxfirst.capability-assay.v1", "cohort": cohort,
            "engineering": "PASS", "science": "SCIENTIFIC_NEGATIVE_NO_TRAINED_SUPERIORITY",
            "dimensions": LEVELS, "n_worlds": len(records),
            "known_affine_full_all_exact": ok, "partial_and_nonlinear_controls_effective": negative_worked,
            "largest_qualified_dimension": LEVELS[0],
            "largest_speed_competitive_dimension": max(eligible) if eligible else None,
            "speed": speed, "scores": records, "trace_sha256": digest,
            "seconds": round(time.perf_counter()-start, 6),
            "limits": "Specialized preauthored affine representation and oracle probes, not general intelligence; symbolic GF2 control parity, no trained neural comparator, no universal knowledge discovery."}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", choices=tuple(SEEDS), default="DEV")
    cfg = ap.parse_args()
    print(json.dumps(run(cfg.cohort), sort_keys=True, indent=2))

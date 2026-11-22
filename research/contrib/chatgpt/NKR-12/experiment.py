"""NKR-12: falsify NKR-11's fixed linear causal family on unseen conjunctions.

This experiment is a source-safe independent code path, NOT a production
learning engine. The environment is deliberately distinct from the learner.
No hidden mask, protected test consequence, phase signal, or truth access
passes to NativeInterventionRepair. The exact broader symbolic control sees
the SAME 16 public action outcomes, but a pre-listed conjunction family.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from yggdrasil.native_intervention_repair import (
    NativeInterventionRepair, BUNDLE_SCHEMA, SOURCE_MODE,
    SOURCE_KIND, canonical, digest,
)
from yggdrasil.public_causal_cells import PublicCausalCells

BASE = (1,2,4,8,3,5,6,9,10,12,13,14)
AND_MASKS = (3,5,6,9,10,12,7,11,13,14,15,7)
TRAIN = (0,1,2,4,8,3,5,10)
COLD = (6,7,9,11,12,13,14,15)
OLD_WORLD_COUNT = 12
NOISE_WORLDS = (0,1,2,3)


class IndependentActionWorld:
    """Private deterministic source of observable action consequences."""
    __slots__ = ("world_id", "interventions", "mode")

    def __init__(self, world_id, *, mode="nonlinear"):
        if (type(world_id) is not int or not 0 <= world_id < OLD_WORLD_COUNT
                or mode not in ("nonlinear", "noise")):
            raise ValueError("NKR12_WORLD_INVALID")
        self.world_id = world_id
        self.mode = mode
        self.interventions = 0

    def execute(self, context, action, *, warm=False):
        if (type(context) is not int or not 0 <= context < 16
                or type(action) is not int or action not in (0,1)):
            raise ValueError("NKR12_PUBLIC_ACTION_INVALID")
        self.interventions += 1
        if warm or self.mode == "noise":
            return ((context & (1 << (self.world_id % 4))).bit_count() & 1) ^ action
        base = ((context & BASE[self.world_id]).bit_count() & 1)
        nonlinear_effect = int(
            (context & AND_MASKS[self.world_id]) == AND_MASKS[self.world_id]
        )
        return base ^ (action & nonlinear_effect)


def bundle(source_id, records):
    return canonical({
        "schema": BUNDLE_SCHEMA,
        "source_id": source_id,
        "source_kind": SOURCE_KIND,
        "source_mode": SOURCE_MODE,
        "records": [list(r) for r in records],
    })


def observations(env, *, warm=False, inject_single_sensor_noise=False):
    if warm:
        positions = [(x,a) for x in range(16) for a in (0,1)]
    else:
        positions = [(0,1),(0,0)] + [
            (x,a) for x in TRAIN[1:] for a in (0,1)
        ]
    if len(positions) != (32 if warm else 16) or len(set(positions)) != len(positions):
        raise AssertionError("NKR12_FROZEN_PUBLIC_ACTION_BUDGET_DRIFT")
    result = []
    for index, (x,a) in enumerate(positions):
        outcome = env.execute(x,a,warm=warm)
        if inject_single_sensor_noise and index == 0 and not warm:
            outcome ^= 1  # explicitly one fabricated sensor corruption
        result.append((
            f"{'warm' if warm else 'public'}-{env.mode}-world-{env.world_id:02d}-{index:02d}",
            x,a,outcome
        ))
    return result


def independent_broader_symbolic_fit(records):
    """Independent exact *conjunction family* fit, without NKR-11 GF(2).

    The action-zero rows identify base intercept/main bit parity. Every
    conjunction mask from 1..15 is fitted with identical action outcomes.
    Unseen condition combinations remain ambiguous and cause abstention.
    """
    data = {(x,a):y for _,x,a,y in records}
    if len(data) != 16 or any((x,0) not in data or (x,1) not in data for x in TRAIN):
        raise ValueError("NKR12_STRONG_CONTROL_MISSING_OBSERVATIONS")
    intercept = data[(0,0)]
    base_mask = 0
    for bit in range(4):
        bitval = data[(1<<bit,0)] ^ intercept
        if bitval:
            base_mask |= 1 << bit
    for x in TRAIN:
        if data[(x,0)] != (intercept ^ ((x & base_mask).bit_count() & 1)):
            raise ValueError("NKR12_STRONG_CONTROL_BASE_NOT_PARITY")
    candidates=[]
    for mask in range(1,16):
        if all(
                data[(x,1)] ^ data[(x,0)] == int((x & mask) == mask)
                for x in TRAIN):
            candidates.append(mask)
    if not candidates:
        raise ValueError("NKR12_NO_EXACT_CONJUNCTION_FIT")
    return intercept,base_mask,tuple(candidates)


def independent_broader_symbolic_predict(fit, x, a):
    intercept,base_mask,candidates=fit
    baseline = intercept ^ ((x & base_mask).bit_count() & 1)
    if a == 0:
        return baseline
    possible={baseline ^ int((x & mask) == mask) for mask in candidates}
    return next(iter(possible)) if len(possible)==1 else None


def _record_correct(prediction, truth):
    return int(prediction is not None and prediction == truth)


def run_frozen():
    now=time.monotonic()
    initial_native=PublicCausalCells().snapshot()
    totals={
        "nonlinear_worlds":12,
        "sensor_noise_worlds":4,
        "public_feedback_per_nonlinear_world":16,
        "cold_queries":192,
        "old_retention_queries":384,
        "native_accepted_repairs":0,
        "native_rejected_inconsistent_evidence":0,
        "native_cold_coverage":0,
        "native_cold_correct":0,
        "native_confident_cold_errors":0,
        "strong_control_cold_coverage":0,
        "strong_control_cold_correct":0,
        "strong_control_cold_abstentions":0,
        "strong_abstained_on_native_wrong":0,
        "first_contradictions":0,
        "old_retention_correct":0,
        "single_sensor_noise_refusals":0,
        "single_sensor_noise_false_repairs":0,
        "single_noise_old_checkpoint_preserved":0,
    }
    results=[]
    for world in range(12):
        env=IndependentActionWorld(world)
        warm=observations(env,warm=True)
        raw=bundle(f"nkr12-warm-world-{world:02d}",warm)
        original=NativeInterventionRepair.from_warmup(raw,digest(raw))
        original_sha=original.checkpoint_sha256
        repair=observations(env)
        if len(repair)!=16:
            raise AssertionError("NKR12_TRAIN_BUDGET_INCORRECT")
        if original.prior(repair[0][1],repair[0][2]) == repair[0][3]:
            raise AssertionError("NKR12_FROZEN_FIRST_CONTRADICTION_ABSENT")
        totals["first_contradictions"] += 1
        feedback=bundle(f"nkr12-repair-world-{world:02d}",repair)
        rejected=False
        try:
            candidate,receipt=original.stage_public_interventions(
                feedback,digest(feedback))
            if candidate is original or not candidate.change_detected:
                raise AssertionError("NKR12_REPAIR_IGNORED_FIRST_CONTRADICTION")
            # This is a separate research candidate, never a promoted owner
            # checkpoint. Count "accepted" as internal fit for diagnostic.
            totals["native_accepted_repairs"] += 1
            restored=NativeInterventionRepair(
                candidate.checkpoint(),candidate.checkpoint_sha256)
        except ValueError as exc:
            if "NKR11_CONTRADICTORY_SAME_EPOCH_EVIDENCE" not in str(exc):
                raise
            rejected=True
            totals["native_rejected_inconsistent_evidence"] += 1
            restored=None
        if original.checkpoint_sha256 != original_sha:
            raise AssertionError("NKR12_OLD_CHECKPOINT_REWRITTEN")
        strong=independent_broader_symbolic_fit(repair)
        if AND_MASKS[world] not in strong[2]:
            raise AssertionError("NKR12_TRUE_MASK_OUTSIDE_STRONG_CONTROL_SET")
        local={"world":world,"and_mask":AND_MASKS[world],
               "native_rejected_nonlin":rejected,
               "strong_consistent_masks":len(strong[2]),
               "native_errors":0,"strong_abstentions":0,
               "native_correct":0,"strong_correct":0}
        for x in COLD:
            for a in (0,1):
                before=(None if restored is None else
                        restored.predict(x,a)["public_outcome"])
                control=independent_broader_symbolic_predict(strong,x,a)
                truth=env.execute(x,a)
                totals["native_cold_coverage"] += int(before is not None)
                totals["native_cold_correct"] += _record_correct(before,truth)
                totals["native_confident_cold_errors"] += int(
                    before is not None and before != truth)
                totals["strong_control_cold_coverage"] += int(control is not None)
                totals["strong_control_cold_correct"] += _record_correct(control,truth)
                totals["strong_control_cold_abstentions"] += int(control is None)
                totals["strong_abstained_on_native_wrong"] += int(
                    before is not None and before != truth and control is None)
                local["native_correct"] += _record_correct(before,truth)
                local["strong_correct"] += _record_correct(control,truth)
                local["native_errors"] += int(before is not None and before != truth)
                local["strong_abstentions"] += int(control is None)
        for x in range(16):
            for a in (0,1):
                truth=env.execute(x,a,warm=True)
                totals["old_retention_correct"] += _record_correct(
                    original.prior(x,a),truth)
                if restored is not None and restored.prior(x,a) != original.prior(x,a):
                    raise AssertionError("NKR12_PREVIOUS_MECHANISM_ERASED")
        results.append(local)
    noise=[]
    for world in NOISE_WORLDS:
        env=IndependentActionWorld(world,mode="noise")
        warm=observations(env,warm=True)
        raw=bundle(f"nkr12-noise-warm-{world:02d}",warm)
        original=NativeInterventionRepair.from_warmup(raw,digest(raw))
        checkpoint=original.checkpoint()
        measured=observations(env,inject_single_sensor_noise=True)
        if (sum(int(original.prior(x,a) != y) for _,x,a,y in measured)!=1
                or measured[0][1:4] != (0,1,0)):
            raise AssertionError("NKR12_NOT_EXACTLY_ONE_SENSOR_FLIP")
        input_raw=bundle(f"nkr12-noise-events-{world:02d}",measured)
        refused=False
        try:
            candidate,_=original.stage_public_interventions(input_raw,digest(input_raw))
            if candidate is not original and candidate.change_detected:
                totals["single_sensor_noise_false_repairs"] += 1
            else:
                refused=True
        except ValueError as exc:
            if "NKR11_CONTRADICTORY_SAME_EPOCH_EVIDENCE" not in str(exc):
                raise
            refused=True
        totals["single_sensor_noise_refusals"] += int(refused)
        if original.checkpoint()!=checkpoint or original.change_detected:
            raise AssertionError("NKR12_SINGLE_NOISE_DESTROYED_OLD_MEMORY")
        totals["single_noise_old_checkpoint_preserved"] += 1
        noise.append({"world":world,"refused_single_sensor_flip":refused})
    if PublicCausalCells().snapshot()!=initial_native:
        raise AssertionError("NKR12_ORIGINAL_CAUSAL_OWNER_MUTATED")
    diagnosis=(
        totals["native_confident_cold_errors"]>0
        and totals["native_rejected_inconsistent_evidence"]>0
        and totals["strong_abstained_on_native_wrong"]>0
        and totals["old_retention_correct"]==384
        and totals["single_sensor_noise_false_repairs"]==0
        and totals["single_noise_old_checkpoint_preserved"]==4
        and totals["first_contradictions"]==12)
    return {
        "schema":"yggdrasil.nkr12.out-of-family-development-falsification.v1",
        "classification":(
            "FIXED_PARITY_OUT_OF_FAMILY_LIMITATION_EXPOSED" if diagnosis
            else "FROZEN_DIAGNOSTIC_NOT_FULLY_CONFIRMED"),
        "source_mode":"engineering_fixture_only",
        "outcome_truth_authentic_external":False,
        "is_fixed_parity_family_wider_than_tested_truth":False,
        "native_one_world_overfit_exclusion":False,
        "hypothesis_family_expanded_in_native":False,
        "per_world":results,"noise_worlds":noise,"totals":totals,
        "frozen_falsification_criteria_met":diagnosis,
        "strong_control_has_prespecified_conjunction_family":True,
        "native_accepted":False,
        "native_original_memory_unchanged":True,
        "scientific_pass":False,
        "new_authentic_world_relations_certified":0,
        "whole_process_seconds":time.monotonic()-now,
    }


if __name__=="__main__":
    print("NKR12_FROZEN_FALSIFICATION="+json.dumps(
        run_frozen(),sort_keys=True,separators=(",",":")),flush=True)

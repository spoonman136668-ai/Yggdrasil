"""NKR-12 reused NKR-11 fixture-only engineering retention screen.

This module is an evaluator; it imports the source generator. Native learner
module does not. No untouched first-use cohort, real source or owner model.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time

from yggdrasil.native_cumulative_action_bank import NativeCumulativeActionBank
from yggdrasil.native_intervention_repair import (
    NativeInterventionRepair, canonical, digest,
)
from yggdrasil.public_causal_cells import PublicCausalCells

SCRIPT = (Path(__file__).resolve().parents[4] /
          "research/contrib/chatgpt/NKR-11/experiment.py")
spec = importlib.util.spec_from_file_location("nkr12_reused_fixture", SCRIPT)
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


def address(world_id):
    return (world_id, False) if world_id < 7 else (world_id - 7, True)


def run():
    t0 = time.perf_counter()
    preserved_original_cells = PublicCausalCells().snapshot()
    bank = NativeCumulativeActionBank()
    reference = {}
    envs = {}
    public_evidence = []
    for world_id in range(12):
        env = study.ComputationalEnvironment(world_id)
        envs[world_id] = env
        addr, retained = address(world_id)
        warm_events = study.collect_warmup(env)
        public_evidence.append([world_id, "warm", [list(e) for e in warm_events]])
        warm = study.evidence(f"warm-bundle-world-{world_id:02d}", warm_events)
        bank, receipt = bank.install_public(addr, warm, digest(warm),
                                            retained=retained)
        ref = NativeInterventionRepair.from_warmup(warm, digest(warm))
        assert receipt["stored_slots"] == world_id+1
        interventions = study.collect_paired_interventions(env)
        public_evidence.append([world_id, "repair",
                                [list(e) for e in interventions]])
        repair = study.evidence(f"repair-bundle-world-{world_id:02d}",
                                interventions)
        previous = bank
        bank, outcome = bank.repair_public(addr, repair, digest(repair),
                                           retained=retained)
        ref, ref_outcome = ref.stage_public_interventions(repair, digest(repair))
        if (outcome["new_events"] != 16
                or outcome["classification"] !=
                "FIXTURE_CONTRADICTION_GATED_NEW_RELATION_CANDIDATE"
                or ref_outcome["new_events"] != 16
                or previous.prior(addr, 0, 1, retained=retained) != 1):
            raise AssertionError("native public intervention mismatch")
        reference[world_id] = ref
    before = bank.checkpoint()
    bank = NativeCumulativeActionBank.restore(before, bank.checkpoint_sha256)
    if bank.checkpoint() != before:
        raise AssertionError("cold bank mismatch")
    correct_warm = correct_cold = symbolic = ref_equal = 0
    traces = []
    for world_id in range(12):
        env = envs[world_id]
        addr, retained = address(world_id)
        ref = reference[world_id]
        for x in range(16):
            for action in (0, 1):
                pred = bank.prior(addr, x, action, retained=retained)
                truth = env.intervene(x, action, old_mechanism=True)
                if pred != ref.prior(x, action):
                    raise AssertionError("previous native relation lost")
                correct_warm += int(pred == truth)
                traces.append(["old",world_id,x,action,pred,truth])
        new_train = study.collect_paired_interventions(env)
        matches = study.independent_symbolic_fit(new_train)
        for x in study.COLD_CONTEXTS:
            for action in (0, 1):
                scored = bank.predict(addr,x,action,retained=retained)
                result = scored["public_outcome"]
                truth = env.intervene(x,action)
                reference_prediction = ref.predict(x, action)["public_outcome"]
                if result != reference_prediction:
                    raise AssertionError("independent per-world reference drift")
                ref_equal += 1
                correct_cold += int(result == truth)
                vote = {
                  study._independent_candidate_signature(m,x,action)
                  for m in matches
                }
                if len(vote) != 1:
                    raise AssertionError("symbolic control underdetermined")
                symbolic += int(next(iter(vote))==truth)
                traces.append(["new",world_id,x,action,result,truth])
    if (correct_warm != 384 or correct_cold != 192
            or symbolic != 192 or ref_equal != 192
            or bank.stored_slots != tuple(range(12))
            or PublicCausalCells().snapshot() != preserved_original_cells):
        raise AssertionError("NKR12 development retention gate failed")
    result={
        "schema":"yggdrasil.nkr12.native-cumulative-reuse-dev.v1",
        "classification":"ENGINEERING_DEV_PASS_SCIENCE_UNVERIFIED",
        "engineered_slots":16,"loaded_slots":12,
        "observed_warm_interventions":384,
        "observed_repair_interventions":192,
        "warm_correct":correct_warm,"warm_total":384,
        "cold_correct":correct_cold,"cold_total":192,
        "fully_fit_symbolic_correct":symbolic,
        "independent_reference_equal_predictions":ref_equal,
        "cold_process_checkpoint_recovered":True,
        "checkpoint_bytes":bank.checkpoint_bytes,
        "member_bytes_sum":sum(len(m.checkpoint()) for m in reference.values()),
        "bank_checkpoint_sha256":bank.checkpoint_sha256,
        "public_evidence_sha256":digest(canonical(public_evidence)),
        "prediction_trace_sha256":digest(canonical(traces)),
        "legacy_ypc1_unchanged":True,
        "scientific_first_use_consumed":0,
        "accepted_native_changed":False,
        "runner_used":"isolated source-only or pinned GitHub-hosted verification",
        "elapsed_seconds":round(time.perf_counter()-t0,6),
    }
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dev",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary:p.error("NKR12 SCIENTIFIC FIRST USE DISARMED")
    if not args.source_dev:p.error("source-only --source-dev is required")
    print("NKR12_DEV="+json.dumps(run(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()

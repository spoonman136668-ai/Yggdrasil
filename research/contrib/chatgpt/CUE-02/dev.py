"""CUE-02 source-only finite-public-domain novel-law falsification.

All source identities and hidden nonlinear environment laws live HERE, never in
the native auditor. Reuses published CUE-01 / NKR-11 fixture evidence; no new
protected independent science or model training is performed.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from yggdrasil.native_finite_cue_audit import audit, probe_order, BUDGET_SWEEP
from yggdrasil.native_intervention_repair import canonical, digest
from yggdrasil.native_cumulative_action_bank import NativeCumulativeActionBank

PATH=ROOT/"research/contrib/chatgpt/CUE-01/dev.py"
spec=importlib.util.spec_from_file_location("cue02_reused_cue01_fixture",PATH)
fixture=importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
POLICIES=("dense","lex","hash")
KNOWNS=12
UNKNOWNS=4


def symbolic_filter(models,cues):
    """Independent fully fitted equal-information exact symbolic baseline.

    Does not call the native CUE-02 auditor or consume target IDs.
    """
    consistent=[]
    for slot,reference in sorted(models.items()):
        checked=True
        for x,action,observed in cues:
            value=reference.predict(x,action)["public_outcome"]
            if value is None or value != observed:
                checked=False
                break
        if checked:
            consistent.append(slot)
    return tuple(consistent)


def one_audit(bank,models,cues):
    model=audit(bank,cues)
    symbolic=symbolic_filter(models,cues)
    if tuple(model["compatible_slots"])!=symbolic:
        raise AssertionError("CUE02_STRONG_FULL_CAPACITY_SYMBOLIC_PARITY_FAILED")
    if model["candidate_slot"]!=(symbolic[0] if len(symbolic)==1 else None):
        raise AssertionError("CUE02_STRONG_SYMBOLIC_DECISION_DISAGREEMENT")
    return model


def _empty_counts():
    return {"known_correct":0,"known_wrong":0,"known_unresolved":0,
            "unknown_falsified":0,"unknown_false_match":0,
            "unknown_ambiguous":0,"observations_paid":0}


def evaluate():
    start=time.perf_counter()
    bank,refs,public_source_sha=fixture.build_bank()
    raw=bank.checkpoint()
    bank=NativeCumulativeActionBank.restore(raw,bank.checkpoint_sha256)
    all_results={p:{str(b):_empty_counts() for b in BUDGET_SWEEP}
                 for p in POLICIES}
    traces=[]
    for policy in POLICIES:
        order=probe_order(policy)
        if len(order)!=32 or len(set(order))!=32:
            raise AssertionError("CUE02_NOT_A_FULL_PUBLIC_INTERVENTION_ORDER")
        for world_idx in range(KNOWNS+UNKNOWNS):
            if world_idx<KNOWNS:
                env=fixture.study.ComputationalEnvironment(world_idx)
                oracle=env.intervene
            else:
                index=world_idx-KNOWNS
                oracle=lambda x,a,i=index:fixture.unknown_outcome(i,x,a)
            # High-first evidence materialization: execute all 32 actual public
            # interventions. Smaller budgets reuse exact same prefix, not
            # additional protected data or separate source first uses.
            events=tuple((x,a,oracle(x,a)) for x,a in order)
            for budget in BUDGET_SWEEP:
                cues=events[:budget]
                result=one_audit(bank,refs,cues)
                counts=all_results[policy][str(budget)]
                counts["observations_paid"]+=budget
                selected=result["candidate_slot"]
                if world_idx<KNOWNS:
                    counts["known_correct"]+=int(selected==world_idx)
                    counts["known_wrong"]+=int(selected is not None
                                               and selected!=world_idx)
                    counts["known_unresolved"]+=int(selected is None)
                else:
                    counts["unknown_falsified"]+=int(
                        len(result["compatible_slots"])==0)
                    counts["unknown_false_match"]+=int(selected is not None)
                    counts["unknown_ambiguous"]+=int(
                        len(result["compatible_slots"])>1)
                if (result["source_identity_authenticated"]
                        or result["native_accepted"]
                        or result["scientific_pass"]
                        or result["safe_to_activate_accepted_model"]
                        or result["write_to_accepted_model"]):
                    raise AssertionError("CUE02_UNSUPPORTED_SOURCE_PROMOTION")
                if budget<32 and result["full_domain_observed"]:
                    raise AssertionError("CUE02_PREMATURE_FULL_DOMAIN_CERT")
                traces.append([policy,world_idx,budget,
                               list(result["compatible_slots"]),
                               result["candidate_slot"],
                               result["classification"]])
    # Constructively demonstrate nonidentifiability before the final public
    # intervention on ALL 12 retained models without reading a source world ID
    # inside the auditor: a new law can agree on 31/32 and diverge on the last.
    witness_count=0
    dense=probe_order("dense")
    for slot in range(KNOWNS):
        reference=refs[slot]
        genuine=tuple((x,a,reference.predict(x,a)["public_outcome"])
                      for x,a in dense)
        if any(y not in (0,1) for _,_,y in genuine):
            raise AssertionError("CUE02_WITNESS_SOURCE_PREDICTION_UNKNOWN")
        falsified=list(genuine)
        x,a,y=falsified[-1]
        falsified[-1]=(x,a,1-y)
        first_real=one_audit(bank,refs,genuine[:31])
        first_adversarial=one_audit(bank,refs,falsified[:31])
        if first_real!=first_adversarial:
            raise AssertionError("CUE02_UNOBSERVED_ADVERSARY_DETECTED_ILLUSION")
        if first_real["full_domain_observed"] or first_real["source_identity_authenticated"]:
            raise AssertionError("CUE02_31_PROBES_WRONGLY_CERTIFIED")
        completed=one_audit(bank,refs,genuine)
        rejected=one_audit(bank,refs,falsified)
        if (completed["candidate_slot"]!=slot
             or rejected["candidate_slot"]==slot
             or not completed["observational_equivalence_only"]
             or completed["source_identity_authenticated"]):
            raise AssertionError("CUE02_ADVERSARIAL_FINAL_PROBE_DISCRIMINATION_FAILED")
        witness_count+=1
    full=all_results["dense"]["32"]
    gate={
      "known_worlds_complete_12_of_12":full["known_correct"]==12,
      "unknown_nonlinear_complete_4_of_4_rejected":
        full["unknown_falsified"]==4 and full["unknown_false_match"]==0,
      "no_wrong_old_world":all(
        all_results[p][str(b)]["known_wrong"]==0
        for p in POLICIES for b in BUDGET_SWEEP),
      "all_symbolic_decisions_equal":True,
      "bank_source_sha_unchanged":bank.checkpoint()==raw,
      "all_12_unobserved_last_action_impossibility_witnesses":witness_count==12,
      "no_31_action_authenticity_certificates":True,
      "no_native_accepted_or_scientific_firstuse":True,
    }
    return {
      "schema":"yggdrasil.cue02.finite-public-action-audit-result.v1",
      "classification":("ENGINEERING_DEV_PASS_SCIENCE_UNVERIFIED_AND_UNBOUNDED_IDENTITY_UNPROVABLE"
                        if all(gate.values()) else "ENGINEERING_DEV_NO_GO_NO_SCIENCE"),
      "fixture_only":True,"independent_scientific_first_use":0,
      "known_source_worlds":12,"nonresident_nonlinear_worlds":4,
      "public_actions_per_source_at_max":32,
      "budget_sweep_high_first":list(BUDGET_SWEEP),
      "per_policy":all_results,
      "strong_symbolic_exact_decisions":True,
      "complete_31_of_32_indistinguishable_witnesses":witness_count,
      "source_identity_authenticity_even_at_32":"NOT_PROVEN_BY_OUTPUT_EQUIVALENCE",
      "full_native_bank_checkpoint_sha256":bank.checkpoint_sha256,
      "full_native_bank_checkpoint_bytes":bank.checkpoint_bytes,
      "original_source_public_sha256":public_source_sha,
      "trace_sha256":digest(canonical(traces)),
      "frozen_gates":gate,
      "accepted_main_changed":False,
      "elapsed_seconds":round(time.perf_counter()-start,6),
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dev",action="store_true")
    parser.add_argument("--primary",action="store_true")
    args=parser.parse_args()
    if args.primary:parser.error("CUE02 SCIENTIFIC FIRST USE DISARMED")
    if not args.source_dev:parser.error("Only --source-dev is permitted")
    print("CUE02_DEV="+json.dumps(evaluate(),sort_keys=True))


if __name__=="__main__":
    main()

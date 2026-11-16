"""FKP-23 single prospective TRAIN-only physical prior-repair experiment.

NO access to any protected source cohort. New source-public prior support and
later contradictory updates are physically observed ONCE and passed equally
to every method. Each evaluation arm/world independently applies 12 base
interventions, 3 online selected queries, and 1 PREOUTCOME scored query.
The score never trains. Source world IDs are NOT given to learning policies.

Full per-world source-action/outcome SHA evidence must be uploaded BEFORE
any downstream independent scoring audit, even on a later audit failure.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import random
import sys
import time

sys.path.append(str(Path(__file__).resolve().parents[1]/"FKP-21"))
import rule_learning as gf2

import prior_repair as memory
import public_repair_source as world

FIRST_PREREG="53185e1e0df4ecb7ce45b57379ded7d387b63a16"
ARMS=memory.MODES


def _packed(value):
    return json.dumps(value,sort_keys=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def _digest(value):
    return sha256(_packed(value)).hexdigest()


def _public_bit(steps):
    return gf2._actual(steps)[1:]


def _base(seed,arm):
    mode=("INDEPENDENT_GF2_ELIMINATION" if
          arm=="EXACT_BAYES_ALL_HISTORY" else "INNOVATION_GF2")
    model=gf2.PublicRuleArm(mode)
    earned=[]
    for i,x in enumerate(world.BASE_INPUTS):
        physical=world.physical_action_episode(seed,x)
        bit,receipt=_public_bit(physical)
        model.observe_train(physical,event_id=i)
        earned.append([x,bit,receipt])
    model.freeze()
    if model.observations!=12:
        raise AssertionError("FKP23_BASE_NOT_FITTED_ON_REAL_OUTCOMES")
    return model,earned


def _support_signature(seed):
    model,base=_base(seed,"SPARSE_CONTRADICTION_REPAIR")
    evidence=[]
    for i,x in enumerate(world.RESIDUAL_INPUTS):
        predicted=model.predict_first(x)
        bit,receipt=_public_bit(world.physical_action_episode(seed,x))
        evidence.append([i,x,predicted,bit,bit^predicted,receipt])
    signature=sum(row[4]<<row[0] for row in evidence)
    # Ledger receipt includes full physical public action consequences.
    return signature,_digest({"base":base,"physical_residuals":evidence}),{
        "source_baseline_sha256":_digest(base),
        "source_residual_proofs_sha256":_digest(evidence),
        "physically_observed_signature":signature
    }


def _same_public_population():
    memory_by_arm={mode:memory.PhysicalPriorRepair(mode) for mode in ARMS}
    evidence=[]
    novel_observed=[]
    for stage,seed_group in (("support",world.SUPPORT),("update",world.UPDATE)):
        for seed in seed_group:
            sig,receipt,proof=_support_signature(seed)
            for model in memory_by_arm.values():
                model.observe_public_world(stage,sig,receipt)
            evidence.append({"stage":stage,"world_evidence":proof,
                             "physical_episode_count":16})
            if stage=="update" and sig not in set(
                    s for s,r in memory_by_arm[ARMS[0]]._support):
                novel_observed.append(sig)
    checkpoint={}
    for name,model in memory_by_arm.items():
        model.freeze()
        cold=memory.PhysicalPriorRepair.restore(model.checkpoint())
        if cold.state_sha()!=model.state_sha() or cold.checkpoint()!=model.checkpoint():
            raise AssertionError("FKP23_COLD_PAST_RELATION_LOSS")
        checkpoint[name]=model.checkpoint()
    # Important: no private source law or cohort flag sent to the policies.
    if len({model.support_count for model in memory_by_arm.values()})!=1 or (
        len({model.update_count for model in memory_by_arm.values()})!=1):
        raise AssertionError("FKP23_ARMS_MISMATCHED_PRIOR_INFORMATION")
    return checkpoint,evidence,tuple(sorted(set(novel_observed)))


def _physical_eval(seed,arm,checkpoint):
    model=memory.PhysicalPriorRepair.restore(checkpoint)
    prior_sha=model.state_sha()
    began=time.perf_counter()
    base,base_rows=_base(seed,arm)
    base_sha=base.state_receipt()
    fit_wall=time.perf_counter()-began
    selected=[]
    began=time.perf_counter()
    for n in range(3):
        index=model.choose_physical_query()
        x=world.RESIDUAL_INPUTS[index]
        predicted_base=base.predict_first(x)
        actual_bit,trace=_public_bit(world.physical_action_episode(seed,x))
        model.observe_selected_consequence(index,actual_bit^predicted_base,trace)
        selected.append([index,x,predicted_base,actual_bit,
                         actual_bit^predicted_base,trace])
    if len({record[0] for record in selected})!=3:
        raise AssertionError("FKP23_DUPLICATED_PHYSICAL_QUERY")
    checkpoint_after_three=model.checkpoint()
    resumed=memory.PhysicalPriorRepair.restore(checkpoint_after_three)
    if resumed.state_sha()!=model.state_sha() or (
            resumed.checkpoint()!=checkpoint_after_three):
        raise AssertionError("FKP23_COLD_INTERVENTION_REPLAY_FAILED")
    remaining=[i for i in range(4) if i not in resumed.queried]
    if len(remaining)!=1:
        raise AssertionError("FKP23_UNQUERIED_SOURCE_NOT_UNIQUE")
    index=remaining[0]
    x=world.RESIDUAL_INPUTS[index]
    prediction=base.predict_first(x)^resumed.predict_last_unqueried(index)
    before_score_sha=resumed.state_sha()
    observed,physical_sha=_public_bit(world.physical_action_episode(seed,x))
    if resumed.state_sha()!=before_score_sha or (
        base.state_receipt()!=base_sha):
        raise AssertionError("FKP23_OUTCOME_WAS_USED_TO_UPDATE_FROZEN_MODEL")
    scored=[index,x,prediction,observed,int(prediction==observed),physical_sha]
    return {
        "physical_base_sha256":_digest(base_rows),
        "base_public_model_sha256":base_sha,
        "original_learned_prior_sha256":prior_sha,
        "chosen_physical_probe_events":selected,
        "scored_preaction_source_event":scored,
        "correct_score":int(prediction==observed),
        "source_consequence_not_used_for_update":True,
        "distinct_posterior_signatures":resumed.distinct_posterior_relations,
        "support_examples_after_3_probes":resumed.supporting_example_count,
        "cold_after_three_sha256":before_score_sha,
        "checkpoint_sha256":sha256(checkpoint_after_three).hexdigest(),
        "max_logical_learned_bytes":base.logical_learned_bytes+resumed.learned_logical_bytes,
        "fit_wall_seconds":fit_wall,
        "online_intervention_wall_seconds":time.perf_counter()-began
    }


def _resample(worlds):
    if len(worlds)!=16:
        raise ValueError("FKP23_WORLD_COUNT_FOR_BOOTSTRAP")
    randomizer=random.Random(2323)
    strong=[]
    weak=[]
    for _ in range(10000):
        subset=[worlds[randomizer.randrange(16)] for n in range(16)]
        strong.append(sum(w["arms"]["SPARSE_CONTRADICTION_REPAIR"]["correct_score"]-
                          w["arms"]["EXACT_BAYES_ALL_HISTORY"]["correct_score"]
                          for w in subset))
        weak.append(sum(w["arms"]["SPARSE_CONTRADICTION_REPAIR"]["correct_score"]-
                        w["arms"]["FROZEN_OLD_PRIOR"]["correct_score"]
                        for w in subset))
    strong.sort()
    weak.sort()
    return {
        "draws":10000,"seed":2323,
        "candidate_minus_exact_bayes_95_interval":[strong[249],strong[9749]],
        "candidate_minus_frozen_old_95_interval":[weak[249],weak[9749]],
        "source_safe_train_descriptive_only":True,
        "scientific_pass":False
    }


def run():
    sha=os.environ.get("FKP23_SOURCE_SHA","")
    if len(sha)!=40 or any(x not in "0123456789abcdef" for x in sha):
        raise ValueError("FKP23_CANDIDATE_SHA_NOT_PINNED")
    started=time.perf_counter()
    cpu_started=time.process_time()
    checkpoints,prior_receipts,novel=_same_public_population()
    prior_sha={arm:sha256(checkpoints[arm]).hexdigest() for arm in ARMS}
    per_world=[]
    for cohort,seeds in (("shift",world.SHIFT_EVAL),
                         ("return",world.RETURN_EVAL)):
        for ordinal,seed in enumerate(seeds):
            arms={name:_physical_eval(seed,name,checkpoints[name])
                  for name in ARMS}
            if len({v["physical_base_sha256"] for v in arms.values()})!=1:
                raise AssertionError("FKP23_INEQUAL_REAL_BASE_INTERVENTIONS")
            per_world.append({"cohort":cohort,
                "world_index_within_cohort":ordinal,
                "common_public_base_sha256":arms[ARMS[0]]["physical_base_sha256"],
                "arms":arms})
    summary={}
    for mode in ARMS:
        summary[mode]={}
        for cohort in ("shift","return"):
            vals=[w["arms"][mode] for w in per_world if w["cohort"]==cohort]
            summary[mode][cohort]={
                "first_unqueried_correct":sum(v["correct_score"] for v in vals),
                "total_first_unqueried":len(vals),
                "inconsistent_posterior_worlds":sum(
                    v["distinct_posterior_signatures"]==0 for v in vals),
                "max_learned_logical_bytes":max(v["max_logical_learned_bytes"]
                                               for v in vals),
                "fit_wall_seconds":sum(v["fit_wall_seconds"] for v in vals),
                "online_wall_seconds":sum(v["online_intervention_wall_seconds"]
                                          for v in vals)
            }
    for method in ARMS:
        if any(summary[method][cohort]["total_first_unqueried"]!=16
               for cohort in ("shift","return")):
            raise AssertionError("FKP23_SOURCE_EVAL_COHORT_INCOMPLETE")
    return {
        "schema":"fkp23.cold-contradiction-prior-repair-source.v1",
        "classification":"SOURCE_SAFE_TRAIN_PRIOR_REPAIR_DEVELOPMENT_ONLY",
        "exact_source_sha":sha,
        "prereg_first_commit":FIRST_PREREG,
        "support_worlds":len(world.SUPPORT),
        "adaptation_worlds":len(world.UPDATE),
        "shift_eval_worlds":len(world.SHIFT_EVAL),
        "return_eval_worlds":len(world.RETURN_EVAL),
        "physical_action_count":(len(world.SUPPORT)+len(world.UPDATE))*16*4+
            (len(world.SHIFT_EVAL)+len(world.RETURN_EVAL))*len(ARMS)*16*4,
        "observed_prior_world_custody":prior_receipts,
        "novel_signatures_detected_from_public_feedback":list(novel),
        "prior_checkpoint_sha256_by_arm":prior_sha,
        "per_world":per_world,
        "summary":summary,
        "paired_bootstrap_by_cohort":{
            "shift":_resample([w for w in per_world if w["cohort"]=="shift"]),
            "return":_resample([w for w in per_world if w["cohort"]=="return"])},
        "whole_process_wall_seconds":time.perf_counter()-started,
        "whole_process_cpu_seconds":time.process_time()-cpu_started,
        "original_protected_first_use":False,
        "native_main_modified":False,
        "scientific_pass":False
    }


def main():
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--output-json",required=True)
    args=a.parse_args()
    receipt=run()
    path=Path(args.output_json)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(receipt,sort_keys=True,allow_nan=False,
                               indent=2)+"\n",encoding="utf-8")
    report={"schema":receipt["schema"],
            "classification":receipt["classification"],
            "exact_source_sha":receipt["exact_source_sha"],
            "physical_action_count":receipt["physical_action_count"],
            "novel_signatures_detected_from_public_feedback":
                receipt["novel_signatures_detected_from_public_feedback"],
            "summary":receipt["summary"],
            "paired_bootstrap_by_cohort":receipt["paired_bootstrap_by_cohort"],
            "whole_process_wall_seconds":receipt["whole_process_wall_seconds"],
            "original_protected_first_use":False,
            "native_main_modified":False,"scientific_pass":False}
    print("FKP23_ORIGINAL_PUBLIC_PRIOR_REPAIR="+json.dumps(
        report,sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()

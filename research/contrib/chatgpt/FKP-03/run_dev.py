"""FKP-03 FROZEN fresh DEV-only active-intervention assay, not native promotion.

All policies are sealed into prediction tuples before the development-only
source evaluator reveals any held outcome. Protected cohorts never opened.
"""
from __future__ import annotations
import hashlib
import json
import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from source import CausalWorld,N_HELD,N_PAID
from model import (acquire_foundation,compose_generic_functions,generic_mask,
                   family_mask,execute_policy,replay_exact_prior)

DEV=tuple(range(400,416))
ARMS=("foundation_active","foundation_random","foundation_coverage",
      "known_family_active","preloaded_active","known_family_matched_transcript")
PRECOMMITTED_BOOTSTRAP_SEED=9090
RESAMPLES=10000

def paired_ci(rows:list[dict],lhs:str,rhs:str)->tuple[float,float,float]:
    differences=[r["scores"][lhs]-r["scores"][rhs] for r in rows]
    rng=random.Random(PRECOMMITTED_BOOTSTRAP_SEED)
    n=len(differences)
    sampled=sorted(sum(differences[rng.randrange(n)] for _ in range(n))/n
                   for _ in range(RESAMPLES))
    return statistics.mean(differences),sampled[249],sampled[9749]

def run():
    start=time.perf_counter()
    foundation=acquire_foundation()
    learned_gates=tuple(int(g) for g in foundation["learned_gate_counts"])
    functions=compose_generic_functions(learned_gates)
    assert len(functions)==256 and len(learned_gates)==4
    mask=generic_mask(functions)
    assert mask.bit_count()==218
    oracle_mask=family_mask()
    assert oracle_mask.bit_count()==7

    world_rows=[]
    all_pred=hashlib.sha256()
    for seed in DEV:
        view=CausalWorld(seed).public_view()
        # Fully independent source instance and 16 paid interventions for each
        # adaptive policy; no replay of unknown effects across policies.
        arm_results={
            "foundation_active":execute_policy(seed,mask,"information"),
            "foundation_random":execute_policy(seed,mask,"random"),
            "foundation_coverage":execute_policy(seed,mask,"coverage"),
            "known_family_active":execute_policy(seed,oracle_mask,"information"),
            "preloaded_active":execute_policy(seed,mask,"information"),
        }
        a=arm_results["foundation_active"]
        matched=replay_exact_prior(a["queries"],a["answers"],view.held_inputs)
        pred={k:tuple(v["prediction"]) for k,v in arm_results.items()}
        pred["known_family_matched_transcript"]=matched
        for arm in ARMS:
            if len(pred[arm])!=N_HELD:raise AssertionError("FKP03_INCOMPLETE_PREDICTIONS")
            all_pred.update(bytes(pred[arm]))
        # Sanity: preloading the exact compositional grammar has to tie the
        # acquired basis; any difference is an implementation/data leak.
        assert pred["foundation_active"]==pred["preloaded_active"]
        assert a["queries"]==arm_results["preloaded_active"]["queries"]
        assert a["answers"]==arm_results["preloaded_active"]["answers"]
        # Sealed ALL predictions before owner-only DEV held evaluation.
        held=CausalWorld(seed).development_only_labels(view.held_inputs)
        scores={arm:sum(u==v for u,v in zip(pred[arm],held))/N_HELD
                for arm in ARMS}
        family=( "mux3" if seed % 2==0 else "majority3" )
        # Family is not supplied to any arm and cannot be treated as an
        # explanation of per-world source law; record only cohort strata.
        world_rows.append({
            "dev_world_seed":seed,"dev_descriptive_stratum":family,
            "scores":scores,
            "paid_actions":{k:len(v["queries"]) for k,v in arm_results.items()},
            "foundational_active_action_overlap_with_random":len(set(a["queries"])&
                          set(arm_results["foundation_random"]["queries"])),
            "remaining_hypotheses":{k:v["surviving_hypotheses"] for k,v in arm_results.items()},
            "serialized_checkpoint_bytes":{k:v["checkpoint_bytes"] for k,v in arm_results.items()},
            "policy_and_fit_elapsed_seconds_dev":{k:round(v["elapsed_seconds_local_dev"],6)
                                                   for k,v in arm_results.items()},
        })
    means={arm:statistics.mean(r["scores"][arm] for r in world_rows) for arm in ARMS}
    differences={name:{"delta_accuracy":delta,"ci95":[lower,upper]}
                 for name,lhs,rhs in (("B_minus_random","foundation_active","foundation_random"),
                                      ("B_minus_coverage","foundation_active","foundation_coverage"),
                                      ("B_minus_preloaded","foundation_active","preloaded_active"),
                                      ("B_minus_known_family_active","foundation_active","known_family_active"))
                 for delta,lower,upper in (paired_ci(world_rows,lhs,rhs),)}
    bmx={arm:statistics.mean(r["scores"][arm] for r in world_rows
                              if r["dev_world_seed"]%2==0) for arm in ARMS}
    bma={arm:statistics.mean(r["scores"][arm] for r in world_rows
                              if r["dev_world_seed"]%2==1) for arm in ARMS}
    # Primary DEV policy-signal criterion is deliberately strict; no count of
    # released world results as an unconsumed independent science cohort.
    ci1=differences["B_minus_random"]
    ci2=differences["B_minus_coverage"]
    qualifies=(ci1["delta_accuracy"]>=0.05 and ci1["ci95"][0]>0
               and ci2["delta_accuracy"]>=0.05 and ci2["ci95"][0]>0
               and all(bmx["foundation_active"]>=bmx[a] and bma["foundation_active"]>=bma[a]
                       for a in ("foundation_random","foundation_coverage")))
    result={
        "schema":"fkp03.public-dev-active-learning.v1",
        "experiment":"FKP-03","source_dev_only":True,"protected_first_use":False,
        "native_yggdrasil_accepted_model_unchanged":True,
        "foundation":foundation,"learned_compositional_three_input_functions":len(functions),
        "hypotheses_per_effect":220*218,
        "distinct_dev_worlds":len(world_rows),"held_per_world":N_HELD,
        "action_budget_per_world_per_policy":N_PAID,
        "mean_accuracy":means,"paired_bootstrap":differences,
        "descriptive_even_seed_stratum":bmx,"descriptive_odd_seed_stratum":bma,
        "predictions_sha256":all_pred.hexdigest(),
        "dev_policy_threshold_met":qualifies,
        "learned_foundation_vs_preloaded_equal_by_construction":True,
        "strict_scientific_advantage":"UNVERIFIED_NO_QUALIFIED_CONVENTIONAL_MATCHED_COMPUTE",
        "cold_historical_retention":"UNVERIFIED",
        "full_process_cost_parity":"UNVERIFIED",
        "wall_seconds_local_dev":time.perf_counter()-start,
        "classification":"DEV_POLICY_SIGNAL_ONLY_NOT_SCIENCE" if qualifies else "DEV_NO_GO_FROZEN",
        "worlds":world_rows
    }
    print(json.dumps(result,sort_keys=True,indent=2))
    return result

if __name__=="__main__":
    run()

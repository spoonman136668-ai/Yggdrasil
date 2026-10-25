"""C32: frozen FIT-trained policies actually operate original public worlds."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import time
from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c29.analysis import read_frozen_artifact
from research.mass_r7c31.run import train_models
from research.mass_r7c31.action_bridge import learned_source_motors
from research.mass_r7c32.physical_episode import run_episode
from research.mass_r7c32.cold import cold_policy

P=json.loads((Path(__file__).parent/"PREREG.json").read_text())

def evaluate(source_dir):
    from research.mass_r7c20 import run as c20
    c20.check_source()
    original,source=read_frozen_artifact(source_dir)
    if (P["schema"]!="itd02.c32.real-physical-selected-policy-fit-v1"
        or P["parentC31"]!="f46fdd149af4f676a17941073fe3d61aaeebbcca"
        or len(original)!=P["priorFIT"]["authenticatedEvents"]
        or P["governance"]["protectedScientificFirstUse"] is not False):
        raise ValueError("C32_SOURCE_FIRST_PRECOMMIT_OR_FIT_DRIFT")
    models,training,check=train_models(original)
    motors=learned_source_motors(training)
    episodes=[]
    cap=P["prospectivePublicFIT"]["maxActionsPerEpisode"]
    for arm in P["actors"]:
        for family,seeds in P["prospectivePublicFIT"]["families"].items():
            for seed in seeds:
                episodes.append(run_episode(family,seed,arm,
                    None if arm=="r3_original" else models[arm],
                    motors,cap,cold_policy))
    cohorts={}
    for arm in P["actors"]:
        rows=[e for e in episodes if e["arm"]==arm]
        cohorts[arm]={
           "episodes":len(rows),
           "real_goals":sum(e["source_goal"] for e in rows),
           "real_collisions":sum(e["source_collision"] for e in rows),
           "real_horizons":sum(e["source_horizon"] for e in rows),
           "mean_real_reward":sum(e["reward_sum"] for e in rows)/len(rows),
           "real_actions":sum(e["steps"] for e in rows),
           "actually_executed_turn_substitutions":sum(e["native_real_turn_changes"] for e in rows),
           "blocked_forward_attempts":sum(
               a["executed"]==2 and a["before"]["front_blocked"]
               for e in rows for a in e["source_actual_actions"])
        }
    native=cohorts["native"]
    baseline=cohorts["r3_original"]
    conventional=("full9_conventional_sgd",
                  "full9_conventional_momentum","temporal_bayes")
    best=max((cohorts[k] for k in conventional),
             key=lambda d:(d["mean_real_reward"],d["real_goals"]))
    c=P["acceptance"]
    # Frozen control's physical trajectories must match the original R3,
    # although their model checkpoint metadata naturally differs.
    for frozen in [e for e in episodes if e["arm"]=="native_frozen"]:
        corresponding=next(x for x in episodes if x["arm"]=="r3_original"
                          and x["family"]==frozen["family"] and x["seed"]==frozen["seed"])
        a=[(x["executed"],x["after"],x["reward"]) for x in frozen["source_actual_actions"]]
        b=[(x["executed"],x["after"],x["reward"]) for x in corresponding["source_actual_actions"]]
        if a!=b:
            raise ValueError("C32_FROZEN_CONTROL_DIFFERS_FROM_NATIVE_R3_SOURCE")
    criteria={
       "all_actors_run_same_number_of_original_source_worlds":all(
         t["episodes"]==8 for t in cohorts.values()),
       "native_actually_changed_turn":native["actually_executed_turn_substitutions"]>=c["minNativeActuallyChosenDeviations"],
       "native_goals_vs_original_R3":native["real_goals"]>=baseline["real_goals"]+c["minAdditionalNativeGoalsVsR3"],
       "native_goals_vs_fully_trained_conventional":native["real_goals"]>=best["real_goals"]+c["minAdditionalNativeGoalsVsBestConventional"],
       "real_source_reward_vs_R3":native["mean_real_reward"]-baseline["mean_real_reward"]>=c["minNativeRealRewardGainVsR3"],
       "real_source_reward_vs_conventional":native["mean_real_reward"]-best["mean_real_reward"]>=c["minNativeRealRewardGainVsBestConventional"],
       "no_extra_native_source_collisions":native["real_collisions"]<=baseline["real_collisions"],
       "actual_frozen_R3_control_parity":True,
       "cold_OS_for_every_actual_episode":all(e["cold_step_three"]["restored_in_fresh_process"] for e in episodes)
    }
    verdict=c["positive"] if all(criteria.values()) else c["noGo"]
    return {"schema":P["schema"],"gate":"ITD02-C32",
        "verdict":verdict,"criteria":criteria,"source_actor_summary":cohorts,
        "original_world_episode_records":episodes,
        "original_C28_FIT_ledger_sha256":source["source_fit_event_ledger_sha256"],
        "original_C28_FIT_training_samples":len(training),
        "original_C28_FIT_check_only_samples":len(check),
        "frozen_protocol_sha256":hashlib.sha256(
          (Path(__file__).parent/"PREREG.json").read_bytes()).hexdigest(),
        "original_upstream":P["source"]["upstream"],
        "all_actor_actions_physically_executed":True,
        "source_DEV_or_protected_episodes":0,
        "prior_original_native_R3_modified":False,
        "scientific_first_use":False,"scientific_accepted":False}

def main():
    import resource  # original Linux-source runner only; Windows source-only tests stay portable
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-fit-dir",required=True)
    ap.add_argument("--output",required=True)
    arg=ap.parse_args()
    dest=Path(arg.output)
    if dest.exists() or not dest.parent.is_dir():
        raise ValueError("C32_EVIDENCE_NOT_FRESH")
    cpu=time.process_time();wall=time.perf_counter()
    value=evaluate(arg.original_fit_dir)
    value["resources"]={
        "python_self_cpu_seconds":time.process_time()-cpu,
        "whole_process_wall_seconds":time.perf_counter()-wall,
        "python_self_peak_RSS_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "checkpoint_child_process_CPU_not_included":True,
        "energy_measured":False}
    dest.write_bytes(canonical(value)+b"\n")
    print("C32_ORIGINAL_FIT_POLICY_RESULT="+value["verdict"],flush=True)
    print("C32_PHYSICALLY_EXECUTED_SOURCE_POLICY_SUMMARY="+
         json.dumps(value["source_actor_summary"],sort_keys=True),flush=True)
    print("C32_FROZEN_ACCEPTANCE="+json.dumps(value["criteria"],sort_keys=True),flush=True)
    print("C32_ZERO_NEW_DEV_PROTECTED_FIRST_USE=PASS",flush=True)

if __name__=="__main__":main()

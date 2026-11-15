"""AAI-11G prospective feasibility benchmark: reachable-goal recovery + reward.

NO candidate learner and NO primary scientific first use. Independently
requalifies the original eleven conventional public-data models and reports
a posterior-only diagnostic without changing models, laws or contexts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
for folder in ("AAI-11P","AAI-11A","AAI-11D","AAI-11F"):
    sys.path.insert(0,str(HERE.parent/folder))
import world,controls,admission
import learner as original_learner
import fixture as original_fixture
import calibration,dev as posterior_dev
import audit as ceiling

POSTERIOR="posterior_planner"
MATCHED=original_learner.MATCHED
REWARD_MARGIN=.08
GOAL_RECOVERY_MARGIN=.05
MAX_UNREACHABLE_REGRET_EXCESS=.03
MAX_FAMILIAR_RETURN_DROP=.03
MAX_COST_RATIO=2.
MIN_REWARD_HEADROOM=.25
MIN_RECOVERY_HEADROOM=.10
EXPECTED_ORIGINAL_BEST="graph_recent8"
EXPECTED_ORIGINAL_BEST_REWARD=2.134027778
EXPECTED_POSTERIOR_MEAN=2.189756944
EXPECTED_POSTERIOR_GOAL=.40625


def digest(item):
    return hashlib.sha256(controls.canonical(item).encode("utf8")).hexdigest()


def mean(numbers):
    if not numbers:
        raise ValueError("empty metric group")
    return sum(numbers)/len(numbers)


def best_method(means,names):
    """Stable original matched-method order resolves exact performance ties."""
    return max(names,key=lambda n:means[n])


def finalize_method(episodes,reachable_total,unreachable_total):
    """An honest oracle-relative metric never discounts reward on impossible goals."""
    if not episodes:
        raise ValueError("empty episodes")
    reachable=[e for e in episodes if e["oracle_reachable"]]
    unreachable=[e for e in episodes if not e["oracle_reachable"]]
    if len(reachable)!=reachable_total or len(unreachable)!=unreachable_total:
        raise AssertionError("oracle reachable/unreachable composition changed")
    if any(e["goal_correct"] and not e["oracle_reachable"] for e in episodes):
        raise AssertionError("model has impossible exact-goal achievement")
    if any(e["reward"]>e["oracle_reward"]+1e-9 for e in episodes):
        raise AssertionError("model outperformed exact lawful oracle")
    hits=sum(e["goal_correct"] for e in reachable)
    return {
        "reward":round(mean([e["reward"] for e in episodes]),9),
        "raw_exact_three_goal_fraction":round(sum(e["goal_correct"] for e in episodes)/len(episodes),9),
        "reachable_goals_hit":hits,
        "reachable_goals_total":reachable_total,
        "oracle_normalized_reachable_goal_recovery":round(hits/reachable_total,9),
        "reachable_regret":round(mean([e["oracle_reward"]-e["reward"] for e in reachable]),9),
        "unreachable_regret":round(mean([e["oracle_reward"]-e["reward"] for e in unreachable]),9),
        "mean_real_actions":round(mean([e["actions"] for e in episodes]),9),
        "per_law_reachable_recovery":{
            law:round(sum(e["goal_correct"] for e in reachable if e["law"]==law)/
                      sum(e["law"]==law for e in reachable),9)
            for law in world.TRANSFER
        },
        "per_law_unreachable_regret":{
            law:round(mean([e["oracle_reward"]-e["reward"]
                            for e in unreachable if e["law"]==law]),9)
            for law in world.TRANSFER
        },
    }


def episode_reference(name,snapshot,law,x,g):
    if name==POSTERIOR:
        reward,hit,actions=posterior_dev.episode(name,snapshot,law,x,g)
    else:
        reward,hit,actions=original_fixture.episode(name,snapshot,law,x,g)
    if type(hit) is not int or hit not in (0,1) or len(actions)>2:
        raise AssertionError("invalid original public action budget or goal observation")
    return reward,hit,actions


def challenge_reference(name,postB,law,key,budget):
    if name==POSTERIOR:
        return posterior_dev.challenge(name,postB,law,key,budget)
    return original_fixture.challenge(name,postB,law,key,budget)


def score_familiar(name,training,key):
    scores=[]
    for law in world.TRAIN:
        for budget in (2,4):
            frozen=challenge_reference(name,training,law,key,budget)
            for x,g in admission.contexts(key,law,12):
                scores.append(episode_reference(name,frozen,law,x,g)[0])
    return scores


def run_benchmark():
    prereg=json.loads((HERE/"prereg.json").read_text("utf8"))
    if (prereg["id"]!="AAI-11G" or
        prereg["future_scientific_acceptance_contract"]["consumed"]!=0 or
        prereg["authority"]["no_science_first_use"] is not True):
        raise PermissionError("AAI11G SCIENTIFIC FIRST USE DISARMED")
    if len(MATCHED)!=11 or len(set(MATCHED))!=11 or MATCHED!=(
        *controls.METHODS,"graph_recent8","graph_recent16","graph_all"):
        raise AssertionError("unfrozen eleven strongest eligible controls")
    if (REWARD_MARGIN,GOAL_RECOVERY_MARGIN,MIN_RECOVERY_HEADROOM)!=(
        prereg["future_candidate_dev_gates_frozen_now"]["reward_margin_over_strongest_conventional"],
        prereg["future_candidate_dev_gates_frozen_now"]["normalized_reachable_goal_recovery_margin_over_best_of_all_11_controls"],
        prereg["future_candidate_dev_gates_frozen_now"]["oracle_reachable_goal_recovery_headroom_over_best_conventional_min"]):
        raise AssertionError("post-prereg threshold drift")
    audit=ceiling.mechanical_audit()
    if (audit["classification"]!="BENCHMARK_GOAL_GATE_IMPOSSIBLE" or
        audit["exact_goal_attainable_episodes"]!=144 or
        audit["total_original_evaluation_episodes"]!=288):
        raise AssertionError("frozen AAI11F exact goal oracle ceiling changed")

    names=(*MATCHED,POSTERIOR)
    all_transfer={name:[] for name in names}
    all_familiar={name:[] for name in names}
    elapsed={name:0. for name in names}
    trace=[]
    source_receipts=[]
    counts={"reachable":0,"unreachable":0}
    start=time.perf_counter()
    for key in world.FIXTURES:
        saved,evidence,train_cost=original_fixture.common_training(key,names=MATCHED)
        if len(evidence)!=64 or any(set(row)!=world.PUBLIC_KEYS for row in evidence):
            raise AssertionError("unmatched common public training examples")
        posterior=calibration.PosteriorCausalModel(POSTERIOR)
        pstart=time.perf_counter()
        for row in evidence:
            posterior.observe(world.copy_public(row))
        saved[POSTERIOR]=calibration.checkpoint(posterior)
        elapsed[POSTERIOR]+=time.perf_counter()-pstart
        for name in MATCHED:
            elapsed[name]+=train_cost[name]
        if posterior.rows!=original_learner.restore("graph_recent8",saved["graph_recent8"]).rows:
            raise AssertionError("posterior observed different public rows to strongest baseline")
        for name in names:
            cold=(calibration.checkpoint(calibration.restore(name,saved[name])) if name==POSTERIOR
                  else original_learner.checkpoint(name,original_learner.restore(name,saved[name])))
            if cold!=saved[name]:
                raise AssertionError("cold A/B source state changed")
        source_receipts.append([key,*[digest(saved[name]) for name in names]])

        for law in world.TRANSFER:
            contexts=admission.contexts(key,law,12)
            oracle_meta=[]
            for x,g in contexts:
                possible=int(tuple(g) in ceiling.closure(law,x)[1])
                independent=ceiling.sequences(law,x,g)
                if possible!=independent["attainable"]:
                    raise AssertionError("oracle reachability solvers disagreed")
                oracle_reward=world.exact_oracle(law,x,g)
                if abs(oracle_reward-independent["reward_best"])>1e-10:
                    raise AssertionError("original optimal reward drift")
                oracle_meta.append((possible,oracle_reward))
            for budget in (2,4):
                counts["reachable"]+=sum(i[0] for i in oracle_meta)
                counts["unreachable"]+=sum(not i[0] for i in oracle_meta)
                for name in names:
                    tick=time.perf_counter()
                    frozen=challenge_reference(name,saved[name],law,key,budget)
                    for (x,g),(possible,oracle_reward) in zip(contexts,oracle_meta):
                        reward,hit,actions=episode_reference(name,frozen,law,x,g)
                        item={
                            "law":law,"oracle_reachable":possible,
                            "oracle_reward":oracle_reward,"reward":reward,
                            "goal_correct":hit,"actions":len(actions)
                        }
                        all_transfer[name].append(item)
                        trace.append([key,law,budget,name,list(x),list(g),
                                      int(possible),round(reward,9),int(hit),list(actions)])
                    elapsed[name]+=time.perf_counter()-tick
        for name in names:
            tick=time.perf_counter()
            all_familiar[name].extend(score_familiar(name,saved[name],key))
            elapsed[name]+=time.perf_counter()-tick
            if name==POSTERIOR:
                original=calibration.checkpoint(calibration.restore(name,saved[name]))
            else:
                original=original_learner.checkpoint(name,original_learner.restore(name,saved[name]))
            if original!=saved[name]:
                raise AssertionError("retention episodes changed frozen original training")
    if counts!={"reachable":144,"unreachable":144}:
        raise AssertionError("original oracle ceiling count drift")
    metrics={name:finalize_method(all_transfer[name],144,144) for name in names}
    familiar={name:round(mean(all_familiar[name]),9) for name in names}
    if any(len(all_transfer[name])!=288 or len(all_familiar[name])!=144 for name in names):
        raise AssertionError("unfrozen model evaluation episode count")
    rewards={name:metrics[name]["reward"] for name in MATCHED}
    recovery={name:metrics[name]["oracle_normalized_reachable_goal_recovery"] for name in MATCHED}
    strongest=best_method(rewards,MATCHED)
    best_recovery=best_method(recovery,MATCHED)
    fastest=min(MATCHED,key=lambda name:elapsed[name])
    best_reward=rewards[strongest]
    best_conditional=recovery[best_recovery]
    reward_headroom=audit["original_exact_two_action_oracle_mean_reward"]-best_reward
    goal_headroom=1-best_conditional
    checks={
        "oracle_exact_goal_ceiling_144_of_288":counts=={"reachable":144,"unreachable":144},
        "best_reward_control_exact_replay":strongest==EXPECTED_ORIGINAL_BEST and abs(best_reward-EXPECTED_ORIGINAL_BEST_REWARD)<1e-6,
        "posterior_original_reward_exact_replay":abs(metrics[POSTERIOR]["reward"]-EXPECTED_POSTERIOR_MEAN)<1e-6,
        "posterior_original_raw_goal_exact_replay":abs(metrics[POSTERIOR]["raw_exact_three_goal_fraction"]-EXPECTED_POSTERIOR_GOAL)<1e-6,
        "oracle_reward_headroom_ge_025":reward_headroom>=MIN_REWARD_HEADROOM,
        "oracle_reachable_goal_headroom_ge_010":goal_headroom>=MIN_RECOVERY_HEADROOM,
        "strongest_reward_control_familiar_ge_170":familiar[strongest]>=1.70,
        "all_11_conventional_fully_qualified":len(MATCHED)==11,
        "all_results_mechanical_only_no_science":True
    }
    status=("BENCHMARK_QUALIFIED_FOR_PROSPECTIVE_SOURCE_DEV"
            if all(checks.values()) else "BENCHMARK_NO_GO_NO_SCIENCE")
    return {
        "schema":"yggdrasil.contrib.aai11g.oracle-relative-source-evaluation.v1",
        "classification":status,"checks":checks,
        "strongest_reward_control":strongest,
        "best_conditional_success_control":best_recovery,
        "fastest_measured_conventional":fastest,
        "original_oracle_mean_reward":audit["original_exact_two_action_oracle_mean_reward"],
        "oracle_exact_goal_ceiling":.5,
        "oracle_reachable":counts["reachable"],
        "oracle_unreachable":counts["unreachable"],
        "oracle_reward_headroom":round(reward_headroom,9),
        "oracle_recovery_headroom_vs_best_control":round(goal_headroom,9),
        "original_absolute_060_gate":"INVALID_MATHEMATICALLY_IMPOSSIBLE",
        "frozen_future_candidate_gates":{
            "minimum_reward_gain_vs_best_of_11":REWARD_MARGIN,
            "minimum_reachable_goal_recovery_gain_vs_best_of_11":GOAL_RECOVERY_MARGIN,
            "max_unreachable_regret_excess":MAX_UNREACHABLE_REGRET_EXCESS,
            "max_familiar_reward_loss":MAX_FAMILIAR_RETURN_DROP,
            "max_process_ratio_to_fastest":MAX_COST_RATIO
        },
        "original_matched_controls":{name:metrics[name] for name in MATCHED},
        "posterior_only_diagnostic":metrics[POSTERIOR],
        "familiar_reward":familiar,
        "source_fixture_training_plus_cold_execution_seconds":{
            name:round(elapsed[name],6) for name in names},
        "source_trace_sha256":digest(trace),
        "training_source_receipts_sha256":digest(source_receipts),
        "per_method_transfer_episodes":288,
        "per_method_familiar_episodes":144,
        "science_cohorts_consumed":0,
        "model_changes":0,
        "first_use_disarmed":True,
        "whole_qualification_wall_seconds":round(time.perf_counter()-start,4)
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-protocol-admission",action="store_true")
    parser.add_argument("--primary",action="store_true")
    a=parser.parse_args()
    if a.primary:
        parser.error("AAI11G SCIENTIFIC FIRST USE DISARMED")
    if not a.source_protocol_admission:
        parser.error("only three frozen mechanical AAI11P fixtures admitted")
    print("AAI11G_PROTOCOL="+json.dumps(run_benchmark(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()

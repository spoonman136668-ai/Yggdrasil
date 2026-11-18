"""CKAD28 prospective held-out reward and native-memory qualification audit.

Independently reconstruct every acquired public action consequence from
the exact synthetic source and verify no hidden/counterfactual observation
entered a native learner. Then evaluate the frozen 3-arm matched metrics.
The actual source family is known to the evaluator, never to the policy.
"""
import argparse
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
import campaign
import policy
from yggdrasil.native_context_basis import canonical,digest

SEEDS=(101,202,303)
SCENARIOS=("reward_change","stationary_null")
ARMS=policy.ARMS
CHECKPOINTS=(0,32,64,96,128)


def require(ok,reason):
    if not ok:raise ValueError("CKAD28_AUDIT_"+reason)


def ratio(value):
    return [value.numerator,value.denominator]


def fraction(value):
    require(type(value) is list and len(value)==2 and
            all(type(z) is int for z in value) and value[1]>0,
            "RATIONAL_METRIC")
    return Fraction(*value)


def sha64(value):
    return type(value) is str and len(value)==64 and all(
        q in "0123456789abcdef" for q in value)


def verify_case(obj,p):
    require(obj["schema"]=="yggdrasil.ckad28.decision-relevance.case.v1"
            and obj["seed"] in SEEDS and obj["scenario"] in SCENARIOS,
            "IDENTITY")
    scenario,seed=obj["scenario"],obj["seed"]
    spec=p["scenarios"][scenario]
    source_seed=seed+spec["source_seed_offset"]
    cohort=p["source_cohort"]+"-"+scenario
    require(obj["source_seed"]==source_seed and
            obj["source_cohort"]==cohort and
            obj["parent_commit"]==p["parent_commit"] and
            obj["source_generator_sha256"]==p["original_source_sha256"] and
            obj["original_source_actions"]==obj["protected_first_use"]==
            obj["held_updates"]==0,"EXACT_SOURCE_CUSTODY")
    require(obj["scientific_pass"] is False and
            obj["accepted_native"] is False and
            obj["deployment"]=="NONE","PROMOTION_FENCE")
    require(obj["source_public_episodes_per_arm"]==128 and
            sha64(obj["parent_checkpoint_sha256"]) and
            campaign.stable(obj)==obj["stable_sha256"],
            "STABLE_SOURCE_PROOF")
    require(set(obj["source_receipts"])==set(ARMS) and
            set(obj["custody"])==set(ARMS) and
            [v["count"] for v in obj["checkpoints"]]==list(CHECKPOINTS),
            "ARMS_AND_HELD_SCOPE")
    for arm,receipts in obj["source_receipts"].items():
        require(type(receipts) is list and len(receipts)==128 and
                len({r["event_id"] for r in receipts})==128,
                "UNIQUE_PUBLIC_RECEIPTS")
        for index,source_row in enumerate(receipts):
            family,regime=spec["phases"][index//32]
            world=campaign.B.make_episode(cohort=cohort,seed=source_seed,
                       index=index,family=family,regime=regime)
            views=campaign.B.public_views(world)
            identity=digest(canonical(["ckad28",p["original_source_sha256"],
                              cohort,source_seed,index,arm]))
            require(set(source_row)=={
                "event_id","index","views","first_action","next_state",
                "second_action","reward"
            } and source_row["event_id"]==identity and
                    source_row["index"]==index and
                    source_row["views"]==[list(v) for v in views],
                    "SOURCE_INITIAL_IDENTITY")
            first,second=source_row["first_action"],source_row["second_action"]
            require(type(first) is int and first in (0,1) and
                    type(second) is int and second in (0,1),
                    "PUBLIC_ACTIONS")
            observed=campaign.LEGACY.fixed_rollout(world,(first,second))
            require([source_row["next_state"],source_row["reward"]]==
                    [observed["s2"],observed["y"]],
                    "AUTHENTIC_CAUSAL_OUTCOME")
            if arm=="random" and index%4!=3:
                require((first,second)==policy.random_bits(
                    f"{scenario}/{seed}/random",index),
                    "RANDOM_POLICY_COMMITMENT")
        custody=obj["custody"][arm]
        require(custody["filename"]==f"{scenario}-{seed}-{arm}-native.json"
                and sha64(custody["checkpoint_sha256"])
                and 0<custody["checkpoint_bytes"]<=5*1024*1024
                and custody["original_prefix_episodes"]==448
                and custody["appended_public_episodes"]==128
                and custody["cold_restore_exact"] is True,
                "SOURCE_COLD_MODEL")
    require(len({r["event_id"] for events in obj["source_receipts"].values()
                 for r in events})==384,"CROSS_ARM_UNIQUE_IDENTITIES")
    for checkpoint in obj["checkpoints"]:
        count=checkpoint["count"]
        true_phase=spec["phases"][0 if count==0 else (count-1)//32]
        require(checkpoint["evaluator_only_phase"]==true_phase
                and checkpoint["held_episodes"]==96
                and set(checkpoint["by_arm"])==set(ARMS),
                "HELD_RECEIPT_SCOPE")
        for arm,metric in checkpoint["by_arm"].items():
            require(0<=metric["reward_sum"]<=96
                and 0<=metric["conventional_mle_reward_sum"]<=96
                and type(metric["reward_sum"]) is int
                and type(metric["conventional_mle_reward_sum"]) is int
                and sha64(metric["checkpoint_sha256"]),
                "HELD_REWARD_SOURCE")
            for key in ("transition_brier","terminal_brier"):
                require(0<=fraction(metric[key])<=1,"HELD_BRIER_RANGE")
            if count==128:
                require(metric["checkpoint_sha256"]==
                        obj["custody"][arm]["checkpoint_sha256"],
                        "FINAL_HELD_NATIVE_SHA")
    return obj


def metrics(cases):
    prereg=campaign.source_protocol()
    require(type(cases) is list and len(cases)==6,"SIX_SOURCE_CASES")
    indexed={}
    for case in cases:
        key=(case["scenario"],case["seed"])
        require(key not in indexed,"DUPLICATE_CASE")
        indexed[key]=verify_case(case,prereg)
    require(set(indexed)==set(product(SCENARIOS,SEEDS)),
            "INDEPENDENT_SOURCE_COVERAGE")

    def pooled(scenario,counts,arm,key):
        vals=[indexed[scenario,seed]["checkpoints"][CHECKPOINTS.index(count)]
              ["by_arm"][arm][key] for seed in SEEDS for count in counts]
        if key in ("terminal_brier","transition_brier"):
            return sum((fraction(v) for v in vals),Fraction(0))/len(vals)
        return Fraction(sum(vals),len(vals)*96)

    target=(64,96,128)
    decision=pooled("reward_change",target,"decision","reward_sum")
    native=pooled("reward_change",target,"native","reward_sum")
    random=pooled("reward_change",target,"random","reward_sum")
    conventional=pooled("reward_change",target,"decision",
                        "conventional_mle_reward_sum")
    brier_decision=pooled("reward_change",target,"decision","terminal_brier")
    brier_native=pooled("reward_change",target,"native","terminal_brier")
    null_decision=pooled("stationary_null",target,"decision","reward_sum")
    null_native=pooled("stationary_null",target,"native","reward_sum")
    return_decision=pooled("reward_change",(96,),"decision","reward_sum")
    return_native=pooled("reward_change",(96,),"native","reward_sum")
    seeds_deltas={str(seed):ratio(
        Fraction(sum(indexed["reward_change",seed]["checkpoints"][
            CHECKPOINTS.index(count)]["by_arm"]["decision"]["reward_sum"]
            -indexed["reward_change",seed]["checkpoints"][
            CHECKPOINTS.index(count)]["by_arm"]["native"]["reward_sum"]
            for count in target),3*96))
        for seed in SEEDS}
    alternate=sum(
        a["first_action"]!=b["first_action"] or
        a["second_action"]!=b["second_action"]
        for scenario,seed in product(SCENARIOS,SEEDS)
        for a,b in zip(indexed[scenario,seed]["source_receipts"]["decision"],
                       indexed[scenario,seed]["source_receipts"]["native"])
    )
    gates={
      "reward_change_gain_vs_native":decision-native>=Fraction(5,100),
      "reward_change_gain_vs_random":decision-random>=Fraction(5,100),
      "reward_change_per_seed":sum(fraction(v)>0 for v in seeds_deltas.values())>=2,
      "reward_prediction_quality":brier_native-brier_decision>=Fraction(1,100),
      "stationary_no_harm":null_decision>=null_native-Fraction(3,100),
      "familiar_return":return_decision>=return_native-Fraction(3,100),
      "strong_conventional":decision>=conventional,
      "source_integrity":True,
    }
    values={
      "reward_change_decision":ratio(decision),
      "reward_change_native":ratio(native),
      "reward_change_random":ratio(random),
      "reward_change_fitted_conventional":ratio(conventional),
      "decision_gain_vs_native":ratio(decision-native),
      "decision_gain_vs_random":ratio(decision-random),
      "native_minus_decision_terminal_brier":ratio(brier_native-brier_decision),
      "null_decision":ratio(null_decision),
      "null_native":ratio(null_native),
      "familiar_return_decision":ratio(return_decision),
      "familiar_return_native":ratio(return_native),
      "per_seed_gain_vs_native":seeds_deltas,
      "interventions_differing_from_native":alternate,
      "total_arm_episode_comparisons":128*6,
    }
    report={
      "schema":"yggdrasil.ckad28.decision-relevance.sealed.v1",
      "classification":"DEVELOPMENT_GO" if all(gates.values())
                       else "DEVELOPMENT_NO_GO",
      "parent_commit":prereg["parent_commit"],
      "generator_sha256":prereg["original_source_sha256"],
      "metrics":values,"frozen_gates":gates,
      "independent_parent_seed_groups":3,
      "matched_source_cases":6,
      "native_trainers":18,
      "public_action_consequence_episodes":2304,
      "held_evaluator_episodes":96*5*18,
      "protected_first_use":0,"held_updates":0,
      "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    }
    report["stable_sha256"]=digest(canonical(report))
    return report


def from_artifacts(root,osname):
    return [json.loads((root/f"ckad28-{osname}-{scenario}-{seed}-proof"/
                        "case-result.json").read_bytes())
            for scenario,seed in product(SCENARIOS,SEEDS)]


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifact-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    one=from_artifacts(args.artifact_root,"ubuntu-latest")
    two=from_artifacts(args.artifact_root,"windows-2022")
    for a,b in zip(one,two):
        require(campaign.stable(a)==a["stable_sha256"]==
                b["stable_sha256"]==campaign.stable(b),
                "TWO_OS_SOURCE_PARITY")
    result,replicated=metrics(one),metrics(two)
    require(result==replicated,"TWO_OS_AGGREGATE")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"classification":result["classification"],
                      "gates":result["frozen_gates"],
                      "metrics":result["metrics"],
                      "stable_sha256":result["stable_sha256"]},sort_keys=True))

if __name__=="__main__":
    main()

"""C37 original-source full-episode mechanistic attribution, retrospective only.

Reads ONLY exact authenticated already executed C36 MiniGrid per-arm trajectories;
does not import original environment, reconstruct unexecuted effects, or run it.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from research.native.itd02.r1.native_policy import canonical

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text(encoding="utf-8"))
PUB={"x","y","goal_x","goal_y","direction","front_blocked"}


def public(x):
    if type(x) is not dict or set(x)!=PUB or type(x["front_blocked"]) is not bool:
        raise ValueError("C37_PRIVATE_OR_UNQUALIFIED_PUBLIC_FRAME")
    for v in ("x","y","goal_x","goal_y","direction"):
        if type(x[v]) is not int or not 0<=x[v]<=31:
            raise ValueError("C37_NON_PUBLIC_OR_OUT_OF_RANGE_POSE")
    if x["direction"] not in (0,1,2,3):
        raise ValueError("C37_ILLEGAL_PUBLIC_ORIENTATION")
    return x


def pose(x):
    t=public(x)
    return (t["x"],t["y"],t["direction"])


def audit_episode(e):
    if type(e) is not dict or e["arm"] not in P["arms"] or e["seed"] not in P["original_C36_physical_world_roles"].get(e["family"],[]):
        raise ValueError("C37_ORIGINAL_ACTOR_OR_COHORT_DRIFT")
    events=e["real_true_source_actions"]
    if type(events) is not list or len(events)!=e["actual_source_steps"] or not 1<=len(events)<=128:
        raise ValueError("C37_NON_SOURCE_PHYSICAL_EPISODE")
    if hashlib.sha256(canonical(events)).hexdigest()!=e["trace_sha256"]:
        raise ValueError("C37_SOURCE_EVENT_DIGEST_DRIFT")
    if e["checkpoint_cold"]["fresh_os"] is not True:
        raise ValueError("C37_ORIGINAL_SOURCE_COLD_POLICY_STATE_MISSING")
    turns=changes=undo=revisits=longest=run=0
    observed=[pose(events[0]["before"])]
    unique={observed[0]}
    previous=None
    for index,s in enumerate(events):
        if type(s) is not dict or set(s)!={
            "t","before","R3_proposed","real_selected","real_after",
            "reward","terminal","trunc","two_step_option_started","option_second_action"}:
            raise ValueError("C37_EXPECTED_ORIGINAL_PHYSICAL_EVENT_FIELDS")
        if type(s["t"]) is not int or s["t"]!=index:
            raise ValueError("C37_SOURCE_STEP_NOT_CONTIGUOUS")
        b=public(s["before"]);a=public(s["real_after"])
        if previous and (previous["real_after"]!=b or previous["terminal"] or previous["trunc"]):
            raise ValueError("C37_SOURCE_PUBLIC_CHAIN_OR_TERMINAL_BREAK")
        act=s["real_selected"];base=s["R3_proposed"]
        if type(act) is not int or type(base) is not int or act not in (0,1,2) or base not in (0,1,2):
            raise ValueError("C37_UNSUPPORTED_SOURCE_ACTION")
        if act!=base:
            # A committed second original physical FORWARD legitimately follows
            # a genuine previous option-start TURN when current public front is clear.
            committed_forward=(act==2 and base in (0,1) and
                s["option_second_action"] is True and previous is not None and
                previous["two_step_option_started"] is True and
                previous["real_selected"] in (0,1) and b["front_blocked"] is False)
            switched_turn=(act in (0,1) and base in (0,1))
            if not (committed_forward or switched_turn):
                raise ValueError("C37_BROKEN_ORIGINAL_FORWARD_GUARD")
        if (b["goal_x"],b["goal_y"])!=(a["goal_x"],a["goal_y"]):
            raise ValueError("C37_GOAL_PRIVILEGE_ORIGINAL_DRIFT")
        if act in (0,1):
            turns+=1;run+=1;longest=max(longest,run)
            if b["x"]!=a["x"] or b["y"]!=a["y"] or a["direction"]!=(b["direction"]+(-1 if act==0 else 1))%4:
                raise ValueError("C37_ILLEGAL_ORIGINAL_PHYSICAL_TURN")
        else:
            run=0
            if b["direction"]!=a["direction"] or abs(a["x"]-b["x"])+abs(a["y"]-b["y"])>1:
                raise ValueError("C37_ILLEGAL_ORIGINAL_PHYSICAL_FORWARD")
        if act!=base:changes+=1
        if (previous and previous["real_selected"] in (0,1) and act in (0,1) and
            previous["real_selected"]!=act and pose(previous["before"])==pose(a)):
            undo+=1
        if pose(a) in observed[-4:]:revisits+=1
        observed.append(pose(a));unique.add(pose(a))
        if type(s["terminal"]) is not bool or type(s["trunc"]) is not bool or (
             type(s["two_step_option_started"]) is not bool or
             type(s["option_second_action"]) is not bool or
             s["terminal"] and s["trunc"]):
            raise ValueError("C37_CORRUPT_ORIGINAL_TERMINAL_OR_OPTION_FLAGS")
        if type(s["reward"]) not in (int,float):
            raise ValueError("C37_CORRUPT_SOURCE_REWARD")
        previous=s
    tail=events[-1]
    if (e["real_goal"] is not (tail["terminal"] and tail["reward"]>0) or
        e["real_collision"] is not (tail["terminal"] and tail["reward"]<0) or
        e["real_horizon"] is not tail["trunc"] or
        e["actually_executed_overrides"]!=changes or
        abs(e["real_reward"]-sum(q["reward"] for q in events))>1e-9):
        raise ValueError("C37_SOURCE_GOAL_OR_REWARD_DRIFT")
    return {"family":e["family"],"seed":e["seed"],"arm":e["arm"],
      "steps":len(events),"goal":int(e["real_goal"]),
      "horizon":int(e["real_horizon"]),"reward":e["real_reward"],
      "R3_turn_overrides":changes,"observed_two_step_option_starts":sum(q["two_step_option_started"] for q in events),
      "observed_second_option_steps":sum(q["option_second_action"] for q in events),
      "selected_turns":turns,"adjacent_opposite_turn_undo":undo,
      "source_pose_revisits_within_four_physical_steps":revisits,
      "max_source_turn_run_without_translation":longest,
      "unique_physically_returned_agent_poses":len(unique)}


def first_divergence(a,b):
    first=a["real_true_source_actions"];other=b["real_true_source_actions"]
    for i in range(min(len(first),len(other))):
        if first[i]["before"]!=other[i]["before"]:
            raise ValueError("C37_SOURCE_STATES_DIFFER_BEFORE_ACTUAL_SELECTED_ACTION")
        if first[i]["real_selected"]!=other[i]["real_selected"]:
            return {"first_physical_selected_action_difference_at":i,
              "reference_R3_actual":first[i]["real_selected"],
              "alternative_actual":other[i]["real_selected"],
              "same_public_preaction":True}
        if (first[i]["real_after"]!=other[i]["real_after"] or first[i]["reward"]!=other[i]["reward"]):
            raise ValueError("C37_IDENTICAL_SELECTED_ACTION_PHYSICS_DIVERGED")
    if len(first)!=len(other):
        raise ValueError("C37_NO_ACTION_DIVERGENCE_BUT_SOURCE_EPISODE_LENGTH_DIFFERS")
    return {"first_physical_selected_action_difference_at":None}


def strip_resource(q):
    return {k:v for k,v in q.items() if k!="resources"}


def evaluate(a,b,old):
    # Keep original past scientific custody and its terminal NO-GO.
    from research.mass_r7c36.compare import compare as original_compare
    original=original_compare(a,b)
    if original!=old or original["science_identical"] is not True or (
        original["result"]!="NO_REPEATABLE_C36_TRUE_SOURCE_TWO_STEP_POLICY_ADVANCEMENT"):
        raise ValueError("C37_ORIGINAL_C36_SCIENCE_MUST_STAY_NO_GO")
    data=a["genuine_original_source_episode_trajectories"]
    wanted={(arm,fam,seed) for arm in P["arms"] for fam,seeds in P["original_C36_physical_world_roles"].items() for seed in seeds}
    seen=[(q["arm"],q["family"],q["seed"]) for q in data]
    if set(seen)!=wanted or len(seen)!=40 or len(set(seen))!=40:
        raise ValueError("C37_ORIGINAL_EXPERIMENT_NOT_FIVE_BY_EIGHT")
    rows=[audit_episode(q) for q in data]
    lookup={(q["arm"],q["family"],q["seed"]):q for q in data}
    per_seed=[];trace_equal={arm:0 for arm in P["arms"]}
    diverge={arm:[] for arm in P["arms"]}
    for fam,seeds in P["original_C36_physical_world_roles"].items():
        for seed in seeds:
            base=lookup["original_r3",fam,seed]
            native=lookup["causal_two_step",fam,seed]
            shuffled=lookup["shuffled_effect_control",fam,seed]
            same_shuffled=(canonical(native["real_true_source_actions"])==canonical(shuffled["real_true_source_actions"]) and
                 native["real_goal"]==shuffled["real_goal"] and
                 native["real_reward"]==shuffled["real_reward"])
            per_seed.append({"family":fam,"seed":seed,
                "native_vs_shuffled_effect_complete_real_source_trace_equal":same_shuffled,
                "native_reached_original_goal":native["real_goal"],
                "original_R3_reached_goal":base["real_goal"],
                "native_true_actions":native["actual_source_steps"],
                "R3_true_actions":base["actual_source_steps"],
                "native_vs_original_R3_first_divergence":first_divergence(base,native)})
            for arm in P["arms"]:
                other=lookup[arm,fam,seed]
                diff=first_divergence(base,other)
                diverge[arm].append({"family":fam,"seed":seed,**diff})
                if diff["first_physical_selected_action_difference_at"] is None:
                    trace_equal[arm]+=1
    if any(not r["native_vs_shuffled_effect_complete_real_source_trace_equal"] for r in per_seed):
        native_unique="EXISTING_EVIDENCE_DIFFERS_REINVESTIGATE"
    else:
        native_unique="NO_NATIVE_CAUSAL_EFFECT_UNIQUENESS_SHUFFLED_SOURCE_TRAJECTORIES_IDENTICAL_8_OF_8"
    grouped=defaultdict(lambda:defaultdict(list))
    for row in rows:grouped[row["arm"]][row["family"]].append(row)
    integer_fields=("steps","goal","horizon","R3_turn_overrides","observed_two_step_option_starts",
      "observed_second_option_steps","selected_turns","adjacent_opposite_turn_undo",
      "source_pose_revisits_within_four_physical_steps")
    stratified={}
    for arm,by_family in grouped.items():
        stratified[arm]={}
        for fam,records in by_family.items():
            stratified[arm][fam]={"episodes":len(records),
                **{k:sum(r[k] for r in records) for k in integer_fields},
                "reward_sum":round(sum(r["reward"] for r in records),9)}
    r3=a["actual_source_actor_summary"]["original_r3"]
    native=a["actual_source_actor_summary"]["causal_two_step"]
    conventional=a["actual_source_actor_summary"]["trained_conventional_ridge_two_step"]
    if (r3["real_goals"]!=7 or r3["real_source_actions"]!=335 or
        native["real_goals"]!=8 or native["real_source_actions"]!=289 or
        conventional["real_goals"]!=8 or conventional["real_source_actions"]!=252):
        raise ValueError("C37_C36_FULL_SOURCE_PHYSICAL_ACCEPTANCE_DRIFT")
    return {"schema":P["schema"],"physical_original_C36_terminal_science":original["result"],
      "original_C36_frozen_eval_worlds":8,"fitted_source_real_two_action_FIT_pairs":a["original_source_C35_FIT_fork_count"],
      "full_real_source_episode_records":40,"source_original":P["source_origin"],
      "physically_returned_action_loop_and_retention_by_family":stratified,
      "all_original_start_state_factorial_episode_comparisons":per_seed,
      "first_physical_action_divergence_reference_R3":diverge,
      "full_identical_selected_action_source_histories_vs_R3":trace_equal,
      "learned_native_conditional_effect_unique_control_attribution":native_unique,
      "native_better_than_R3_but_worse_than_trained_conventional":True,
      "native_vs_shuffled_effect_full_source_equality_count":sum(x["native_vs_shuffled_effect_complete_real_source_trace_equal"] for x in per_seed),
      "new_original_world_source_actions":0,"new_public_DEV_or_protected_first_use":0,
      "new_native_world_model_or_dynamic_intervention":"NOT_EXECUTED",
      "native_long_horizon_planning_novelty":"NOT_DEMONSTRATED",
      "interpretation":"Observed equal-world trajectories of native and effect-shuffled original source falsify unique native learned conditional effect attribution. Loop-veto memory is a mechanistic candidate, not independently isolated without full 2x2 prospective factorial.",
      "C31_C32_one_bit_turn_override":"PERMANENT_NO_GO"}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-C36-evidence",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    folder=args.original_C36_evidence
    if {q.name for q in folder.iterdir() if q.is_file()}!={"process-a.json","process-b.json","comparison.json","process-a.log","process-b.log"}:
        raise ValueError("C37_ORIGINAL_C36_ARCHIVE_MEMBERS_CHANGED")
    a=json.loads((folder/"process-a.json").read_bytes())
    b=json.loads((folder/"process-b.json").read_bytes())
    c=json.loads((folder/"comparison.json").read_bytes())
    report=evaluate(a,b,c)
    if args.output.exists() or not args.output.parent.is_dir():
        raise ValueError("C37_NEW_SOURCE_EVIDENCE_DESTINATION_REQUIRED")
    bits=canonical(report);args.output.write_bytes(bits+b"\n")
    print("C37_ORIGINAL_C36_FULL_SOURCE_TWICE_RECONCILED=PASS")
    print("C37_NATIVE_EFFECT_SHUFFLED_FULL_PHYSICAL_TRAJECTORY_PARITY="+str(report["native_vs_shuffled_effect_full_source_equality_count"])+"/8")
    print("C37_SOURCE_PHYSICAL_FACTORIAL_LOOPS="+json.dumps(report["physically_returned_action_loop_and_retention_by_family"],sort_keys=True))
    print("C37_SCIENTIFIC_NATIVE_CAUSAL_ATTRIBUTION="+report["learned_native_conditional_effect_unique_control_attribution"])
    print("C37_NEW_ORIGINAL_ENV_ACTIONS=ZERO; C37_PROTECTED_FSA_FIRST_USE=DENIED")
    print("C37_FROZEN_REPORT_SHA256="+hashlib.sha256(bits).hexdigest())

if __name__=="__main__":main()

"""C33: source-only forensic audit of actual already executed C32 physical actions.

Never imports the MiniGrid simulator and never calls environment reset/step.
The original C32 ZIP is externally authenticated by exact SHA256 in CI.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c32.compare import compare as original_compare

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text(encoding="utf-8"))
PUBLIC={"x","y","direction","goal_x","goal_y","front_blocked"}
ARMS=P["frozen_actors"]


def checked_public(p):
    if type(p) is not dict or set(p)!=PUBLIC:
        raise ValueError("C33_PRIVILEGED_OR_INCOMPLETE_PUBLIC_POSE")
    if any(type(p[k]) is not int or not 0<=p[k]<=31 for k in
           ("x","y","goal_x","goal_y","direction")) or p["direction"] not in range(4):
        raise ValueError("C33_BAD_PUBLIC_POSITION")
    if type(p["front_blocked"]) is not bool:
        raise ValueError("C33_MASKED_FALSE_NOT_A_REAL_BOOLEAN")
    return p


def pose(p):
    checked_public(p)
    return (p["x"],p["y"],p["direction"])


def validate_action_event(e, t, expected_before=None):
    if type(e) is not dict or set(e)!={
      "t","before","original_r3_proposed","executed",
      "after","reward","terminated","truncated"}:
        raise ValueError("C33_NON_SOURCE_ACTION_EVENT_FIELDS")
    if type(e["t"]) is not int or e["t"]!=t:
        raise ValueError("C33_OUT_OF_ORDER_SOURCE_ACTION")
    b=checked_public(e["before"]);a=checked_public(e["after"])
    if expected_before is not None and b!=expected_before:
        raise ValueError("C33_UNLINKED_ORIGINAL_PHYSICAL_SOURCE_EVENT")
    action=e["executed"];prior=e["original_r3_proposed"]
    if type(action) is not int or type(prior) is not int or (
        action not in (0,1,2) or prior not in (0,1,2)):
        raise ValueError("C33_ILLEGAL_PHYSICALLY_EXECUTED_ACTION")
    if (action!=prior and (action not in (0,1) or prior not in (0,1))):
        raise ValueError("C33_R3_FORWARD_OVERRIDE_DISALLOWED")
    if (b["goal_x"],b["goal_y"])!=(a["goal_x"],a["goal_y"]):
        raise ValueError("C33_SOURCE_GOAL_OR_CUSTODY_DRIFT")
    if action in (0,1):
        if pose(a)[:2]!=pose(b)[:2] or a["direction"]!=(
            b["direction"]+(-1 if action==0 else 1))%4:
            raise ValueError("C33_ILLEGAL_ORIGINAL_TURN_CONSEQUENCE")
    elif (a["direction"]!=b["direction"] or
          abs(a["x"]-b["x"])+abs(a["y"]-b["y"])>1):
        raise ValueError("C33_ILLEGAL_ORIGINAL_FORWARD_CONSEQUENCE")
    if (type(e["reward"]) not in (int,float) or not math.isfinite(e["reward"])
        or type(e["terminated"]) is not bool or
        type(e["truncated"]) is not bool or
        (e["terminated"] and e["truncated"])):
        raise ValueError("C33_INVALID_ORIGINAL_SOURCE_RETURN")
    return a


def summarize_physical_episode(ep):
    if type(ep) is not dict:
        raise ValueError("C33_NO_PHYSICAL_EPISODE")
    actions=ep["source_actual_actions"]
    if type(actions) is not list or not actions or len(actions)>256 or ep["steps"]!=len(actions):
        raise ValueError("C33_UNTRUSTWORTHY_PHYSICAL_ACTION_COUNT")
    if hashlib.sha256(canonical(actions)).hexdigest()!=ep["source_trace_sha256"]:
        raise ValueError("C33_ORIGINAL_ACTION_RETURN_HASH_MISMATCH")
    if ep["arm"] not in ARMS or ep["seed"] not in P["frozen_seed_roles"].get(ep["family"],[]):
        raise ValueError("C33_NONFROZEN_SOURCE_WORLD_OR_ARM")
    seen_recent=[pose(actions[0]["before"])]
    unique_poses={seen_recent[0]}
    revisits=0
    adjacent_undo=0
    turn_run=0;longest_turn_run=0
    selected_turn_changes=0
    prev=None
    last=None
    for t,e in enumerate(actions):
        a=validate_action_event(e,t,last)
        if t+1<len(actions) and (e["terminated"] or e["truncated"]):
            raise ValueError("C33_SOURCE_STEP_AFTER_TERMINATION")
        last=a
        now_pose=pose(a)
        if now_pose in seen_recent[-4:]:
            revisits+=1
        seen_recent.append(now_pose)
        unique_poses.add(now_pose)
        if e["executed"] in (0,1):
            turn_run+=1;longest_turn_run=max(longest_turn_run,turn_run)
        else:
            turn_run=0
        if e["executed"]!=e["original_r3_proposed"]:
            selected_turn_changes+=1
        if prev is not None and (
           prev["executed"] in (0,1) and e["executed"] in (0,1) and
           prev["executed"]!=e["executed"] and
           pose(prev["before"])==now_pose):
            adjacent_undo+=1
        prev=e
    if (ep["native_real_turn_changes"]!=selected_turn_changes or
        ep["source_goal"] is not (actions[-1]["terminated"] and actions[-1]["reward"]>0) or
        ep["source_collision"] is not (actions[-1]["terminated"] and actions[-1]["reward"]<0) or
        ep["source_horizon"] is not actions[-1]["truncated"] or
        abs(ep["reward_sum"]-sum(e["reward"] for e in actions))>1e-9):
        raise ValueError("C33_ORIGINAL_SOURCE_GOAL_REWARD_OR_TURN_DRIFT")
    return {
       "family":ep["family"],"seed":ep["seed"],"arm":ep["arm"],
       "steps":len(actions),"goals":int(ep["source_goal"]),
       "horizon":int(ep["source_horizon"]),"reward":ep["reward_sum"],
       "executed_turn_substitutions":selected_turn_changes,
       "adjacent_turn_undo_pairs":adjacent_undo,
       "source_public_pose_revisits_within_4_steps":revisits,
       "unique_source_public_agent_poses":len(unique_poses),
       "longest_consecutive_turns_without_translation":longest_turn_run,
    }


def first_divergence(reference, other):
    # Same original seed only matches states until first different actual
    # chosen action. Later actions are two independently evolved source worlds.
    a=reference["source_actual_actions"]
    b=other["source_actual_actions"]
    for i in range(min(len(a),len(b))):
        if a[i]["before"]!=b[i]["before"]:
            raise ValueError("C33_SOURCE_WORLD_STATES_DIVERGED_BEFORE_FIRST_ACTION")
        if a[i]["executed"]!=b[i]["executed"]:
            return {"first_action_difference_at_step":i,
               "source_r3":a[i]["executed"],"alternate":b[i]["executed"]}
        if a[i]["after"]!=b[i]["after"] or a[i]["reward"]!=b[i]["reward"]:
            raise ValueError("C33_IDENTICAL_ACTION_PHYSICS_UNEXPECTEDLY_DIVERGED")
    if len(a)!=len(b):
        raise ValueError("C33_UNEXPLAINED_LENGTH_WITH_NO_ACTION_DIVERGENCE")
    return None


def audit(a,b):
    original_repeat=original_compare(a,b)
    if original_repeat["result"]!="NO_REPEATABLE_C32_REAL_SOURCE_NATIVE_EFFECT_DECISION_ADVANTAGE":
        raise ValueError("C33_EXPECTED_NEGATIVE_SCIENCE_WAS_REWRITTEN")
    archived=a["original_world_episode_records"]
    expected_keys={(arm,fam,seed) for arm in ARMS
                   for fam,seeds in P["frozen_seed_roles"].items() for seed in seeds}
    keys=[(e["arm"],e["family"],e["seed"]) for e in archived]
    if len(keys)!=56 or set(keys)!=expected_keys or len(set(keys))!=len(keys):
        raise ValueError("C33_INCOMPLETE_REAL_ORIGINAL_SOURCE_ROSTER")
    lookup={(e["arm"],e["family"],e["seed"]):e for e in archived}
    episode_summaries=[summarize_physical_episode(e) for e in archived]
    group=defaultdict(list)
    for row in episode_summaries:
        group[(row["arm"],row["family"])].append(row)
    fields=["steps","goals","horizon","reward","executed_turn_substitutions",
      "adjacent_turn_undo_pairs","source_public_pose_revisits_within_4_steps",
      "unique_source_public_agent_poses"]
    family_results={}
    for (arm,fam),rows in sorted(group.items()):
        family_results.setdefault(arm,{})[fam]={
           **{key:round(sum(r[key] for r in rows),8) if key=="reward" else
                  sum(r[key] for r in rows) for key in fields},
           "episodes":len(rows),
           "longest_consecutive_turns_without_translation":max(
                  r["longest_consecutive_turns_without_translation"] for r in rows)}
    diverge={};identical={}
    for arm in ARMS:
        diverge[arm]=[]
        identical[arm]=0
        for fam,seeds in P["frozen_seed_roles"].items():
            for seed in seeds:
                base=lookup["r3_original",fam,seed]
                row=lookup[arm,fam,seed]
                d=first_divergence(base,row)
                diverge[arm].append({"family":fam,"seed":seed,**(d or {"first_action_difference_at_step":None})})
                if d is None:identical[arm]+=1
    exact_pairs={}
    for arm in ("native_frozen","native_shuffled","full9_conventional_sgd",
                "full9_conventional_momentum","temporal_bayes"):
        exact_pairs[arm]=sum(
          canonical(lookup["native",fam,seed]["source_actual_actions"])==
          canonical(lookup[arm,fam,seed]["source_actual_actions"])
          for fam,seeds in P["frozen_seed_roles"].items() for seed in seeds)
    native=[r for r in episode_summaries if r["arm"]=="native"]
    baseline=[r for r in episode_summaries if r["arm"]=="r3_original"]
    if sum(r["steps"] for r in native)!=934 or sum(r["goals"] for r in native)!=2:
        raise ValueError("C33_ORIGINAL_NATIVE_NEGATIVE_OUTCOME_DRIFT")
    if sum(r["steps"] for r in baseline)!=256 or sum(r["goals"] for r in baseline)!=8:
        raise ValueError("C33_ORIGINAL_R3_SUCCESS_OUTCOME_DRIFT")
    if sum(r["executed_turn_substitutions"] for r in native)!=430:
        raise ValueError("C33_ORIGINAL_NATIVE_PHYSICAL_TURN_OVERRIDE_DRIFT")
    return {
     "schema":P["schema"],"original_C32_accepted_science":False,
     "original_source_external_identity":P["original_source"],
     "original_two_process_physical_replay":original_repeat["result"],
     "previously_consumed_source_FIT_only":True,
     "original_policy_physical_episodes_per_process":len(archived),
     "original_source_new_actions_run_in_this_audit":0,
     "source_DEV_VALID_protected_first_use":0,
     "per_arm_and_original_world_family":family_results,
     "per_episode_physical_failure_features":episode_summaries,
     "first_actual_action_divergence_from_original_r3":diverge,
     "identical_complete_original_world_episodes_vs_R3":identical,
     "native_versus_competing_control_equal_complete_source_episodes":exact_pairs,
     "scientific_disposition":"C32_MYOPIC_TURN_OVERRIDE_STOPPED_REAL_SOURCE_NO_GO",
     "mechanism_diagnosis_is_retrospective_not_identified_causal_counterfactual":True,
     "next_mechanism_requires_new_qualified_intervention_not_THRESHOLD_RETRY":True
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--original-artifact-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    folder=args.original_artifact_dir
    members={x.name for x in folder.iterdir() if x.is_file()}
    must={"process-a.json","process-b.json","comparison.json","process-a.log","process-b.log"}
    if members!=must:
        raise ValueError("C33_ARCHIVED_C32_ORIGINAL_SOURCE_MEMBERS_CHANGED")
    a=json.loads((folder/"process-a.json").read_text(encoding="utf-8"))
    b=json.loads((folder/"process-b.json").read_text(encoding="utf-8"))
    value=audit(a,b)
    prior=json.loads((folder/"comparison.json").read_text(encoding="utf-8"))
    if prior.get("result")!=value["original_two_process_physical_replay"]:
        raise ValueError("C33_C32_ARCHIVED_SOURCE_REPEAT_VERDICT_MISMATCH")
    if args.output.exists() or not args.output.parent.is_dir():
        raise ValueError("C33_NO_FRESH_EVIDENCE_DESTINATION")
    data=canonical(value)
    args.output.write_bytes(data+b"\n")
    def score(arm):
        rows=value["per_arm_and_original_world_family"][arm].values()
        keys=("steps","goals","horizon","executed_turn_substitutions",
              "adjacent_turn_undo_pairs","source_public_pose_revisits_within_4_steps")
        return {k:sum(row[k] for row in rows) for k in keys}
    print("C33_GENUINE_C32_ORIGINAL_ACTION_DIGEST_AND_REPEAT=PASS",flush=True)
    print("C33_ORIGINAL_R3_FAILURE_BASELINE="+json.dumps(score("r3_original"),sort_keys=True),flush=True)
    print("C33_NATIVE_ACTUAL_FAILURE_MECHANICS="+json.dumps(score("native"),sort_keys=True),flush=True)
    print("C33_NATIVE_VS_COMPETITORS_IDENTICAL_FULL_EPISODES="+
       json.dumps(value["native_versus_competing_control_equal_complete_source_episodes"],sort_keys=True),flush=True)
    print("C33_TRAJECTORY_AUDIT_SHA256="+hashlib.sha256(data).hexdigest(),flush=True)
    print("C33_NEW_ORIGINAL_WORLD_ACTIONS=0; C33_PROTECTED_FIRST_USE=DENIED",flush=True)

if __name__=="__main__":
    main()

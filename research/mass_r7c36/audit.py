"""C36: retrospective original-world physically matched two-action contrasts.

Source-only. Never imports or constructs MiniGrid. Every effect is a real
already-executed C35 chosen-action return from the SAME authenticated reset
and precommitted original physical action prefix. No hypothetical outcomes.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
from research.native.itd02.r1.native_policy import canonical

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text(encoding="utf-8"))
PUBLIC={"x","y","goal_x","goal_y","direction","front_blocked"}
PAIRS={f"{a}{b}" for a in (0,1,2) for b in (0,1,2)}
CONTRAST=[("01","10"),("00","11"),("02","20"),("12","21")]


def validate_public(s):
    if type(s) is not dict or set(s)!=PUBLIC:
        raise ValueError("C36_INVALID_OR_PRIVILEGED_PUBLIC_DATA")
    for k in ("x","y","goal_x","goal_y","direction"):
        if type(s[k]) is not int or not 0<=s[k]<=31:
            raise ValueError("C36_BAD_PUBLIC_COORDINATE")
    if s["direction"] not in range(4) or type(s["front_blocked"]) is not bool:
        raise ValueError("C36_ILLEGAL_PUBLIC_HEADING_OR_SENSOR")
    return s


def validate_selected_step(step, action, prior):
    if type(step) is not dict or set(step)!={"action","before","after","reward","term","trunc"}:
        raise ValueError("C36_ORIGINAL_ACTION_SOURCE_FIELDS_DRIFT")
    if type(step["action"]) is not int or step["action"]!=action or action not in (0,1,2):
        raise ValueError("C36_SELECTED_ACTION_IDENTITY_DRIFT")
    a=validate_public(step["before"]); b=validate_public(step["after"])
    if a!=prior or (a["goal_x"],a["goal_y"])!=(b["goal_x"],b["goal_y"]):
        raise ValueError("C36_SOURCE_RETURN_CHAIN_OR_GOAL_MISMATCH")
    if action in (0,1):
        if (a["x"],a["y"])!=(b["x"],b["y"]) or b["direction"]!=(a["direction"]+(-1 if action==0 else 1))%4:
            raise ValueError("C36_SELECTED_TURN_PHYSICS_MISMATCH")
    elif (b["direction"]!=a["direction"] or
        abs(b["x"]-a["x"])+abs(b["y"]-a["y"])>1):
        raise ValueError("C36_SELECTED_FORWARD_PHYSICS_MISMATCH")
    if type(step["reward"]) not in (int,float) or not math.isfinite(step["reward"]) or (
         type(step["term"]) is not bool or type(step["trunc"]) is not bool or
         (step["term"] and step["trunc"])):
        raise ValueError("C36_INVALID_SOURCE_REWARD_OR_TERMINAL")
    return b


def validate_anchor(row,protocol,role):
    if type(row) is not dict or type(protocol) is not dict or role not in ("FIT","FIT_CHECK"):
        raise ValueError("C36_ORIGINAL_SOURCE_ANCHOR_INVALID")
    fam=row.get("family");seed=row.get("seed");tick=row.get("tick")
    if fam not in protocol["worlds"] or type(seed) is not int or seed not in protocol["worlds"][fam][role] or (
        type(tick) is not int or tick not in protocol["protocol"]["sourcePrefixTicks"]):
        raise ValueError("C36_SOURCE_ORIGINAL_COHORT_ROLE_DRIFT")
    initial=validate_public(row["public_initial"])
    if not isinstance(row.get("anchor_source_sha256"),str) or len(row["anchor_source_sha256"])!=64:
        raise ValueError("C36_NO_ORIGINAL_GRID_ANCHOR_CUSTODY")
    if len(row["original_source_prefix"])!=tick or type(row["all_nine_original_physical_pairs"]) is not dict or (
       set(row["all_nine_original_physical_pairs"])!=PAIRS):
        raise ValueError("C36_FROZEN_PREFIX_OR_ACTUAL_PAIR_MISSING")
    prev=None
    for t,rec in enumerate(row["original_source_prefix"]):
        if type(rec) is not dict or rec.get("step")!=t or rec.get("action") not in (0,1,2):
            raise ValueError("C36_ORIGINAL_PREFIX_ACTION_DRIFT")
        s=validate_public(rec["before"]);n=validate_public(rec["after"])
        if prev is not None and s!=prev:raise ValueError("C36_ORIGINAL_PREFIX_CHAIN_DRIFT")
        prev=n
    if prev is not None and prev!=initial:
        raise ValueError("C36_ORIGINAL_PREFIX_END_DIFFERENT_FROM_ANCHOR")
    outcomes={}
    for pair in sorted(PAIRS):
        r=row["all_nine_original_physical_pairs"][pair]
        if type(r) is not dict or r.get("pair")!=[int(x) for x in pair] or (
             r.get("completed_two_original_actions") is not True):
            raise ValueError("C36_NONPHYSICAL_OR_MISSING_TWO_SELECTED_SOURCE_ACTIONS")
        steps=r.get("actual_selected_source_actions")
        if type(steps) is not list or len(steps)!=2:
            raise ValueError("C36_NOT_TWO_ACTUAL_ORIGINAL_RETURNS")
        if hashlib.sha256(canonical(steps)).hexdigest()!=r.get("physical_trace_sha256"):
            raise ValueError("C36_SOURCE_SELECTED_RETURN_SHA_DRIFT")
        prior=initial
        for idx,x in enumerate(steps):
            prior=validate_selected_step(x,int(pair[idx]),prior)
            if idx==0 and (x["term"] or x["trunc"]):
                raise ValueError("C36_CANNOT_HAVE_TWO_PHYSICAL_ACTIONS_AFTER_FIRST_TERMINATION")
        if (r.get("actually_observed_next_front_blocked") is not prior["front_blocked"] or
            type(r.get("actual_source_reward_sum")) not in (int,float) or
            not math.isclose(sum(x["reward"] for x in steps),r["actual_source_reward_sum"],abs_tol=1e-12) or
            r.get("actual_agent_translation")!=abs(prior["x"]-initial["x"])+abs(prior["y"]-initial["y"])):
            raise ValueError("C36_FINAL_PHYSICAL_SELECTED_RESULT_DRIFT")
        dist=lambda z:abs(z["goal_x"]-z["x"])+abs(z["goal_y"]-z["y"])
        if r.get("real_two_step_goal_distance_improvement")!=dist(initial)-dist(prior):
            raise ValueError("C36_SOURCE_GOAL_PROGRESS_DRIFT")
        outcomes[pair]={"end":prior,"reward":r["actual_source_reward_sum"],
            "progress":r["real_two_step_goal_distance_improvement"],
            "translation":r["actual_agent_translation"],
            "terminal":steps[-1]["term"],"truncated":steps[-1]["trunc"],
            "first_step_front":steps[0]["after"]["front_blocked"]}
    return outcomes


def contrasted(left,right):
    a=left["end"];b=right["end"]
    same_pose=(a["x"],a["y"],a["direction"])==(b["x"],b["y"],b["direction"])
    return {"agent_pose_heading_same":same_pose,
      "final_front_same":a["front_blocked"]==b["front_blocked"],
      "final_front_diff_with_same_agent_pose":same_pose and a["front_blocked"]!=b["front_blocked"],
      "full_public_after_same":a==b,
      "real_reward_same":left["reward"]==right["reward"],
      "goal_progress_same":left["progress"]==right["progress"],
      "source_terminal_same":(left["terminal"],left["truncated"])==(right["terminal"],right["truncated"]),
      "actual_goal_progress_left":left["progress"],"actual_goal_progress_right":right["progress"],
      "actual_translation_left":left["translation"],"actual_translation_right":right["translation"]}


def audit_one(process):
    proto=json.loads((HERE.parent/"mass_r7c35"/"PREREG.json").read_text())
    if process.get("schema")!=proto["schema"] or process.get("result")!=proto["acceptance"]["noGo"] or (
         process.get("original_environment_source")!=P["original_source"] or
         process.get("science_accepted") is not False or
         process.get("original_R3_modified") is not False):
        raise ValueError("C36_ORIGINAL_C35_NEGATIVE_SOURCE_IDENTITY_DRIFT")
    details=[];stats=defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    for role,key in (("FIT","source_original_fit_real_two_action_forks"),
                     ("FIT_CHECK","source_independent_internal_fit_check_real_forks")):
        anchors=process[key];seen=set()
        for row in anchors:
            triple=(row["family"],row["seed"],row["tick"])
            if triple in seen:raise ValueError("C36_DUPLICATE_ORIGINAL_PHYSICAL_ANCHOR")
            seen.add(triple)
            out=validate_anchor(row,proto,role)
            for l,r in CONTRAST:
                measures=contrasted(out[l],out[r]);s=stats[role][row["family"]][l+" vs "+r]
                s["genuine_matched_source_anchors"]+=1
                for k in ("agent_pose_heading_same","final_front_same","final_front_diff_with_same_agent_pose",
                          "full_public_after_same","real_reward_same","goal_progress_same","source_terminal_same"):
                    s[k]+=int(measures[k])
                s["actual_nonzero_goal_progress_difference"]+=int(measures["actual_goal_progress_left"]!=measures["actual_goal_progress_right"])
                s["actual_nonzero_translation_difference"]+=int(measures["actual_translation_left"]!=measures["actual_translation_right"])
                details.append({"role":role,"family":row["family"],"seed":row["seed"],"tick":row["tick"],
                  "real_selected_pairs":[l,r],"actual_physical_outcomes":measures})
        expected=31 if role=="FIT" else 15
        if len(anchors)!=expected:
            raise ValueError("C36_PRIOR_REAL_SOURCE_ANCHOR_COUNT_CHANGED")
    frozen={role:{fam:dict(sorted(v.items())) for fam,v in sorted(x.items())} for role,x in stats.items()}
    pure=("01 vs 10","00 vs 11")
    for role,fams in frozen.items():
        for fam,contrasts in fams.items():
            for name in pure:
                if contrasts[name]["agent_pose_heading_same"]!=contrasts[name]["genuine_matched_source_anchors"]:
                    raise ValueError("C36_PHYSICAL_SYMMETRY_CONTROLS_DO_NOT_MATCH")
    return {"schema":P["schema"],"science_position":"RECONCILED_REAL_MATCHED_CAUSAL_ACTION_SEQUENCE_CONTRASTS_NOT_NATIVE_CONTROL",
       "original_C35_scientific_NO_GO_preserved":True,
       "original_source_physical_intervention_anchors":{k:sum(next(iter(c.values()))["genuine_matched_source_anchors"] for c in v.values()) for k,v in frozen.items()},
       "genuine_two_source_action_observation_contrast_strata":frozen,
       "all_matched_true_original_action_pair_outcomes":details,
       "original_source_actions_executed_in_C36":0,
       "new_DEV_VALID_protected_first_use":0,
       "intervention_causality_limited_to_matching_original_source_anchor_and_two_clock_steps":True,
       "native_cognitive_architectural_superiority":"NOT_TESTED",
       "C31_C32_myopic_turn_switch_policy":"STOPPED"}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-c35-archive",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    archive=a.original_c35_archive
    members={v.name for v in archive.iterdir() if v.is_file()}
    if members!={"process-a.json","process-b.json","comparison.json","process-a.log","process-b.log"}:
        raise ValueError("C36_UNEXPECTED_ORIGINAL_C35_ARCHIVE_CONTENTS")
    x=json.loads((archive/"process-a.json").read_bytes())
    y=json.loads((archive/"process-b.json").read_bytes())
    # Original C35 unchanged verifier authenticates all source SHA, two runs.
    from research.mass_r7c35.compare import compare as original_reconcile
    c=original_reconcile(x,y)
    past=json.loads((archive/"comparison.json").read_bytes())
    if c!=past or c["science_identical"] is not True or (
         c["result"]!="NO_REPEATABLE_C35_TWO_ACTION_CAUSAL_EFFECT_PREDICTIVE_ADVANCEMENT"):
        raise ValueError("C36_ARCHIVED_C35_SCIENCE_RECONCILIATION_FAILURE")
    first=audit_one(x);second=audit_one(y)
    if canonical(first)!=canonical(second):
        raise ValueError("C36_ORIGINAL_INDEPENDENT_SOURCE_PHYSICAL_CONTRAST_DIVERGENCE")
    if a.out.exists() or not a.out.parent.exists():
        raise ValueError("C36_OUTPUT_MUST_BE_FRESH")
    data=canonical(first);a.out.write_bytes(data+b"\n")
    print("C36_C35_ORIGINAL_SOURCE_TWO_PRODUCERS_AND_SHA=PASS")
    print("C36_NEW_ORIGINAL_SOURCE_ACTIONS=0")
    print("C36_PHYSICAL_MATCHED_INTERVENTION_SUMMARY="+json.dumps(
      first["genuine_two_source_action_observation_contrast_strata"],sort_keys=True))
    print("C36_NO_NATIVE_ADVANTAGE_CLAIM=PASS")
    print("C36_ORIGINAL_FIRST_USE_PROTECTED=DENIED")
    print("C36_REPORT_SHA256="+hashlib.sha256(data).hexdigest())

if __name__=="__main__":
    main()

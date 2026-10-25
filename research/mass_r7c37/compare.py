"""Independent read-only custody of two complete C37 source reports."""
import argparse
import hashlib
import json
from pathlib import Path
from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c36.run import P as C36_FROZEN_PROTOCOL

ROOT=Path(__file__).resolve().parent
PROTOCOL=json.loads((ROOT/"PREREG.json").read_text())
PUBLIC={"x","y","direction","goal_x","goal_y","front_blocked"}

def check(report):
    if report.get("schema")!=PROTOCOL["schema"]:
        raise ValueError("C37_WRONG_ORIGINAL_PROTOCOL")
    # C35 original FIT has 31 anchors x nine real pairs = 279 actions.
    # The frozen C36/C37 option learner fits only the three predeclared
    # (turn/forward, turn/forward, forward/forward) pairs per anchor.
    frozen_pairs=PROTOCOL["FIT_only"]["actualPairCount"]
    option_count=len(C36_FROZEN_PROTOCOL["mechanism"]["optionCandidates"])
    if (frozen_pairs%9 or option_count!=3 or
        C36_FROZEN_PROTOCOL["mechanism"]["optionCandidates"]!=[[0,2],[1,2],[2,2]]):
        raise ValueError("C37_FROZEN_PAIR_PORTFOLIO_INVALID")
    if report.get("FIT_trained_two_action_original_forks")!=frozen_pairs//3:
        raise ValueError("C37_TRAINED_OPTION_SUBSET_IDENTITY_DRIFT")
    criteria=report.get("criteria")
    if not isinstance(criteria,dict) or not criteria:
        raise ValueError("C37_MISSING_FROZEN_ACCEPTANCE_EVIDENCE")
    expected_verdict=(PROTOCOL["preregAccept"]["positive"] if all(criteria.values())
                      else PROTOCOL["preregAccept"]["noGo"])
    if report.get("scientific_result")!=expected_verdict:
        raise ValueError("C37_SOURCE_VERDICT_NOT_SUPPORTED_BY_FROZEN_GATES")
    if (report.get("first_use") is not False or
        report.get("scientific_accepted") is not False or
        report.get("original_R3_source_modified") is not False):
        raise ValueError("C37_UNAUTHORIZED_SOURCE_CLAIM")
    expected=hashlib.sha256((ROOT/"PREREG.json").read_bytes()).hexdigest()
    if report.get("precommitted_protocol_sha256")!=expected:
        raise ValueError("C37_PREREG_CHANGED")
    seen=set()
    for episode in report["original_source_true_physical_actor_episodes"]:
        identity=(episode["arm"],episode["family"],episode["seed"])
        if identity in seen:raise ValueError("C37_REPEATED_ACTOR_WORLD")
        seen.add(identity)
        if episode["arm"] not in PROTOCOL["arms"]:
            raise ValueError("C37_UNREGISTERED_ACTOR")
        seeds=PROTOCOL["new_original_public_development_worlds"].get(episode["family"])
        if seeds is None or episode["seed"] not in seeds:
            raise ValueError("C37_UNREGISTERED_SOURCE_WORLD")
        events=episode["full_original_public_source_action_trajectory"]
        if (not events or len(events)!=episode["true_original_action_count"] or
            hashlib.sha256(canonical(events)).hexdigest()!=episode["original_trace_sha256"]):
            raise ValueError("C37_SOURCE_ACTION_TRACE_MISMATCH")
        for index,item in enumerate(events):
            if (item["t"]!=index or item["original_selected_action"] not in (0,1,2) or
                set(item["public_before"])!=PUBLIC or set(item["public_after"])!=PUBLIC):
                raise ValueError("C37_SOURCE_EVENT_NOT_PUBLIC")
            if index and events[index-1]["public_after"]!=item["public_before"]:
                raise ValueError("C37_SOURCE_CHRONOLOGY_BROKEN")
        if episode["real_step3_process_cold"]["cold_OS_source_policy_parity"] is not True:
            raise ValueError("C37_RESTART_UNVERIFIED")
    if len(seen)!=len(PROTOCOL["arms"])*24:
        raise ValueError("C37_INCOMPLETE_FACTORIAL_COVERAGE")

def compare(first,second):
    check(first);check(second)
    a=dict(first);b=dict(second)
    a.pop("resource_observation",None);b.pop("resource_observation",None)
    identical=canonical(a)==canonical(b)
    return {"science_identical":identical,
            "source_A":first["scientific_result"],
            "source_B":second["scientific_result"],
            "scientific_accepted":False,"first_use":False,
            "result":("REPEATED_BOUNDED_C37_CAUSAL_MEMORY_SOURCE_FIT_SIGNAL_NOT_TRANSFER"
              if identical and first["scientific_result"]==second["scientific_result"]==PROTOCOL["preregAccept"]["positive"]
              else "NO_REPEATABLE_C37_CAUSAL_MEMORY_NATIVE_SUPERIORITY")}

def main():
    parser=argparse.ArgumentParser()
    for name in ("first","second","output"):
        parser.add_argument("--"+name,type=Path,required=True)
    options=parser.parse_args()
    if options.output.exists():raise ValueError("C37_REPORT_ALREADY_EXISTS")
    result=compare(json.loads(options.first.read_text()),json.loads(options.second.read_text()))
    options.output.write_bytes(canonical(result)+b"\n")
    print("C37_ORIGINAL_SOURCE_REPEAT="+result["result"])
    if not result["science_identical"]:raise SystemExit(1)

if __name__=="__main__":main()

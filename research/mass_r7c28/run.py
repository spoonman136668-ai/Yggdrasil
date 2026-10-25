"""C28: authentic original-source FIT-only action/consequence ledger.

The unchanged C25 NativeActive policy acts in real, pinned Farama MiniGrid.
C25 run_family returns each actually selected action and source-returned
public successor/reward. This adds a complete public FIT ledger and NOTHING
that uses a new DEV/VALID/protected cohort. It is data custody, not learning.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from research.mass_r7c20 import run as c20
from research.mass_r7c25 import run as c25
from research.native.itd02.r1.native_policy import canonical

P = json.loads((HERE / "PREREG.json").read_text(encoding="utf-8"))
TYPES = ("left", "right", "forward")


def _git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify_source_custody() -> None:
    for path, blob in (
        ("research/native/itd02/r1/native_policy.py", P["original_source"]["native_r1_blob"]),
        ("research/native/itd02/r2/affordance_cells.py", P["original_source"]["native_r2_blob"]),
        ("research/native/itd02/r3/navigator.py", P["original_source"]["native_r3_blob"]),
        (P["frozen_motor_fit"]["selector"], P["frozen_motor_fit"]["blob"]),
    ):
        data = (ROOT / path).read_bytes().replace(bytes((13, 10)), bytes((10,)))
        if _git_blob(data) != blob:
            raise ValueError("FIT_SOURCE_IDENTITY_DRIFT:" + path)
    c20.check_source()


def validate_episode(family: str, seed: int, rows: list, cap: int) -> tuple[list[dict], dict]:
    """Fail closed on malformed, nonchronological, or attributed source events.

    This alone does not authenticate a simulator; its provenance depends on the
    preceding pinned-original source invocation and unmodified C25 collector.
    """
    if type(family) is not str or family not in P["new_fit_episodes"]:
        raise ValueError("NONFROZEN_FIT_FAMILY")
    if type(seed) is not int or seed not in P["new_fit_episodes"][family]:
        raise ValueError("NONFROZEN_FIT_SEED")
    if type(rows) is not list or not rows or len(rows) > cap:
        raise ValueError("SOURCE_EVENT_COUNT_INVALID")
    events = []
    previous_after = None
    goal = None
    counts = Counter()
    info = Counter()
    final = None
    for step, row in enumerate(rows):
        if type(row) is not list or len(row) != 15:
            raise ValueError("ILLEGAL_SOURCE_PUBLIC_EVENT_SCHEMA")
        bx,by,bd,gx,gy,bblocked,a,is_probe,nx,ny,nd,nblocked,reward,done,trunc = row
        if any(type(x) is not int for x in (bx,by,bd,gx,gy,bblocked,a,is_probe,nx,ny,nd,nblocked,done,trunc)):
            raise ValueError("NONINTEGER_OR_BOOL_PUBLIC_FIELD")
        if (a not in (0,1,2) or is_probe not in (0,1) or bblocked not in (0,1)
            or nblocked not in (0,1) or done not in (0,1) or trunc not in (0,1)):
            raise ValueError("ILLEGAL_ACTION_OR_PUBLIC_BOOLEAN")
        if any(x<0 or x>31 for x in (bx,by,gx,gy,nx,ny)) or bd not in range(4) or nd not in range(4):
            raise ValueError("SOURCE_PUBLIC_POSE_OUT_OF_BOUNDS")
        if type(reward) not in (float,int) or not math.isfinite(reward):
            raise ValueError("MALFORMED_SOURCE_REWARD")
        if goal is None:
            goal=(gx,gy)
        if goal!=(gx,gy):
            raise ValueError("GOAL_CHANGED_WITHIN_SOURCE_EPISODE")
        before=(bx,by,bd)
        after=(nx,ny,nd)
        if previous_after is not None and before!=previous_after:
            raise ValueError("BROKEN_ACTION_OUTCOME_SEQUENCE")
        if a in (0,1):
            if (bx,by)!=(nx,ny) or nd!=(bd+(-1 if a==0 else 1))%4:
                raise ValueError("TURN_SOURCE_EFFECT_VIOLATION")
        else:
            if nd!=bd or abs(nx-bx)+abs(ny-by)>1:
                raise ValueError("FORWARD_SOURCE_EFFECT_VIOLATION")
        if is_probe and a not in (0,1):
            raise ValueError("INVALID_INFORMATION_TURN_ACTION")
        if done and trunc:
            raise ValueError("INCONSISTENT_SOURCE_TERMINATION")
        if final:
            raise ValueError("EVENT_AFTER_TERMINAL_RETURN")
        counts[TYPES[a]]+=1
        if is_probe:
            info["blocked" if nblocked else "clear"]+=1
        event={
            "family":family,"seed":seed,"step":step,
            "before":{"x":bx,"y":by,"direction":bd,"goal_x":gx,"goal_y":gy,"front_blocked":bool(bblocked)},
            "chosen_action":a,"information_turn":bool(is_probe),
            "returned_after":{"x":nx,"y":ny,"direction":nd,"goal_x":gx,"goal_y":gy,"front_blocked":bool(nblocked)},
            "returned_reward":float(reward),"terminated":bool(done),"truncated":bool(trunc)
        }
        events.append(event)
        previous_after=after
        final=bool(done or trunc)
    return events, {"family":family,"seed":seed,"episodes":1,"actions":len(events),
      "action_family_counts":{name:counts[name] for name in TYPES},
      "information_turn_returned_front":{"clear":info["clear"],"blocked":info["blocked"]},
      "last_return_terminal":bool(final),
      "source_public_event_sha256":hashlib.sha256(canonical(events)).hexdigest()}


def fit_ledger() -> dict:
    import gymnasium, minigrid  # original package only used within genuine FIT runner
    verify_source_custody()
    timer=time.process_time()
    selected,old_sha,source_counts=c20.fit_data()
    if old_sha != P["frozen_motor_fit"]["original_fit_selected_sha256"] or len(selected)!=12:
        raise ValueError("ORIGINAL_FROZEN_MOTOR_FIT_DRIFT")
    if any(type(row[2]) is not int or row[2]!=2 for row in selected):
        raise ValueError("FROZEN_MOTOR_FIT_HAS_UNEXPECTED_TURN")
    bootstrap_cpu=time.process_time()-timer
    model=c25.make("native_active",selected)
    events, episode_receipts=[],[]
    total=Counter()
    returned=Counter()
    for family,seeds in P["new_fit_episodes"].items():
        totals,source_episodes=c25.run_family("native_active",model,family,seeds)
        if totals["episodes"]!=len(seeds):
            raise ValueError("SOURCE_FIT_EPISODE_COUNT_MISMATCH")
        if [row["seed"] for row in source_episodes]!=seeds:
            raise ValueError("SOURCE_FIT_ORDER_AND_IDENTITY_MISMATCH")
        for ep in source_episodes:
            if hashlib.sha256(canonical(ep["trace"])).hexdigest()!=ep["trace_sha256"]:
                raise ValueError("SOURCE_C25_RAW_TRACE_SHA256_MISMATCH")
            ev,receipt=validate_episode(family,ep["seed"],ep["trace"],c25.P["actions_per_episode_cap"])
            if len(ev)!=ep["steps"]:
                raise ValueError("SOURCE_ACTION_COUNT_MISMATCH")
            events.extend(ev);episode_receipts.append(receipt)
            total.update(receipt["action_family_counts"])
            returned.update(receipt["information_turn_returned_front"])
    if len(episode_receipts)!=sum(len(s) for s in P["new_fit_episodes"].values()):
        raise ValueError("NEW_FIT_COHORT_NOT_COMPLETE")
    coverage=all(total[name]>0 for name in TYPES)
    both_information_labels=returned["blocked"]>0 and returned["clear"]>0
    payload={
       "schema":P["schema"],"classification":P["classification"],
       "protocol_sha256":hashlib.sha256((HERE/"PREREG.json").read_bytes()).hexdigest(),
       "original_source":P["original_source"]["upstream"],
       "bootstrap_previous_source_actions":source_counts,
       "bootstrap_selected_fit_action_counts":P["frozen_motor_fit"]["selection_12_action_counts"],
       "bootstrap_selected_fit_sha256":old_sha,
       "source_fit_episodes":episode_receipts,"source_fit_events":events,
       "source_fit_action_counts":{name:total[name] for name in TYPES},
       "source_fit_information_front_counts":{label:returned[label] for label in ("clear","blocked")},
       "source_action_coverage":coverage,
       "new_front_clear_and_blocked_coverage":both_information_labels,
       "learning_value_of_information_executed":False,
       "original_new_dev_episodes":0,"protected_first_use_episodes":0,
       "scientific_status":("FIT_SOURCE_DATA_READY_FOR_SEPARATE_LEARNER_GATE" if coverage and both_information_labels
          else "NO_GO_FIT_ACTION_OR_INFORMATION_CONTRAST_INSUFFICIENT"),
       "source_fit_event_ledger_sha256":hashlib.sha256(canonical(events)).hexdigest(),
    }
    print("C28_OLD_BOOTSTRAP_MOTOR_SELECTED_FORWARD_ONLY=12",flush=True)
    print("C28_NEW_ORIGINAL_FIT_ACTION_COUNTS="+json.dumps(payload["source_fit_action_counts"],sort_keys=True),flush=True)
    print("C28_NEW_ORIGINAL_FIT_INFORMATION_FRONT_COUNTS="+json.dumps(payload["source_fit_information_front_counts"],sort_keys=True),flush=True)
    print("C28_REAL_FIT_LEDGER_DECISION="+payload["scientific_status"],flush=True)
    payload["cpu_bootstrap_seconds"]=round(bootstrap_cpu,6)
    payload["cpu_whole_process_seconds"]=round(time.process_time()-timer,6)
    payload["peak_process_rss_kib"]=__import__("resource").getrusage(__import__("resource").RUSAGE_SELF).ru_maxrss
    return payload


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    value=fit_ledger()
    Path(args.out).write_bytes(canonical(value)+b"\n")


if __name__=="__main__":
    main()

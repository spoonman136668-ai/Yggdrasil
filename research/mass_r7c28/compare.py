"""C28 reconcile two independent REAL original-source FIT-only event collections."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from research.mass_r7c28.run import P, HERE, TYPES, validate_episode
from research.native.itd02.r1.native_policy import canonical

folder=Path(sys.argv[1])
records=[json.loads((folder/f"original-fit-{i}.json").read_text(encoding="utf-8")) for i in (1,2)]
expected_digest=hashlib.sha256((HERE/"PREREG.json").read_bytes()).hexdigest()
ignore_metrics={"cpu_bootstrap_seconds","cpu_whole_process_seconds","peak_process_rss_kib"}


def audit(value):
    if value.get("schema")!=P["schema"] or value.get("classification")!=P["classification"]:
        raise ValueError("FIT_LEDGER_SCHEMA_OR_ROLE_DRIFT")
    if value.get("protocol_sha256")!=expected_digest:
        raise ValueError("FIT_FROZEN_PROTOCOL_DRIFT")
    if value.get("original_source")!=P["original_source"]["upstream"]:
        raise ValueError("FIT_UPSTREAM_IDENTITY_DRIFT")
    if value.get("bootstrap_selected_fit_sha256")!=P["frozen_motor_fit"]["original_fit_selected_sha256"]:
        raise ValueError("FIT_BASE_MOTOR_IDENTITY_DRIFT")
    if value.get("bootstrap_selected_fit_action_counts")!=P["frozen_motor_fit"]["selection_12_action_counts"]:
        raise ValueError("FIT_BASE_MOTOR_ACTION_GRAMMAR_DRIFT")
    if value.get("original_new_dev_episodes")!=0 or value.get("protected_first_use_episodes")!=0:
        raise ValueError("FIT_ROLE_ESCAPE_PROTECTED_OR_DEVELOPMENT")
    if value.get("learning_value_of_information_executed") is not False:
        raise ValueError("FAKE_LEARNED_CAUSAL_RESULT")
    events=value.get("source_fit_events")
    receipts=value.get("source_fit_episodes")
    if type(events) is not list or type(receipts) is not list:
        raise ValueError("INCOMPLETE_ORIGINAL_SOURCE_FIT_LEDGER")
    if hashlib.sha256(canonical(events)).hexdigest()!=value.get("source_fit_event_ledger_sha256"):
        raise ValueError("FIT_LEDGER_HASH_MISMATCH")
    expected_pair=[(fam,seed) for fam,seeds in P["new_fit_episodes"].items() for seed in seeds]
    pair=[(r.get("family"),r.get("seed")) for r in receipts]
    if pair!=expected_pair:
        raise ValueError("FIT_MISSING_DUPLICATE_OR_REORDERED_EPISODE")
    selected=Counter()
    info=Counter()
    pos=0
    for r in receipts:
        count=r.get("actions")
        chunk=events[pos:pos+count] if type(count) is int and count>0 else []
        pos+=len(chunk)
        if not chunk:
            raise ValueError("FIT_EMPTY_SELECTED_SOURCE_TRACE")
        rows=[]
        for step,e in enumerate(chunk):
            if type(e) is not dict or set(e)!={"family","seed","step","before","chosen_action",
               "information_turn","returned_after","returned_reward","terminated","truncated"}:
                raise ValueError("PUBLIC_EVENT_EXTRA_OR_MISSING_KEYS")
            if (e["family"],e["seed"],e["step"])!=(r["family"],r["seed"],step):
                raise ValueError("FIT_RETURN_ACTION_IDENTITY_CHANGED")
            b=e["before"];n=e["returned_after"]
            keys={"x","y","goal_x","goal_y","direction","front_blocked"}
            if type(b) is not dict or type(n) is not dict or set(b)!=keys or set(n)!=keys:
                raise ValueError("PRIVATE_OR_INCOMPLETE_PUBLIC_STATE")
            if any(type(b[k]) is not int or type(n[k]) is not int for k in (
                "x","y","direction","goal_x","goal_y")):
                raise ValueError("CORRUPT_ORIGINAL_PUBLIC_COORD")
            if type(b["front_blocked"]) is not bool or type(n["front_blocked"]) is not bool:
                raise ValueError("CORRUPT_ORIGINAL_PUBLIC_FRONT_STATUS")
            if type(e["information_turn"]) is not bool or type(e["terminated"]) is not bool or type(e["truncated"]) is not bool:
                raise ValueError("ILLEGAL_BOOLEAN_TYPE")
            if type(e["chosen_action"]) is not int or type(e["returned_reward"]) not in (float,int):
                raise ValueError("ILLEGAL_SELECTED_ACTION_OR_REWARD")
            rows.append([b["x"],b["y"],b["direction"],b["goal_x"],b["goal_y"],
             int(b["front_blocked"]),e["chosen_action"],int(e["information_turn"]),
             n["x"],n["y"],n["direction"],int(n["front_blocked"]),
             float(e["returned_reward"]),int(e["terminated"]),int(e["truncated"])])
        validated, expected=validate_episode(r["family"],r["seed"],rows,len(rows))
        if validated!=chunk or any(r.get(k)!=v for k,v in expected.items()):
            raise ValueError("ORIGINAL_EVENT_OR_EPISODE_RECEIPT_MISMATCH")
        selected.update(expected["action_family_counts"])
        info.update(expected["information_turn_returned_front"])
    if pos!=len(events):
        raise ValueError("UNCLAIMED_SOURCE_PUBLIC_ACTIONS")
    if {a:selected[a] for a in TYPES}!=value.get("source_fit_action_counts"):
        raise ValueError("FIT_SOURCE_ACTION_COVERAGE_MISMATCH")
    if {a:info[a] for a in ("clear","blocked")}!=value.get("source_fit_information_front_counts"):
        raise ValueError("FIT_SOURCE_INFORMATION_COVERAGE_MISMATCH")
    if value["source_action_coverage"]!=all(selected[a]>0 for a in TYPES):
        raise ValueError("FIT_ACTION_GATE_MISMATCH")
    if value["new_front_clear_and_blocked_coverage"]!=(info["clear"]>0 and info["blocked"]>0):
        raise ValueError("FIT_INFORMATION_GATE_MISMATCH")
    expected_status=("FIT_SOURCE_DATA_READY_FOR_SEPARATE_LEARNER_GATE" if
        value["source_action_coverage"] and value["new_front_clear_and_blocked_coverage"]
        else "NO_GO_FIT_ACTION_OR_INFORMATION_CONTRAST_INSUFFICIENT")
    if value["scientific_status"]!=expected_status:
        raise ValueError("FIT_SCIENTIFIC_DISPOSITION_INCORRECT")
    return {"events":pos,"actions":dict(selected),"information":dict(info),
        "status":expected_status}


left,right=records
a,b=audit(left),audit(right)
non_resource=lambda x:{k:v for k,v in x.items() if k not in ignore_metrics}
if non_resource(left)!=non_resource(right):
    raise ValueError("INDEPENDENT_ORIGINAL_SOURCE_FIT_PROCESSES_DIVERGED")
report={
 "schema":"itd02.c28.authenticated-original-fit-two-run-reconciliation.v1",
 "source":P["original_source"]["upstream"],
 "prereg_sha256":expected_digest,
 "actual_original_fit_processes":2,
 "exact_source_event_repetition":True,
 "new_original_source_fit_episodes":len(left["source_fit_episodes"]),
 "new_source_selected_events":a["events"],
 "selected_left_right_forward":a["actions"],
 "info_turn_revealed_front_counts":a["information"],
 "original_source_fit_event_sha256":left["source_fit_event_ledger_sha256"],
 "original_dev_episodes":0,
 "protected_first_use_episodes":0,
 "learned_native_exploration_superiority":"NOT_EVALUATED",
 "scientific_disposition":a["status"]
}
data=canonical(report)
(folder/"comparison.json").write_bytes(data+b"\n")
print("C28_ORIGINAL_SOURCE_DUAL_PROCESS_FIT_RECONCILIATION=PASS",flush=True)
print("C28_NEW_AUTHENTIC_SELECTED_FIT_ACTIONS="+json.dumps(a["actions"],sort_keys=True),flush=True)
print("C28_SOURCE_FIT_INFORMATION_CONTRAST="+json.dumps(a["information"],sort_keys=True),flush=True)
print("C28_RECONCILIATION_SHA256="+hashlib.sha256(data).hexdigest(),flush=True)
print("C28_SCIENTIFIC_DISPOSITION="+a["status"],flush=True)
print("C28_ORIGINAL_NEW_DEV=0",flush=True)
print("C28_PROTECTED_FIRST_USE=0",flush=True)

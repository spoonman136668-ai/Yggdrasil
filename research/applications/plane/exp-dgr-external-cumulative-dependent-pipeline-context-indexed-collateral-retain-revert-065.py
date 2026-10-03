"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAIN-REVERT-065."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAIN-REVERT-065"
PRIOR_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-coalition-064.py")
CORRECT_KEY=(10,32,32,32)
WRONG_KEY=(97,116,105,111)

def load_prior():
    s=importlib.util.spec_from_file_location("ygg064",PRIOR_PATH)
    if s is None or s.loader is None:raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def supported_contract(m):
    return (
        m["gate_use_schedule_count"]==2 and
        m["gate_noop_schedule_count"]==2 and
        m["retained_memory_donor_missing_count"]==0 and
        m["candidate_reserved_key_missing_count"]==0 and
        m["candidate_positive_prose_collateral_schedule_count"]==4 and
        m["candidate_partner_collateral_failure_count"]==0 and
        m["candidate_schedule_slower_than_baseline_count"]==0 and
        m["candidate_mean_packet_reduction"]>=1 and
        m["preserved_state_structure_count_min"]==16 and
        m["active_structure_count_min"]==7 and
        m["retained_structure_count_min"]==9 and
        m["capacity_growth_event_count"]==0 and
        m["invalid_evaluation_rows"]==0
    )

def state_bytes(key):
    state={
        "schema":"yggdrasil.ephemeral-research-candidate-state.v1",
        "experiment_parent":"EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-COALITION-064",
        "retained_key":list(key),
        "retained_row_slots":1,
        "physical_structure_count":16,
        "active_structure_count":7,
        "retained_structure_count":9,
        "persistent":False,
        "production_authority":False,
    }
    return json.dumps(state,sort_keys=True,separators=(",",":")).encode("utf-8")

def run(root):
    p64=load_prior()
    original_key=tuple(p64.RETAINED_KEY)
    if original_key!=CORRECT_KEY:raise RuntimeError("PRIOR_RETAINED_KEY_IDENTITY_MISMATCH")
    snapshot=state_bytes(CORRECT_KEY)
    metrics={
        "wrong_candidate_retain_count":0.0,
        "wrong_candidate_revert_count":0.0,
        "rollback_snapshot_mismatch_count":0.0,
        "correct_candidate_retain_count":0.0,
        "correct_candidate_revert_count":0.0,
        "correct_result_mismatch_vs_064_contract_count":0.0,
        "wrong_and_correct_retained_slot_count":1.0,
        "capacity_growth_event_count":0.0,
        "persistent_state_write_count":0.0,
        "accepted_ref_mutation_count":0.0,
        "production_authority_count":0.0,
        "invalid_evaluation_rows":0.0,
    }

    p64.RETAINED_KEY=WRONG_KEY
    wrong=p64.run(root)
    wm=wrong["metrics"]
    wrong_pass=supported_contract(wm)
    if wrong_pass:
        metrics["wrong_candidate_retain_count"]+=1.0
        restored=state_bytes(WRONG_KEY)
    else:
        metrics["wrong_candidate_revert_count"]+=1.0
        restored=bytes(snapshot)
    if restored!=snapshot:
        metrics["rollback_snapshot_mismatch_count"]+=1.0

    if metrics["wrong_candidate_retain_count"]!=0:
        metrics["invalid_evaluation_rows"]+=1.0
        correct=None
        cm={}
        correct_pass=False
    else:
        p64.RETAINED_KEY=CORRECT_KEY
        correct=p64.run(root)
        cm=correct["metrics"]
        correct_pass=supported_contract(cm)
        if correct_pass:metrics["correct_candidate_retain_count"]+=1.0
        else:
            metrics["correct_candidate_revert_count"]+=1.0
            metrics["correct_result_mismatch_vs_064_contract_count"]+=1.0

    p64.RETAINED_KEY=original_key
    for child in (wm,cm):
        if not child:continue
        metrics["capacity_growth_event_count"]+=float(child.get("capacity_growth_event_count",0.0))
        metrics["invalid_evaluation_rows"]+=float(child.get("invalid_evaluation_rows",0.0))
    if len(WRONG_KEY)!=4 or len(CORRECT_KEY)!=4:
        metrics["invalid_evaluation_rows"]+=1.0
    if metrics["wrong_and_correct_retained_slot_count"]!=1:
        metrics["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in metrics.values())
    return {
        "schema":"yggdrasil.research-scientific-result.v1",
        "experiment":EXPERIMENT,
        "metrics":metrics,
        "diagnostics":{
            "pre_candidate_snapshot":snapshot.decode("utf-8"),
            "wrong_candidate":{"retained_key":list(WRONG_KEY),"supported_contract":wrong_pass,"metrics":wm},
            "correct_candidate":{"retained_key":list(CORRECT_KEY),"supported_contract":correct_pass,"metrics":cm},
        },
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))

if __name__=="__main__":main()

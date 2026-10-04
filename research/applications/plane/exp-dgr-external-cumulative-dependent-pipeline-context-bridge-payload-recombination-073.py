"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-PAYLOAD-RECOMBINATION-073."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-PAYLOAD-RECOMBINATION-073"
P072=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-bridge-translation-072.py")
P068=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.py")
BRIDGE_KEYS=((32,116,104,101),(32,97,110,100))
SOURCE_PAYLOAD={"best":32,"total":112,"best_count":112,"consistency":1.0,"utility":112.0,"cell_index":12,"map_best":32}

def load_mod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise RuntimeError("IMPORT_SPEC_FAILED:"+name)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def bridge_state(key):
    return {"key":tuple(key),**SOURCE_PAYLOAD}

FORCE_NEEDLE='''        missing=[k for k in required if k not in keys]
        if not missing:return out,om
'''
FORCE_REPL='''        force=[k for k in required if k in BRIDGE_KEYS and k in dby]
        for k in force:
            if k in keys:
                out=[r for r in out if r["key"]!=k];om.pop(k,None);keys.discard(k)
            r=dby.get(k)
            if r is None or k not in donor_map:
                m["retained_memory_donor_missing_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
            else:
                out.append(r);om[k]=donor_map[k];keys.add(k)
        missing=[k for k in required if k not in keys]
        if not missing:
            if len(out)!=16 or len({r["key"] for r in out})!=16 or len(om)!=16:
                m["candidate_state_capacity_failure_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
            return out,om
'''
STATE_NEEDLE='''    transported_row={"key":RETAINED_KEY,"best":RETAINED_STATE["best"],"total":RETAINED_STATE["total"],"best_count":RETAINED_STATE["best_count"],"consistency":RETAINED_STATE["consistency"],"utility":RETAINED_STATE["utility"],"cell_index":RETAINED_STATE["cell_index"]}
    transported_map={RETAINED_KEY:RETAINED_STATE["map_best"]}
    if transported_row["best"]!=transported_map[RETAINED_KEY] or tuple(RETAINED_STATE["key"])!=RETAINED_KEY:
        m["transported_state_identity_mismatch_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
'''
STATE_REPL='''    transported_rows=[{"key":k,"best":SOURCE_PAYLOAD["best"],"total":SOURCE_PAYLOAD["total"],"best_count":SOURCE_PAYLOAD["best_count"],"consistency":SOURCE_PAYLOAD["consistency"],"utility":SOURCE_PAYLOAD["utility"],"cell_index":SOURCE_PAYLOAD["cell_index"]} for k in BRIDGE_KEYS]
    transported_map={k:SOURCE_PAYLOAD["map_best"] for k in BRIDGE_KEYS}
    for r in transported_rows:
        if r["best"]!=transported_map[r["key"]]:
            m["transported_state_identity_mismatch_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
'''
COMBINED_NEEDLE='''        combined_by={r["key"]:r for r in hrows};combined_map=dict(hmap)
        if RETAINED_KEY not in combined_by:
            combined_by[RETAINED_KEY]=transported_row;combined_map[RETAINED_KEY]=transported_map[RETAINED_KEY]
        combined_rows=list(combined_by.values())

        if RETAINED_KEY in original_guard:
            active_guard=original_guard;active_used=False
        else:
            active_guard=tuple(list(original_guard[:6])+[RETAINED_KEY]);active_used=True
            m["active_transport_use_schedule_count"]+=1.0
'''
COMBINED_REPL='''        combined_by={r["key"]:r for r in hrows};combined_map=dict(hmap)
        for r in transported_rows:
            combined_by[r["key"]]=r;combined_map[r["key"]]=transported_map[r["key"]]
        combined_rows=list(combined_by.values())

        active_list=list(original_guard)
        missing=[k for k in BRIDGE_KEYS if k not in active_list]
        for _ in missing:
            drop=None
            for j in range(len(active_list)-1,-1,-1):
                if active_list[j] not in BRIDGE_KEYS:
                    drop=j;break
            if drop is None:
                m["invalid_evaluation_rows"]+=1.0;break
            active_list.pop(drop)
        for k in missing:
            active_list.append(k)
        active_guard=tuple(active_list)
        active_used=(active_guard!=original_guard)
        if active_used:m["active_transport_use_schedule_count"]+=1.0
'''
PASSIVE_NEEDLE='''            passive_required=tuple(dict.fromkeys(carry+original_guard+(RETAINED_KEY,)))
'''
PASSIVE_REPL='''            passive_required=tuple(dict.fromkeys(carry+original_guard+BRIDGE_KEYS))
'''

def run_coalition(root):
    source=P068.read_text(encoding="utf-8")
    checks=((FORCE_NEEDLE,FORCE_REPL),(STATE_NEEDLE,STATE_REPL),(COMBINED_NEEDLE,COMBINED_REPL),(PASSIVE_NEEDLE,PASSIVE_REPL))
    for needle,_ in checks:
        if source.count(needle)!=1:raise RuntimeError("P068_COALITION_PATCH_TARGET_NOT_EXACT")
    for needle,repl in checks:source=source.replace(needle,repl,1)
    ns={"__name__":"p068_y73_coalition","__file__":str(P068),"BRIDGE_KEYS":BRIDGE_KEYS,"SOURCE_PAYLOAD":dict(SOURCE_PAYLOAD)}
    exec(compile(source,str(P068),"exec"),ns)
    return ns["run"](root)

def changed(child):
    m=child["metrics"]
    if m["active_positive_prose_collateral_schedule_count"]!=m["original_positive_prose_collateral_schedule_count"]:return True
    if m["active_mean_first_success_packet"]!=m["original_mean_first_success_packet"]:return True
    if m["active_partner_collateral_failure_count"]!=m["original_partner_collateral_failure_count"]:return True
    for d in child.get("diagnostics",[]):
        for p in d.get("packets",[]):
            if p["active"]!=p["original"]:return True
    return False

def run(root):
    m={
      "source_identity_mismatch_count":0.0,"source_payload_identity_mismatch_count":0.0,
      "trigger_identity_mismatch_count":0.0,"coalition_trigger_count":2.0,"bridge_row_count":2.0,
      "bridge_payload_mutation_count":0.0,"arbitrary_payload_synthesis_count":0.0,
      "persistent_state_write_count":0.0,"heldout_selection_count":0.0,
      "original_positive_prose_collateral_schedule_count":0.0,
      "single_positive_prose_collateral_schedule_count":0.0,
      "coalition_positive_prose_collateral_schedule_count":0.0,
      "single_partner_collateral_failure_count":0.0,"coalition_partner_collateral_failure_count":0.0,
      "single_mean_first_success_packet":0.0,"coalition_mean_first_success_packet":0.0,
      "single_behavior_change_count":0.0,"coalition_behavior_change_count":0.0,
      "all_child_source_identity_mismatch_count":0.0,"all_child_manifest_identity_mismatch_count":0.0,
      "capacity_growth_event_count":0.0,"invalid_evaluation_rows":0.0,
    }
    p72=load_mod("p072_y73",P072)
    if tuple(p72.EXPECTED[0]["key"])!=BRIDGE_KEYS[0] or tuple(p72.EXPECTED[1]["key"])!=BRIDGE_KEYS[1]:
        m["trigger_identity_mismatch_count"]+=1.0
    for k,v in SOURCE_PAYLOAD.items():
        if k=="map_best":
            if p72.SOURCE_STATE["map_best"]!=v:m["source_payload_identity_mismatch_count"]+=1.0
        elif p72.SOURCE_STATE[k]!=v:m["source_payload_identity_mismatch_count"]+=1.0
    single_trigger={"rank":1,"key":BRIDGE_KEYS[0]}
    single=p72.run_bridge(root,single_trigger)
    coalition=run_coalition(root)
    sm=single["metrics"];cm=coalition["metrics"]
    m["original_positive_prose_collateral_schedule_count"]=float(sm["original_positive_prose_collateral_schedule_count"])
    if float(cm["original_positive_prose_collateral_schedule_count"])!=m["original_positive_prose_collateral_schedule_count"]:
        m["invalid_evaluation_rows"]+=1.0
    m["single_positive_prose_collateral_schedule_count"]=float(sm["active_positive_prose_collateral_schedule_count"])
    m["coalition_positive_prose_collateral_schedule_count"]=float(cm["active_positive_prose_collateral_schedule_count"])
    m["single_partner_collateral_failure_count"]=float(sm["active_partner_collateral_failure_count"])
    m["coalition_partner_collateral_failure_count"]=float(cm["active_partner_collateral_failure_count"])
    m["single_mean_first_success_packet"]=float(sm["active_mean_first_success_packet"])
    m["coalition_mean_first_success_packet"]=float(cm["active_mean_first_success_packet"])
    if changed(single):m["single_behavior_change_count"]=1.0
    if changed(coalition):m["coalition_behavior_change_count"]=1.0
    m["capacity_growth_event_count"]=float(sm["capacity_growth_event_count"])+float(cm["capacity_growth_event_count"])
    m["all_child_source_identity_mismatch_count"]=float(sm["source_identity_mismatch_count"])+float(cm["source_identity_mismatch_count"])
    m["all_child_manifest_identity_mismatch_count"]=float(sm["transfer_manifest_identity_mismatch_count"])+float(cm["transfer_manifest_identity_mismatch_count"])
    m["invalid_evaluation_rows"]+=float(sm["invalid_evaluation_rows"]+sm["transported_state_identity_mismatch_count"])
    m["invalid_evaluation_rows"]+=float(cm["invalid_evaluation_rows"]+cm["transported_state_identity_mismatch_count"])
    if m["trigger_identity_mismatch_count"]!=0 or m["source_payload_identity_mismatch_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    if m["all_child_source_identity_mismatch_count"]!=0 or m["all_child_manifest_identity_mismatch_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    if m["capacity_growth_event_count"]!=0 or m["persistent_state_write_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {
      "schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,
      "metrics":m,
      "source_payload":dict(SOURCE_PAYLOAD),
      "coalition_keys":[list(k) for k in BRIDGE_KEYS],
      "single_diagnostics":single["diagnostics"],
      "coalition_diagnostics":coalition["diagnostics"],
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":main()

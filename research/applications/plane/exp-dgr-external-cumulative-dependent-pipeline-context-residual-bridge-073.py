"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-RESIDUAL-BRIDGE-073."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-RESIDUAL-BRIDGE-073"
P071=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-factorial-071.py")
P068=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.py")
SOURCE_STATE={"key":(10,32,32,32),"best":32,"total":112,"best_count":112,"consistency":1.0,"utility":112.0,"cell_index":12,"map_best":32}
FORCE_NEEDLE='''        missing=[k for k in required if k not in keys]
        if not missing:return out,om
'''
FORCE_REPL='''        force=[k for k in required if k==RETAINED_KEY and k in dby]
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
COMBINED_NEEDLE='''        combined_by={r["key"]:r for r in hrows};combined_map=dict(hmap)
        if RETAINED_KEY not in combined_by:
            combined_by[RETAINED_KEY]=transported_row;combined_map[RETAINED_KEY]=transported_map[RETAINED_KEY]
        combined_rows=list(combined_by.values())
'''
COMBINED_REPL='''        combined_by={r["key"]:r for r in hrows};combined_map=dict(hmap)
        combined_by[RETAINED_KEY]=transported_row;combined_map[RETAINED_KEY]=transported_map[RETAINED_KEY]
        combined_rows=list(combined_by.values())
'''

def load_mod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise RuntimeError("IMPORT_SPEC_FAILED:"+name)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def load_learner_and_base():
    p71=load_mod("p071_y73_chain",P071)
    p70=p71.load_mod("p070_y73_chain",p71.P070)
    p20=p70.load_mod("p020_y73_chain",p70.P020)
    p17=p20.load_prior_experiment();p16=p17.load_prior_experiment();p15=p16.load_prior_experiment()
    p14=p15.load_prior_experiment();p13=p14.load_prior_experiment();ad=p13.load_prior_experiment()
    eg=ad.load_prior_experiment();wake=eg.load_wake();pressure=wake.load_pressure();learner=pressure.load_prior()
    bt=[];mismatch=0
    for p,h in learner.TRAIN_FILES:
        x,ok=learner.load_checked(p,h);bt.append(x);mismatch+=int(not ok)
    return learner,learner.baseline_train(bt),mismatch

def successor_info(buf,key,baseline):
    counts=[0]*256;occ=0
    for i in range(0,max(0,len(buf)-3)):
        if tuple(buf[i:i+4])!=key:continue
        occ+=1
        if i+4<len(buf):counts[buf[i+4]]+=1
    best_alt=-1;alt_count=0
    for b,c in enumerate(counts):
        if b==baseline:continue
        if c>alt_count or (c==alt_count and c>0 and (best_alt<0 or b<best_alt)):
            best_alt=b;alt_count=c
    return occ,best_alt,alt_count

def adapter_state(key,best):
    return {"key":tuple(key),"best":int(best),"total":SOURCE_STATE["total"],"best_count":SOURCE_STATE["best_count"],
            "consistency":SOURCE_STATE["consistency"],"utility":SOURCE_STATE["utility"],"cell_index":SOURCE_STATE["cell_index"],"map_best":int(best)}

def run_adapter(root,trig):
    source=P068.read_text(encoding="utf-8")
    if source.count(FORCE_NEEDLE)!=1 or source.count(COMBINED_NEEDLE)!=1:raise RuntimeError("P068_PATCH_TARGET_NOT_EXACT")
    source=source.replace(FORCE_NEEDLE,FORCE_REPL,1).replace(COMBINED_NEEDLE,COMBINED_REPL,1)
    ns={"__name__":"p068_y73_"+str(trig["rank"]),"__file__":str(P068)}
    exec(compile(source,str(P068),"exec"),ns)
    ns["RETAINED_KEY"]=tuple(trig["key"]);ns["RETAINED_STATE"]=adapter_state(trig["key"],trig["alt_best"])
    return ns["run"](root)

def behavior_changed(child):
    for d in child.get("diagnostics",[]):
        for p in d.get("packets",[]):
            if p["active"]!=p["original"]:return True
    return False

def run(root):
    m={"source_identity_mismatch_count":0.0,"induction_source_count":0.0,"induction_source_bytes":0.0,
       "base_training_identity_mismatch_count":0.0,"history_byte_budget_mismatch_count":0.0,
       "source_role_override_verified":0.0,"source_baseline_prediction":0.0,"source_best":32.0,
       "candidate_count":0.0,"eligible_candidate_count":0.0,"heldout_selection_count":0.0,
       "selected_trigger_rank":0.0,"selected_compatibility_score":0.0,"selected_alt_best":0.0,
       "alternate_trigger_rank":0.0,"alternate_compatibility_score":0.0,"alternate_alt_best":0.0,
       "selected_behavior_change_count":0.0,"alternate_behavior_change_count":0.0,
       "original_positive_prose_collateral_schedule_count":0.0,
       "selected_positive_prose_collateral_schedule_count":0.0,"alternate_positive_prose_collateral_schedule_count":0.0,
       "selected_partner_collateral_failure_count":0.0,"alternate_partner_collateral_failure_count":0.0,
       "persistent_source_state_mutation_count":0.0,"persistent_adapter_write_count":0.0,
       "capacity_growth_event_count":0.0,"child_identity_mismatch_count":0.0,"invalid_evaluation_rows":0.0}
    p71=load_mod("p071_y73",P071);states=p71.candidate_states(root,m);m["candidate_count"]=float(len(states))
    if len(states)!=2:m["invalid_evaluation_rows"]+=1.0
    learner,base,mis=load_learner_and_base();m["base_training_identity_mismatch_count"]+=float(mis)
    source_base=int(learner.baseline_predict(base,SOURCE_STATE["key"][-1]));m["source_baseline_prediction"]=float(source_base)
    if source_base!=SOURCE_STATE["best"]:m["source_role_override_verified"]=1.0
    else:m["invalid_evaluation_rows"]+=1.0
    raw=(Path(root)/"technical-prose.bin").read_bytes()
    if len(raw)!=1454:m["source_identity_mismatch_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
    prose_train=raw[:len(raw)*60//100]
    triggers=[]
    for rank,state in enumerate(states[:2],1):
        key=tuple(state["key"]);tb=int(learner.baseline_predict(base,key[-1]))
        occ,alt,altc=successor_info(prose_train,key,tb)
        eligible=occ>=1 and alt>=0 and altc>=1
        score=(altc/occ) if eligible else -1.0
        if eligible:m["eligible_candidate_count"]+=1.0
        triggers.append({"rank":rank,"key":key,"target_baseline":tb,"occurrence_count":occ,"alt_best":alt,"alt_count":altc,"score":score,"eligible":eligible})
    eligible=[x for x in triggers if x["eligible"]]
    if not eligible:
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"decision":"REJECT","metrics":m,"triggers":triggers}
    eligible.sort(key=lambda x:(-x["score"],x["key"]))
    sel=eligible[0];alt=eligible[1] if len(eligible)>1 else None
    m["selected_trigger_rank"]=float(sel["rank"]);m["selected_compatibility_score"]=sel["score"];m["selected_alt_best"]=float(sel["alt_best"])
    sc=run_adapter(root,sel);sm=sc["metrics"]
    m["original_positive_prose_collateral_schedule_count"]=float(sm["original_positive_prose_collateral_schedule_count"])
    m["selected_positive_prose_collateral_schedule_count"]=float(sm["active_positive_prose_collateral_schedule_count"])
    m["selected_partner_collateral_failure_count"]=float(sm["active_partner_collateral_failure_count"])
    m["selected_behavior_change_count"]=float(behavior_changed(sc))
    m["capacity_growth_event_count"]+=float(sm["capacity_growth_event_count"])
    m["child_identity_mismatch_count"]+=float(sm["source_identity_mismatch_count"]+sm["transfer_manifest_identity_mismatch_count"]+sm["transported_state_identity_mismatch_count"])
    m["invalid_evaluation_rows"]+=float(sm["invalid_evaluation_rows"])
    ac=None
    if alt is not None:
        m["alternate_trigger_rank"]=float(alt["rank"]);m["alternate_compatibility_score"]=alt["score"];m["alternate_alt_best"]=float(alt["alt_best"])
        ac=run_adapter(root,alt);am=ac["metrics"]
        m["alternate_positive_prose_collateral_schedule_count"]=float(am["active_positive_prose_collateral_schedule_count"])
        m["alternate_partner_collateral_failure_count"]=float(am["active_partner_collateral_failure_count"])
        m["alternate_behavior_change_count"]=float(behavior_changed(ac))
        m["capacity_growth_event_count"]+=float(am["capacity_growth_event_count"])
        m["child_identity_mismatch_count"]+=float(am["source_identity_mismatch_count"]+am["transfer_manifest_identity_mismatch_count"]+am["transported_state_identity_mismatch_count"])
        m["invalid_evaluation_rows"]+=float(am["invalid_evaluation_rows"])
    if m["child_identity_mismatch_count"]!=0 or m["capacity_growth_event_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"decision":"RESIDUAL_BRIDGE","metrics":m,
            "selected":sel,"alternate":alt,"selected_diagnostics":sc["diagnostics"],"alternate_diagnostics":[] if ac is None else ac["diagnostics"]}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"),sort_keys=True)
if __name__=="__main__":main()

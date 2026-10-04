"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-INCOMPATIBILITY-GATE-075."""
import argparse
import hashlib
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-INCOMPATIBILITY-GATE-075"
P068=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.py")
P020=Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
SOURCE_STATE={"key":(10,32,32,32),"best":32,"total":112,"best_count":112,"consistency":1.0,"utility":112.0,"cell_index":12,"map_best":32}
TARGET_SOURCES={
    "A":{"file":"code.bin","sha256":"283073d9f6c0dd868c39a913364bce6744ff1e29c038f6920197c0d33e0c2ac1","bytes":41453},
    "B":{"file":"structured.bin","sha256":"a46fcfb7d862b03b750b61a5f667d4ac25a064df9ccb746e395db7e864068933","bytes":14365},
    "C":{"file":"technical-prose.bin","sha256":"5d0c2efd139bd6094098bc893ed746020f03e0860a25f278348f43f47c236222","bytes":1454},
}
ACTIVATION_NEEDLE='''        if RETAINED_KEY in original_guard:
            active_guard=original_guard;active_used=False
        else:
            active_guard=tuple(list(original_guard[:6])+[RETAINED_KEY]);active_used=True
            m["active_transport_use_schedule_count"]+=1.0
'''

def load_mod(name,path):
    import importlib.util
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise RuntimeError("IMPORT_SPEC_FAILED:"+name)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def byte_class(x):
    x=int(x)
    if x in (9,10,13,32):return 0
    if 65<=x<=90 or 97<=x<=122:return 1
    if 48<=x<=57:return 2
    return 3

def load_target(root,m):
    root=Path(root);out={};total=0
    for name in ("A","B","C"):
        spec=TARGET_SOURCES[name];p=root/spec["file"]
        try:data=p.read_bytes()
        except OSError:
            data=b"";m["target_source_identity_mismatch_count"]+=1.0
        if len(data)!=spec["bytes"] or hashlib.sha256(data).hexdigest()!=spec["sha256"]:
            m["target_source_identity_mismatch_count"]+=1.0
        total+=len(data);split=len(data)*60//100
        if split<=0 or split>=len(data):
            m["invalid_evaluation_rows"]+=1.0;out[name]=(b"",b"")
        else:out[name]=(data[:split],data[split:])
    m["target_source_count"]=3.0;m["target_total_source_bytes"]=float(total)
    return out

def scan_key(buf,key):
    occ=0;succ=[0]*256
    for i in range(0,max(0,len(buf)-3)):
        if tuple(buf[i:i+4])==key:
            occ+=1
            if i+4<len(buf):succ[buf[i+4]]+=1
    obs=sum(succ)
    if obs:
        best=max(range(256),key=lambda x:(succ[x],-x));best_count=succ[best]
    else:best=-1;best_count=0
    return occ,obs,best,best_count

def canonical_donor(root,m):
    p20=load_mod("p020_y75",P020);p17=p20.load_prior_experiment();p16=p17.load_prior_experiment()
    p15=p16.load_prior_experiment();p14=p15.load_prior_experiment();p13=p14.load_prior_experiment()
    ad=p13.load_prior_experiment();eg=ad.load_prior_experiment();wake=eg.load_wake();pressure=wake.load_pressure();learner=pressure.load_prior()
    d=load_target(root,m)
    bt=[]
    for p,h in learner.TRAIN_FILES:
        x,ok=learner.load_checked(p,h);m["base_training_identity_mismatch_count"]+=float(not ok);bt.append(x)
    base=learner.baseline_train(bt)
    bcue=d["B"][0];ccue=d["C"][0]
    bh=bcue[:len(bcue)//2];ch=ccue[:len(ccue)//2];total=len(bh)+len(ch)
    add=len(ccue)-len(ch);ch=ccue;bh=bcue[:len(bh)-add]
    if min(len(bh),len(ch))<=0 or len(bh)+len(ch)!=total:m["history_byte_budget_mismatch_count"]+=1.0
    cur={"B":(bh,d["B"][1]),"C":(ch,d["C"][1])}
    ind={}
    for n in ("B","C"):
        cue,_=cur[n]
        st,o,iv=learner.candidate_stats(bt+[cue]);m["invalid_evaluation_rows"]+=float(o+iv)
        cells,rv=learner.develop(st);m["invalid_evaluation_rows"]+=float(rv)
        fm=learner.specialized_map(cells);rows=wake.known_rows(pressure,learner,cells,st)
        if len(fm)!=16 or len(rows)!=16:m["invalid_evaluation_rows"]+=1.0
        ind[n]=rows
    st,o,iv=learner.candidate_stats(bt+[cur["B"][0],cur["C"][0]]);m["invalid_evaluation_rows"]+=float(o+iv)
    pooled,rv=learner.develop(st);m["invalid_evaluation_rows"]+=float(rv)
    cells,nsel,_,_=p16.build_matched_minimax_cells(learner,eg,base,st,pooled,ind,["B","C"],cur,p15)
    if nsel!=16:m["invalid_evaluation_rows"]+=1.0
    fm=learner.specialized_map(cells);rows=wake.known_rows(pressure,learner,cells,st)
    if len(fm)!=16 or len(rows)!=16:m["invalid_evaluation_rows"]+=1.0
    m["donor_row_count"]=float(len(rows));m["induction_source_bytes"]=float(len(bcue)+len(ccue))
    return rows,fm,d["C"][0]

def build_pool(root,m):
    rows,fm,prose_train=canonical_donor(root,m);pool=[]
    for r in rows:
        key=tuple(r["key"]);occ,obs,argmax,argmax_count=scan_key(prose_train,key)
        if occ<1 or obs<1:continue
        pool.append({
          "key":key,"best":int(r["best"]),"total":int(r["total"]),"best_count":int(r["best_count"]),
          "consistency":float(r["consistency"]),"utility":float(r["utility"]),
          "cell_index":int(r["cell_index"]),"map_best":int(fm[key]),
          "train_occurrence_count":int(occ),"train_argmax_count":int(argmax_count),"train_argmax":int(argmax),
        })
    m["eligible_candidate_count"]=float(len(pool));return pool

def source_rank(s):
    best_match=int(byte_class(s["best"])==byte_class(SOURCE_STATE["best"]))
    key_matches=sum(byte_class(a)==byte_class(b) for a,b in zip(s["key"],SOURCE_STATE["key"]))
    return (-best_match,-key_matches,-s["train_occurrence_count"],-s["train_argmax_count"],-s["utility"],s["key"])

def local_rank(s):
    return (-s["train_occurrence_count"],-s["train_argmax_count"],-s["utility"],s["key"])

def run_variant(root,state):
    source=P068.read_text(encoding="utf-8")
    if source.count(ACTIVATION_NEEDLE)!=1:raise RuntimeError("P068_ACTIVATION_BLOCK_NOT_EXACT")
    repl='''        base_guard=[k for k in original_guard if k!=RETAINED_KEY]
        if RETAINED_KEY not in original_guard:
            if len(base_guard)!=7:m["invalid_evaluation_rows"]+=1.0
            else:base_guard.pop(6)
        if len(base_guard)!=6:m["invalid_evaluation_rows"]+=1.0
        active_list=list(base_guard);active_list.insert(6,RETAINED_KEY)
        active_guard=tuple(active_list)
        active_used=(active_guard!=original_guard)
        if active_used:m["active_transport_use_schedule_count"]+=1.0
'''
    source=source.replace(ACTIVATION_NEEDLE,repl,1)
    ns={"__name__":"p068_y75_variant","__file__":str(P068)}
    exec(compile(source,str(P068),"exec"),ns)
    ns["TRANSFER_SOURCES"]={k:dict(v) for k,v in TARGET_SOURCES.items()}
    ns["RETAINED_KEY"]=tuple(state["key"])
    ns["RETAINED_STATE"]={k:state[k] for k in ("key","best","total","best_count","consistency","utility","cell_index","map_best")}
    return ns["run"](root)

def behavior_changed(child):
    m=child["metrics"]
    if m["active_positive_prose_collateral_schedule_count"]!=m["original_positive_prose_collateral_schedule_count"]:return True
    if m["active_mean_first_success_packet"]!=m["original_mean_first_success_packet"]:return True
    if m["active_partner_collateral_failure_count"]!=m["original_partner_collateral_failure_count"]:return True
    for d in child.get("diagnostics",[]):
        for p in d.get("packets",[]):
            if p["active"]!=p["original"]:return True
    return False

def summarize(child):
    m=child["metrics"]
    return {
      "original_prose":float(m["original_positive_prose_collateral_schedule_count"]),
      "active_prose":float(m["active_positive_prose_collateral_schedule_count"]),
      "original_partner_fail":float(m["original_partner_collateral_failure_count"]),
      "active_partner_fail":float(m["active_partner_collateral_failure_count"]),
      "original_first":float(m["original_mean_first_success_packet"]),
      "active_first":float(m["active_mean_first_success_packet"]),
      "invalid":float(m["invalid_evaluation_rows"]),
      "source_mismatch":float(m["source_identity_mismatch_count"]+m["transfer_manifest_identity_mismatch_count"]),
      "transport_mismatch":float(m["transported_state_identity_mismatch_count"]),
      "capacity_growth":float(m["capacity_growth_event_count"]),
    }

def run(root):
    m={
      "target_source_identity_mismatch_count":0.0,"target_source_count":0.0,"target_total_source_bytes":0.0,
      "base_training_identity_mismatch_count":0.0,"history_byte_budget_mismatch_count":0.0,
      "donor_row_count":0.0,"induction_source_bytes":0.0,"eligible_candidate_count":0.0,
      "source_state_identity_mismatch_count":0.0,"source_state_mutation_count":0.0,
      "heldout_gate_input_count":0.0,"post_result_gate_change_count":0.0,
      "selectors_same_row_count":0.0,"source_selected_best_class_match":0.0,
      "source_selected_key_class_match_count":0.0,"local_selected_key_class_match_count":0.0,
      "source_specificity_gain":0.0,"decision_allow_source_prior":0.0,"decision_reject":0.0,
      "original_positive_prose_collateral_schedule_count":0.0,
      "source_positive_prose_collateral_schedule_count":0.0,"local_positive_prose_collateral_schedule_count":0.0,
      "source_partner_collateral_failure_count":0.0,"local_partner_collateral_failure_count":0.0,
      "source_mean_first_success_packet":0.0,"local_mean_first_success_packet":0.0,
      "source_behavior_change_count":0.0,"local_behavior_change_count":0.0,
      "operational_positive_prose_collateral_schedule_count":0.0,"operational_partner_collateral_failure_count":0.0,
      "all_child_source_identity_mismatch_count":0.0,"all_child_transport_identity_mismatch_count":0.0,
      "capacity_growth_event_count":0.0,"persistent_state_write_count":0.0,"invalid_evaluation_rows":0.0,
    }
    if SOURCE_STATE!={"key":(10,32,32,32),"best":32,"total":112,"best_count":112,"consistency":1.0,"utility":112.0,"cell_index":12,"map_best":32}:
        m["source_state_identity_mismatch_count"]+=1.0
    pool=build_pool(root,m)
    if not pool:
        m["invalid_evaluation_rows"]+=1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"decision":"INVALID","metrics":m}
    source_selected=sorted(pool,key=source_rank)[0];local_selected=sorted(pool,key=local_rank)[0]
    same=tuple(source_selected["key"])==tuple(local_selected["key"])
    m["selectors_same_row_count"]=float(same)
    sbm=int(byte_class(source_selected["best"])==byte_class(SOURCE_STATE["best"]))
    skm=sum(byte_class(a)==byte_class(b) for a,b in zip(source_selected["key"],SOURCE_STATE["key"]))
    lkm=sum(byte_class(a)==byte_class(b) for a,b in zip(local_selected["key"],SOURCE_STATE["key"]))
    gain=skm-lkm
    m["source_selected_best_class_match"]=float(sbm)
    m["source_selected_key_class_match_count"]=float(skm)
    m["local_selected_key_class_match_count"]=float(lkm)
    m["source_specificity_gain"]=float(gain)
    decision="ALLOW_SOURCE_PRIOR" if (not same and sbm==1 and gain>=1) else "REJECT"
    if decision=="ALLOW_SOURCE_PRIOR":m["decision_allow_source_prior"]=1.0
    else:m["decision_reject"]=1.0
    # Decision is frozen above. Shadow evaluation begins only below.
    source_child=run_variant(root,source_selected);local_child=run_variant(root,local_selected)
    ss=summarize(source_child);ls=summarize(local_child)
    if (ss["original_prose"],ss["original_partner_fail"],ss["original_first"])!=(ls["original_prose"],ls["original_partner_fail"],ls["original_first"]):
        m["invalid_evaluation_rows"]+=1.0
    m["original_positive_prose_collateral_schedule_count"]=ss["original_prose"]
    m["source_positive_prose_collateral_schedule_count"]=ss["active_prose"]
    m["local_positive_prose_collateral_schedule_count"]=ls["active_prose"]
    m["source_partner_collateral_failure_count"]=ss["active_partner_fail"]
    m["local_partner_collateral_failure_count"]=ls["active_partner_fail"]
    m["source_mean_first_success_packet"]=ss["active_first"];m["local_mean_first_success_packet"]=ls["active_first"]
    if behavior_changed(source_child):m["source_behavior_change_count"]=1.0
    if behavior_changed(local_child):m["local_behavior_change_count"]=1.0
    if decision=="ALLOW_SOURCE_PRIOR":
        m["operational_positive_prose_collateral_schedule_count"]=ss["active_prose"]
        m["operational_partner_collateral_failure_count"]=ss["active_partner_fail"]
    else:
        m["operational_positive_prose_collateral_schedule_count"]=ss["original_prose"]
        m["operational_partner_collateral_failure_count"]=ss["original_partner_fail"]
    m["all_child_source_identity_mismatch_count"]=ss["source_mismatch"]+ls["source_mismatch"]
    m["all_child_transport_identity_mismatch_count"]=ss["transport_mismatch"]+ls["transport_mismatch"]
    m["capacity_growth_event_count"]=ss["capacity_growth"]+ls["capacity_growth"]
    m["invalid_evaluation_rows"]+=ss["invalid"]+ls["invalid"]
    if m["target_source_identity_mismatch_count"]!=0 or m["base_training_identity_mismatch_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    if m["source_state_identity_mismatch_count"]!=0 or m["source_state_mutation_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    if m["all_child_source_identity_mismatch_count"]!=0 or m["all_child_transport_identity_mismatch_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    if m["capacity_growth_event_count"]!=0 or m["persistent_state_write_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {
      "schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"decision":decision,
      "metrics":m,"source_selected":source_selected,"local_selected":local_selected,
      "source_diagnostics":source_child["diagnostics"],"local_diagnostics":local_child["diagnostics"],
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":main()

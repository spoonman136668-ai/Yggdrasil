"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-070."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-070"
P068=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.py")
P020=Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
SOURCES={
    "B":{"file":"structured.bin","sha256":"2a97ba02bc5e479b1738f6f0c3e09318bb5a255350c84de014ddbcebea46af56","bytes":14365},
    "C":{"file":"technical-prose.bin","sha256":"23c002a1984ed065abfdbafa82100ed54d6bf6276a947676e710a30c75d96017","bytes":1454},
}

def load_mod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise RuntimeError("IMPORT_SPEC_FAILED:"+name)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def load_sources(root,m):
    root=Path(root);out={};total=0
    for name in ("B","C"):
        spec=SOURCES[name];p=root/spec["file"]
        try:data=p.read_bytes()
        except OSError:data=b"";m["source_identity_mismatch_count"]+=1.0
        if len(data)!=spec["bytes"] or hashlib.sha256(data).hexdigest()!=spec["sha256"]:
            m["source_identity_mismatch_count"]+=1.0
        total+=len(data);split=len(data)*60//100
        if split<=0 or split>=len(data):m["invalid_evaluation_rows"]+=1.0;out[name]=(b"",b"")
        else:out[name]=(data[:split],data[split:])
    m["induction_source_count"]=2.0;m["induction_source_bytes"]=float(total)
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
    else:
        best=-1;best_count=0
    return occ,obs,best,best_count

def rebalanced(bcue,ccue,m):
    bh=bcue[:len(bcue)//2];ch=ccue[:len(ccue)//2];total=len(bh)+len(ch)
    add=len(ccue)-len(ch);ch=ccue;bh=bcue[:len(bh)-add]
    if min(len(bh),len(ch))<=0 or len(bh)+len(ch)!=total:m["history_byte_budget_mismatch_count"]+=1.0
    return bh,ch

def canonical_donor(root,m):
    p20=load_mod("p020_y70",P020);p17=p20.load_prior_experiment();p16=p17.load_prior_experiment()
    p15=p16.load_prior_experiment();p14=p15.load_prior_experiment();p13=p14.load_prior_experiment()
    ad=p13.load_prior_experiment();eg=ad.load_prior_experiment();wake=eg.load_wake();pressure=wake.load_pressure();learner=pressure.load_prior()
    d=load_sources(root,m)
    bt=[]
    for p,h in learner.TRAIN_FILES:
        x,ok=learner.load_checked(p,h);m["base_training_identity_mismatch_count"]+=float(not ok);bt.append(x)
    base=learner.baseline_train(bt)
    bh,ch=rebalanced(d["B"][0],d["C"][0],m)
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
    return rows,fm,d["C"][0]

def select_local(rows,fm,prose_train,m):
    eligible=[]
    for r in rows:
        key=tuple(r["key"]);occ,obs,best,best_count=scan_key(prose_train,key)
        map_best=fm.get(key)
        ok=(occ>=1 and obs>=1 and best==int(r["best"]) and map_best is not None and int(map_best)==int(r["best"]))
        if ok:
            eligible.append((occ,best_count,float(r["utility"]),key,r,int(map_best)))
    m["local_candidate_count"]=float(len(eligible))
    if not eligible:return None
    eligible.sort(key=lambda x:(-x[0],-x[1],-x[2],x[3]))
    occ,best_count,utility,key,row,map_best=eligible[0]
    m["selected_local_key_train_occurrence_count"]=float(occ)
    m["selected_local_key_train_argmax_count"]=float(best_count)
    m["selected_local_row_map_best_mismatch_count"]=float(int(row["best"])!=map_best)
    state={
      "key":key,"best":int(row["best"]),"total":int(row["total"]),"best_count":int(row["best_count"]),
      "consistency":float(row["consistency"]),"utility":float(row["utility"]),"cell_index":int(row["cell_index"]),"map_best":map_best,
    }
    return state

def run(root):
    m={
      "source_identity_mismatch_count":0.0,"induction_source_count":0.0,"induction_source_bytes":0.0,
      "base_training_identity_mismatch_count":0.0,"history_byte_budget_mismatch_count":0.0,
      "local_candidate_count":0.0,"selected_local_key_train_occurrence_count":0.0,
      "selected_local_key_train_argmax_count":0.0,"selected_local_row_map_best_mismatch_count":0.0,
      "local_row_synthesis_count":0.0,"heldout_local_row_selection_count":0.0,
      "active_local_use_schedule_count":0.0,"original_positive_prose_collateral_schedule_count":0.0,
      "passive_positive_prose_collateral_schedule_count":0.0,"active_positive_prose_collateral_schedule_count":0.0,
      "active_partner_collateral_failure_count":0.0,"capacity_growth_event_count":0.0,
      "invalid_evaluation_rows":0.0,
    }
    rows,fm,prose_train=canonical_donor(root,m)
    state=select_local(rows,fm,prose_train,m)
    if state is None:
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"selected_local_state":None,"diagnostics":[]}
    p68=load_mod("p068_y70",P068)
    p68.RETAINED_KEY=tuple(state["key"])
    p68.RETAINED_STATE=dict(state)
    child=p68.run(root);cm=child["metrics"]
    m["active_local_use_schedule_count"]=float(cm["active_transport_use_schedule_count"])
    m["original_positive_prose_collateral_schedule_count"]=float(cm["original_positive_prose_collateral_schedule_count"])
    m["passive_positive_prose_collateral_schedule_count"]=float(cm["passive_positive_prose_collateral_schedule_count"])
    m["active_positive_prose_collateral_schedule_count"]=float(cm["active_positive_prose_collateral_schedule_count"])
    m["active_partner_collateral_failure_count"]=float(cm["active_partner_collateral_failure_count"])
    m["capacity_growth_event_count"]=float(cm["capacity_growth_event_count"])
    m["invalid_evaluation_rows"]+=float(cm["invalid_evaluation_rows"])
    if cm["transported_state_identity_mismatch_count"]!=0:m["invalid_evaluation_rows"]+=float(cm["transported_state_identity_mismatch_count"])
    if cm["candidate_selection_heldout_use_count"]!=0:m["invalid_evaluation_rows"]+=float(cm["candidate_selection_heldout_use_count"])
    if cm["preserved_state_structure_count_min"]!=16 or cm["active_structure_count_min"]!=7 or cm["retained_structure_count_min"]!=9:
        m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"selected_local_state":state,"diagnostics":child["diagnostics"]}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":main()

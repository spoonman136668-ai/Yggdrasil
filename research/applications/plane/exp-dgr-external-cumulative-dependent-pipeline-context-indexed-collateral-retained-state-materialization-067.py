"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAINED-STATE-MATERIALIZATION-067."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAINED-STATE-MATERIALIZATION-067"
PRIOR_PATH=Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
RETAINED_KEY=(10,32,32,32)
SOURCES={
    "B":{"file":"structured.bin","sha256":"95ddbd0eaef29aad5ecfc74f9da21b795481f58b2c59380324a445fcd4d08932","bytes":14365},
    "C":{"file":"technical-prose.bin","sha256":"48c3d95b8b03864a4af41d892710675956cde85afd0d5d6c331594de9f17881b","bytes":1454},
}

def load_prior():
    s=importlib.util.spec_from_file_location("p020",PRIOR_PATH)
    if s is None or s.loader is None:raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def load_sources(root,m):
    root=Path(root);out={};total=0
    for name in ("B","C"):
        spec=SOURCES[name];p=root/spec["file"]
        try:data=p.read_bytes()
        except OSError:
            data=b"";m["source_identity_mismatch_count"]+=1.0
        if len(data)!=spec["bytes"] or hashlib.sha256(data).hexdigest()!=spec["sha256"]:
            m["source_identity_mismatch_count"]+=1.0
        total+=len(data);split=len(data)*60//100
        if split<=0 or split>=len(data):
            m["invalid_rows"]+=1.0;out[name]=(b"",b"")
        else:out[name]=(data[:split],data[split:])
    m["loaded_source_count"]=2.0;m["loaded_source_bytes"]=float(total)
    return out

def rebalanced(bcue,ccue,m):
    bh=bcue[:len(bcue)//2];ch=ccue[:len(ccue)//2];total=len(bh)+len(ch)
    add=len(ccue)-len(ch);ch=ccue;bh=bcue[:len(bh)-add]
    if min(len(bh),len(ch))<=0 or len(bh)+len(ch)!=total:m["history_byte_budget_mismatch_count"]+=1.0
    return bh,ch

def run(root):
    p20=load_prior();p17=p20.load_prior_experiment();p16=p17.load_prior_experiment()
    p15=p16.load_prior_experiment();p14=p15.load_prior_experiment();p13=p14.load_prior_experiment()
    ad=p13.load_prior_experiment();eg=ad.load_prior_experiment();wake=eg.load_wake();pressure=wake.load_pressure();learner=pressure.load_prior()
    m={
      "source_identity_mismatch_count":0.0,"loaded_source_count":0.0,"loaded_source_bytes":0.0,
      "base_training_identity_mismatch_count":0.0,"history_byte_budget_mismatch_count":0.0,
      "donor_row_count":0.0,"retained_key_row_count":0.0,"retained_key_map_count":0.0,
      "serialized_field_count":0.0,"evaluation_use_count":0.0,"policy_selection_count":0.0,
      "capacity_growth_event_count":0.0,"persistent_state_write_count":0.0,
      "production_authority_count":0.0,"invalid_rows":0.0,
    }
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
        st,o,iv=learner.candidate_stats(bt+[cue]);m["invalid_rows"]+=float(o+iv)
        cells,rv=learner.develop(st);m["invalid_rows"]+=float(rv)
        fm=learner.specialized_map(cells);rows=wake.known_rows(pressure,learner,cells,st)
        if len(fm)!=16 or len(rows)!=16:m["invalid_rows"]+=1.0
        ind[n]=rows
    st,o,iv=learner.candidate_stats(bt+[cur["B"][0],cur["C"][0]]);m["invalid_rows"]+=float(o+iv)
    pooled,rv=learner.develop(st);m["invalid_rows"]+=float(rv)
    cells,nsel,_,_=p16.build_matched_minimax_cells(learner,eg,base,st,pooled,ind,["B","C"],cur,p15)
    if nsel!=16:m["invalid_rows"]+=1.0
    fm=learner.specialized_map(cells);rows=wake.known_rows(pressure,learner,cells,st)
    m["donor_row_count"]=float(len(rows))
    matches=[r for r in rows if tuple(r["key"])==RETAINED_KEY]
    m["retained_key_row_count"]=float(len(matches))
    m["retained_key_map_count"]=1.0 if RETAINED_KEY in fm else 0.0
    state=None
    if len(rows)!=16 or len(fm)!=16:m["invalid_rows"]+=1.0
    if len(matches)!=1 or RETAINED_KEY not in fm:
        m["invalid_rows"]+=1.0
    else:
        r=matches[0]
        state={
          "schema":"yggdrasil.retained-row-state.v1",
          "key":list(RETAINED_KEY),
          "best":int(r["best"]),
          "total":int(r["total"]),
          "best_count":int(r["best_count"]),
          "consistency":float(r["consistency"]),
          "utility":float(r["utility"]),
          "cell_index":int(r["cell_index"]),
          "map_best":int(fm[RETAINED_KEY]),
        }
        m["serialized_field_count"]=8.0
        if state["best"]!=state["map_best"]:m["invalid_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"retained_state":state}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":main()

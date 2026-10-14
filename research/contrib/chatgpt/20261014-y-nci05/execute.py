"""Y-NCI05: native StatePool bounded multiedge storage integration and falsification.

Fix only experimental writer representation, not Y-NCI02 learned admission/join.
Existing StatePool remains 576 bytes, 7 active and <=9 retained. 96
prospectively frozen novel seed/motif cases test graph composition, recovery,
new knowledge and same-resource original one-valued StatePool baseline.
This writer is deterministic, not learned relational memory or search.
"""
from __future__ import annotations
import copy,importlib.util,json
from pathlib import Path
import torch
P=Path(__file__).resolve().parent.parent/"20261014-y-nci02-learned-join"/"execute.py"
S=importlib.util.spec_from_file_location("y_nci02_source",P)
assert S and S.loader
nci02=importlib.util.module_from_spec(S);S.loader.exec_module(nci02)
nci01=nci02.nci01
SEEDS=tuple(range(24640,24664))
MOTIFS=("root_fork","internal_fork","dual_fork","nonfork_control")
CAP=7
def fixture(seed,family):
    step=(1,3,5,7)[family]
    shift=(seed*7+3*family)%16
    nodes=[64+(shift+step*i)%16 for i in range(5)]
    ex=[80+3*i+(seed+i+family)%3 for i in range(6)]
    links=[(nodes[0],nodes[1]),(nodes[1],nodes[2]),(nodes[2],nodes[3])]
    if family==0:
        links += [(nodes[0],ex[0]),(ex[2],ex[3]),(ex[4],ex[5])]
    elif family==1:
        links += [(nodes[1],ex[0]),(ex[2],ex[3]),(ex[4],ex[5])]
    elif family==2:
        links += [(nodes[0],ex[0]),(nodes[1],ex[1]),(ex[4],ex[5])]
    else:
        links += [(ex[0],ex[1]),(ex[2],ex[3]),(ex[4],ex[5])]
    assert len(links)==6 and len(set(links))==6 and len(set(nodes))==5
    return nodes,links
def multi_write(pool,source,target):
    state=pool.state_dict()["storage"]
    for idx in range(CAP):
        y,x=divmod(idx,nci01.GRID)
        if float(state[0,2,y,x])>0 and (int(state[0,0,y,x])-1,int(state[0,1,y,x])-1)==(source,target):
            return
    for idx in range(CAP):
        y,x=divmod(idx,nci01.GRID)
        if float(state[0,2,y,x])==0:
            state[0,0,y,x]=float(source+1)
            state[0,1,y,x]=float(target+1)
            state[0,2,y,x]=1.0
            pool.update(torch.tensor([0]),state)
            return
    raise RuntimeError("NCI05_SEVEN_ACTIVE_EDGE_BUDGET_EXCEEDED")
def exact_reach(edges,source,target,hops):
    current={source}
    for _ in range(hops):
        current={b for a,b in edges if a in current}
    return target in current
def eval_case(admit,weights,bias,cut,seed,family,work):
    nodes,links=fixture(seed,family)
    multi=nci01.new_native_pool()
    control=nci01.new_native_pool()
    tp=fp=fn=calls=0
    def observe(a,b,store):
        nonlocal tp,fp,fn,calls
        clause=f"e{a} {'stores' if store else 'observes'} e{b}."
        with torch.no_grad():
            prob=float(torch.sigmoid(admit(nci01.token_features(clause))).item())
        accept=prob>=.5
        calls+=1
        if accept and store:tp+=1
        if accept and not store:fp+=1
        if not accept and store:fn+=1
        if accept:
            multi_write(multi,a,b)
            nci01.memory_write(control,a,b)
    for a,b in links:observe(a,b,True)
    observe(98,99,False)
    old_multi=nci02.memory_edges(multi)
    old_control=nci02.memory_edges(control)
    def query(edges,dest,steps,arm):
        calls=work[arm]
        return nci02.reached(weights,bias,cut,edges,nodes[0],dest,steps,calls)
    row={"seed":seed,"motif":MOTIFS[family]}
    row["multiedge_two"]=query(old_multi,nodes[2],2,"multi")
    row["multiedge_three"]=query(old_multi,nodes[3],3,"multi")
    row["multiedge_two_negative"]=not query(old_multi,nodes[3],2,"multi")
    row["multiedge_three_negative"]=not query(old_multi,nodes[4],3,"multi")
    row["baseline_two"]=query(old_control,nodes[2],2,"baseline")
    row["baseline_three"]=query(old_control,nodes[3],3,"baseline")
    row["direct_only"]=(nodes[0],nodes[2]) in old_control
    row["oracle_two"]=exact_reach(links,nodes[0],nodes[2],2)
    row["oracle_three"]=exact_reach(links,nodes[0],nodes[3],3)
    checkpoint_multi=copy.deepcopy(multi.state_dict())
    checkpoint_old=copy.deepcopy(control.state_dict())
    restored_multi=nci01.new_native_pool();restored_multi.load_state_dict(checkpoint_multi)
    restored_old=nci01.new_native_pool();restored_old.load_state_dict(checkpoint_old)
    work["restores"]+=1
    row["multiedge_interrupted"]=query(nci02.memory_edges(restored_multi),nodes[2],2,"multi")
    # New learned observation after interruption; same frozen trained admission.
    clause=f"e{nodes[3]} stores e{nodes[4]}."
    with torch.no_grad():
        predicted=float(torch.sigmoid(admit(nci01.token_features(clause))).item())>=.5
    calls+=1
    if predicted:
        tp+=1
        multi_write(restored_multi,nodes[3],nodes[4])
        nci01.memory_write(restored_old,nodes[3],nodes[4])
    else:fn+=1
    new_multi=nci02.memory_edges(restored_multi)
    new_old=nci02.memory_edges(restored_old)
    row["multiedge_retained"]=query(new_multi,nodes[2],2,"multi")
    row["multiedge_new_four"]=query(new_multi,nodes[4],4,"multi")
    row["baseline_retained"]=query(new_old,nodes[2],2,"baseline")
    row["active_edges"]=len(new_multi)
    row["baseline_entries"]=len(new_old)
    row["state_bytes_multi"]=int(restored_multi.state_dict()["storage"].numel()*4)
    row["state_bytes_baseline"]=int(restored_old.state_dict()["storage"].numel()*4)
    row["admission"]={"tp":tp,"fp":fp,"fn":fn,"calls":calls}
    assert row["active_edges"]<=CAP and row["baseline_entries"]<=CAP
    assert row["state_bytes_multi"]==row["state_bytes_baseline"]==576
    return row
def run(phase="development"):
    if phase not in ("development","sealed"):raise ValueError(phase)
    weights,bias,cut,dev=nci02.join_training()
    admit,dev_admit,ntrain=nci01.learned_admission()
    result={"schema":"yggdrasil.nci05.multiedge-native-statepool.v1",
      "phase":phase,"scientific_parent":"e403542948fcaae1353c1292079e336f5347c72f",
      "join_dev_accuracy":dev,"admission_dev_accuracy":dev_admit,
      "join_params":6,"admission_params":4,
      "sealed_seed_range":list((SEEDS[0],SEEDS[-1]+1)),
      "motifs":MOTIFS,"native_state_bytes":576,"active_edge_cap":7,"retained_limit":9,
      "multiedge_storage_learned":False,"learned_graph_search":False,
      "nci01_full_acceptance":False,"external_llm_calls":0,
      "accepted_ref_mutation":False,"verdict":"DEVELOPMENT_ONLY"}
    if phase=="development":return result
    work={"multi":{"join_candidate_evaluations":0},
          "baseline":{"join_candidate_evaluations":0},"restores":0}
    trials=[eval_case(admit,weights,bias,cut,seed,f,work)
            for seed in SEEDS for f in range(len(MOTIFS))]
    assert len(trials)==96 and work["restores"]==96
    keys=("multiedge_two","multiedge_three","multiedge_two_negative",
          "multiedge_three_negative","multiedge_interrupted","multiedge_retained",
          "multiedge_new_four","baseline_two","baseline_three","baseline_retained",
          "oracle_two","oracle_three","direct_only")
    per={motif:{k:sum(bool(t[k]) for t in trials if t["motif"]==motif)/24
                 for k in keys} for motif in MOTIFS}
    strong=all(per[m][k]>=.90 for m in MOTIFS for k in keys[:7])
    strong=strong and all(per[m]["oracle_two"]>=.99 and per[m]["oracle_three"]>=.99
                          for m in MOTIFS)
    baseline_failure=all(per[m]["baseline_two"]<.50 for m in MOTIFS[:3])
    verdict="BOUNDED_MULTIEDGE_STORAGE_DID_NOT_RESTORE_COMPOSITION"
    if strong and baseline_failure:
        verdict="BOUNDED_MULTIEDGE_STORAGE_RESTORES_CODED_COMPOSITION"
    elif strong:
        verdict="MULTIEDGE_COMPONENT_TRANSFER_WITHOUT_BASELINE_CONTRAST"
    result.update({"records":trials,"accuracy_by_motif":per,
       "multiedge_join_candidate_evaluations":work["multi"]["join_candidate_evaluations"],
       "baseline_join_candidate_evaluations":work["baseline"]["join_candidate_evaluations"],
       "checkpoint_restores":work["restores"],
       "peak_multiedge_entries":max(x["active_edges"] for x in trials),
       "admission":{k:sum(x["admission"][k] for x in trials)
                    for k in ("tp","fp","fn","calls")},
       "verdict":verdict})
    return result
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--phase",choices=("development","sealed"),default="development")
    print(json.dumps(run(ap.parse_args().phase),sort_keys=True,indent=2))

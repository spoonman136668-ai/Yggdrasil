"""Y-NCI04: frozen multivalued-relation memory falsification.

Tests existing native StatePool against two same-subject true edge motifs,
with no changes to the learned admission or join. A finite same-capacity
multigraph oracle distinguishes join failure from single-value overwriting.
"""
from __future__ import annotations
import copy,importlib.util,json
from pathlib import Path
import torch

P=Path(__file__).resolve().parent.parent/"20261014-y-nci02-learned-join"/"execute.py"
S=importlib.util.spec_from_file_location("y_nci02_frozen",P)
assert S and S.loader
nci02=importlib.util.module_from_spec(S);S.loader.exec_module(nci02)
nci01=nci02.nci01
SEALED=tuple(range(23936,23960))
MOTIFS=("root_fork","internal_fork","no_fork_control")
def reference(edges,start,target,hops):
    state={start}
    for _ in range(hops):
        state={b for a,b in edges if a in state}
    return target in state

def eval_case(admit,weights,bias,cut,seed,family,work):
    shift=(seed*5+family*3)%16
    nodes=[64+(shift+3*i)%16 for i in range(5)]
    extra=80+(seed+family)%5
    noise_a=86+(seed+family)%5
    noise_b=92+(seed+family)%5
    alt_source=nodes[0] if family==0 else (nodes[1] if family==1 else 97)
    links=[(nodes[0],nodes[1]),(nodes[1],nodes[2]),(nodes[2],nodes[3]),
           (alt_source,extra),(noise_a,noise_b)]
    pool=nci01.new_native_pool()
    admission={"tp":0,"fp":0,"fn":0,"calls":0}
    def observe(pool,a,b,verb):
        clause=f"e{a} {verb} e{b}."
        with torch.no_grad():
            pred=bool(torch.sigmoid(admit(nci01.token_features(clause))).item()>=.5)
        truth=(verb=="stores")
        admission["calls"]+=1
        if pred and truth:admission["tp"]+=1
        if pred and not truth:admission["fp"]+=1
        if not pred and truth:admission["fn"]+=1
        if pred:nci01.memory_write(pool,a,b)
    for edge in links:observe(pool,*edge,"stores")
    observe(pool,98,99,"observes")
    edges=nci02.memory_edges(pool)
    def reach(e,goal,depth):
        return nci02.reached(weights,bias,cut,e,nodes[0],goal,depth,work)
    row={"seed":seed,"motif":MOTIFS[family]}
    row["original_two_hop"]=reach(edges,nodes[2],2)
    row["original_three_hop"]=reach(edges,nodes[3],3)
    row["alternate_direct"]=(alt_source,extra) in edges
    row["oracle_original_two_hop"]=reference(links,nodes[0],nodes[2],2)
    row["oracle_original_three_hop"]=reference(links,nodes[0],nodes[3],3)
    row["direct_only_baseline"]=(nodes[0],nodes[2]) in edges
    checkpoint=copy.deepcopy(pool.state_dict())
    restored=nci01.new_native_pool()
    restored.load_state_dict(checkpoint)
    work["checkpoint_restores"]+=1
    row["interrupted_original"]=reach(nci02.memory_edges(restored),nodes[2],2)
    observe(restored,nodes[3],nodes[4],"stores")
    later=nci02.memory_edges(restored)
    row["old_after_new"]=reach(later,nodes[2],2)
    row["new_four_hop"]=reach(later,nodes[4],4)
    row["active_entries"]=len(later)
    assert row["active_entries"]<=7 and restored.sample_shape==(16,3,3)
    row["admission"]=admission
    row["state_bytes"]=int(restored.state_dict()["storage"].numel()*4)
    return row

def run(phase="development"):
    if phase not in ("development","sealed"):raise ValueError(phase)
    weights,bias,cut,dev=nci02.join_training()
    admission,dev_admission,ntrain=nci01.learned_admission()
    result={"schema":"yggdrasil.nci04.multivalued-native-memory-falsification.v1",
        "phase":phase,"scientific_parent":"7b79e5ee6ae42be534c5f8b0da9349abe5627526",
        "development_join_accuracy":dev,"development_admission_accuracy":dev_admission,
        "native_join_parameters":6,"native_admission_parameters":4,
        "state_bytes":576,"active_cap":7,"retained_cap":9,
        "sealed_heldout_seeds":list(SEALED),"motifs":MOTIFS,
        "learned_multivalued_storage":False,"learned_graph_search":False,
        "nci01_full_acceptance":False,
        "external_llm_calls":0,"accepted_ref_mutation":False,"verdict":"DEVELOPMENT_ONLY"}
    if phase=="development":return result
    work={"join_candidate_evaluations":0,"checkpoint_restores":0}
    rows=[eval_case(admission,weights,bias,cut,seed,family,work)
          for seed in SEALED for family in range(3)]
    assert len(rows)==72
    keys=("original_two_hop","original_three_hop","alternate_direct",
          "interrupted_original","old_after_new","new_four_hop",
          "oracle_original_two_hop","oracle_original_three_hop","direct_only_baseline")
    summaries={motif:{key:sum(bool(r[key]) for r in rows if r["motif"]==motif)/24
                      for key in keys} for motif in MOTIFS}
    control=summaries["no_fork_control"]["original_two_hop"]
    root=summaries["root_fork"]["original_two_hop"]
    internal=summaries["internal_fork"]["original_two_hop"]
    verdict="MULTIVALUED_MEMORY_LIMITATION_NOT_ISOLATED"
    if control>=.85 and root<.5 and internal<.5:
        verdict="FUNCTIONAL_MAP_FORK_RETENTION_FAILURE"
    elif control>=.85 and root>=.85 and internal>=.85:
        verdict="MULTIVALUED_TRANSFER_DEMONSTRATED"
    result.update({"verdict":verdict,"records":rows,"accuracy_by_motif":summaries,
        "peak_entries":max(r["active_entries"] for r in rows),
        "join_candidate_evaluations":work["join_candidate_evaluations"],
        "checkpoint_restores":work["checkpoint_restores"],
        "admission":{k:sum(r["admission"][k] for r in rows)
                     for k in ("tp","fp","fn","calls")}})
    return result

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=("development","sealed"),default="development")
    print(json.dumps(run(ap.parse_args().phase),sort_keys=True,indent=2))

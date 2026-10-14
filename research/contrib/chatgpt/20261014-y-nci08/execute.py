"""Y-NCI08: two disjoint chain memory-capacity counterfactual transfer.

Frozen NCI07 learned Torch graph-local policy, NCI06 earlier learned policy
and equal-7-edge FIFO/LRU retention. All receive identical public facts.
Queries for BOTH independent four-edge chains arrive only after storage.
The original full-12-edge oracle is explicitly outside the seven-edge cap.
"""
from __future__ import annotations
import importlib.util,json,torch
from pathlib import Path
P=Path(__file__).resolve().parent.parent/"20261014-y-nci07"/"execute.py"
S=importlib.util.spec_from_file_location("y07_frozen",P)
assert S and S.loader
y07=importlib.util.module_from_spec(S);S.loader.exec_module(y07)
prev=y07.previous
nci02=y07.nci02
nci01=y07.nci01
SEEDS=tuple(range(29248,29272))
FAMILIES=("interleaved_chains","first_chain_early","second_chain_early","noise_interleaved")
CAP=7

def fixture(seed,family):
    chains=(
      [64+(seed*3+5*i)%16 for i in range(5)],
      [96+(seed*7+3*i)%16 for i in range(5)])
    edges=[(chains[c][i],chains[c][i+1]) for c in range(2) for i in range(4)]
    edges.extend((128+i*4+seed%3,150+i*4+seed%3) for i in range(4))
    orders=((0,4,1,5,2,6,3,7,8,9,10,11),
            (0,1,2,3,4,5,6,7,8,9,10,11),
            (4,5,6,7,0,1,2,3,8,9,10,11),
            (8,0,4,9,1,5,10,2,6,11,3,7))
    observed=[]
    for t,idx in enumerate(orders[family]):
        observed.append({"edge":edges[idx],"exposure":1+(seed+t)%4,"time":t})
    assert len(edges)==len(set(edges))==12
    return chains,observed,edges

def run(phase="development"):
    if phase not in ("development","sealed"):raise ValueError(phase)
    policy,dev_rows,dev_acc=y07.train()
    prior_policy,prior_rows,prior_acc=prev.learner()
    result={"schema":"yggdrasil.nci08.paired-competing-chain-capacity.v1",
      "phase":phase,"source_parent":"7ac948630fe899a9f0551d774352703400cfb272",
      "sealed_seed_range":[29248,29272],"four_order_families":list(FAMILIES),
      "states":96,"paired_questions":192,
      "frozen_graph_parameters":4,"frozen_previous_parameters":3,
      "graph_dev_examples":dev_rows,"previous_dev_examples":prior_rows,
      "graph_validation_accuracy":dev_acc,"previous_validation_accuracy":prior_acc,
      "edge_cap":CAP,"native_state_bytes":576,"full_graph_oracle_edges":12,
      "paired_theoretical_physical_ceiling":0.5,
      "new_model_training":False,"external_llm_calls":0,"accepted_ref_mutation":False,
      "nci01_full_acceptance":False,"learned_graph_search":False,
      "verdict":"DEVELOPMENT_ONLY"}
    if phase=="development":return result
    join,bias,cut,_=nci02.join_training()
    admission,_,_=nci01.learned_admission()
    records=[]
    ops={p:0 for p in ("graph","previous","fifo","lru")}
    tally={p:[0,0] for p in ("graph","previous","fifo","lru","oracle")}
    groups={family:{p:[0,0] for p in tally} for family in FAMILIES}
    admitted=missed=multiplications=rejections=0
    physically_impossible_predictions=0
    for seed in SEEDS:
      for family in range(4):
        chains,raw,oracle_edges=fixture(seed,family)
        stream=[]
        for fact in raw:
            a,b=fact["edge"]
            with torch.no_grad():
                accepted=bool(torch.sigmoid(admission(nci01.token_features(f"e{a} stores e{b}."))).item()>=.5)
            if accepted:stream.append(fact);admitted+=1
            else:missed+=1
        graph_pool,graph_edges,spent,rejected=y07.retain(stream,policy)
        multiplications+=spent;rejections+=rejected
        others={}
        for name,oldmode in (("previous","learned"),("fifo","fifo"),("lru","lru")):
            pool,edges,_,_=prev.keep(stream,oldmode,prior_policy)
            others[name]=edges
        if not all(len(ed)==CAP for ed in [graph_edges,*others.values()]):
            raise RuntimeError("NCI08_ADMISSION_CAPACITY_PRECONDITION_FAILED")
        arms={"graph":graph_edges,**others}
        row={"seed":seed,"family":FAMILIES[family],"raw_admitted":len(stream),
             "graph_edges":len(graph_edges),"previous_edges":len(others["previous"]),
             "fifo_edges":len(others["fifo"]),"lru_edges":len(others["lru"])}
        for name,edges in arms.items():
            calls={"join_candidate_evaluations":0}
            answers=[nci02.reached(join,bias,cut,edges,
                chains[i][0],chains[i][4],4,calls) for i in range(2)]
            row[name+"_a"],row[name+"_b"]=answers
            ops[name]+=calls["join_candidate_evaluations"]
            if all(answers):physically_impossible_predictions+=1
            for i in range(2):
                tally[name][i]+=int(answers[i])
                groups[FAMILIES[family]][name][i]+=int(answers[i])
        answers=[prev.exact_oracle(oracle_edges,chains[i][0],chains[i][4],4) for i in range(2)]
        row["oracle_a"],row["oracle_b"]=answers
        for i in range(2):
            tally["oracle"][i]+=int(answers[i])
            groups[FAMILIES[family]]["oracle"][i]+=int(answers[i])
        records.append(row)
    assert len(records)==96
    score={n:(a+b)/192 for n,(a,b) in tally.items()}
    by_family={f:{n:sum(v)/48 for n,v in stats.items()} for f,stats in groups.items()}
    if physically_impossible_predictions:
        verdict="LEARNED_JOIN_FALSE_POSITIVE_INVALIDATES_PHYSICAL_CAPACITY"
    elif score["oracle"]<1:
        verdict="COUNTERFACTUAL_ORACLE_OR_TASK_INVALID"
    elif all(score[m]<=.5 for m in ("graph","previous","fifo","lru")):
        verdict="CAPACITY_SYMMETRY_LIMIT_CONFIRMED"
    else:
        verdict="DUAL_CHAIN_INFORMATION_BOUND_NOT_QUALIFIED"
    result.update({"verdict":verdict,"records":records,
      "paired_accuracy":score,"per_family_accuracy":by_family,
      "paired_numerators":tally,"join_candidate_evaluations":ops,
      "graph_feature_multiplications":multiplications,
      "incoming_rejections":rejections,
      "admission_tp":admitted,"admission_fn":missed,
      "physically_impossible_double_answers":physically_impossible_predictions,
      "checkpoint_restores":0})
    return result

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=("development","sealed"),default="development")
    print(json.dumps(run(ap.parse_args().phase),sort_keys=True,indent=2))

"""Yggdrasil NCI-03: four graph motifs falsifying generalization of learned native edge-join.

Trains a Torch relation-join classifier on development-only identities. Its
prediction composes two edges stored in the original native bounded phenotype
pool. Exact symbolic storage and edge enumeration are *not* learned.
"""
from __future__ import annotations
import copy,importlib.util,json,math
from pathlib import Path
import torch
from torch import nn
from yggdrasil.pool import StatePool

torch.set_num_threads(1)
parent=Path(__file__).resolve().parent.parent/"20261014-y-nci01-r2"/"execute.py"
spec=importlib.util.spec_from_file_location("yggdrasil_nci01_frozen",parent)
assert spec and spec.loader
nci01=importlib.util.module_from_spec(spec)
spec.loader.exec_module(nci01)
SEALED=tuple(range(23104,23128))
TRAIN=384
DIM=5
def join_features(a,b):
    return (float(a[1]==b[0]),float(a[0]==b[0]),
            float(a[1]==b[1]),float(a[0]==b[1]),
            float((a[1]-b[0]+256)%7)/7.0)

def join_training():
    torch.manual_seed(17)
    model=nn.Linear(DIM,1)
    features,labels=[],[]
    for i in range(TRAIN):
        a=((i*5+3)%24,(i*7+9)%24)
        good=(a[1],(i*11+13)%24)
        negative=((a[1]+1+i%7)%24,good[1])
        for pair,y in ((good,1.0),(negative,0.0)):
            features.append(join_features(a,pair))
            labels.append([y])
    xx=torch.tensor(features,dtype=torch.float32)
    yy=torch.tensor(labels,dtype=torch.float32)
    optimizer=torch.optim.Adam(model.parameters(),lr=.08)
    for _ in range(200):
        optimizer.zero_grad()
        loss=nn.functional.binary_cross_entropy_with_logits(model(xx),yy)
        loss.backward();optimizer.step()
    weights=tuple(float(x) for x in model.weight.detach().view(-1))
    bias=float(model.bias.detach().item())
    def predict(a,b,cut):
        z=bias+sum(w*x for w,x in zip(weights,join_features(a,b)))
        prob=1/(1+math.exp(-max(-60.,min(60.,z))))
        return prob>=cut
    chosen,best=.5,-1.
    for cut in (.4,.5,.6,.7):
        correct=0
        for i in range(160):
            a=(24+i%8,24+(i*3+1)%8)
            positive=(a[1],24+(i*5+3)%8)
            negative=(24+(a[1]-23+i%6)%8,positive[1])
            if negative[0]==a[1]:
                negative=(24+(negative[0]-23)%8,negative[1])
            correct+=int(predict(a,positive,cut))
            correct+=int(not predict(a,negative,cut))
        accuracy=correct/320
        if accuracy>best:chosen,best=cut,accuracy
    return weights,bias,chosen,best

def memory_edges(pool:StatePool):
    state=pool.state_dict()["storage"][0]
    edges=[]
    for idx in range(nci01.ACTIVE_LIMIT):
        y,x=divmod(idx,nci01.GRID)
        if float(state[2,y,x])>0:
            edges.append((int(state[0,y,x])-1,int(state[1,y,x])-1))
    return edges

def reached(weights,bias,cut,edges,source,target,depth,counts):
    if depth<1 or depth>4:return False
    frontier=list(edges)
    if depth==1:return (source,target) in frontier
    for hop in range(2,depth+1):
        following=set()
        for a in frontier:
            for b in edges:
                counts["join_candidate_evaluations"]+=1
                f=join_features(a,b)
                z=bias+sum(w*x for w,x in zip(weights,f))
                p=1/(1+math.exp(-max(-60.,min(60.,z))))
                if p>=cut:following.add((a[0],b[1]))
        if len(following)>256:return False
        frontier=sorted(following)
    return (source,target) in frontier

def eval_case(admit,weights,bias,cut,seed,work):
    offset=seed*11%32
    nodes=[32+(offset+i*7)%32 for i in range(5)]
    d1,d2=32+(offset+3)%32,32+(offset+11)%32
    backbone=[(nodes[0],nodes[1]),(nodes[1],nodes[2]),(nodes[2],nodes[3])]
    motifs=(
        ((d1,d2),(d2,nodes[1])),
        ((d1,d2),(d2,d1)),
        ((d1,nodes[2]),(d2,d1)),
        ((d1,nodes[3]),(d2,nodes[0])),
    )
    topology_class=seed%4
    links=backbone+list(motifs[topology_class])
    assert len(links)==5 and len(set(a for a,b in links))==5
    pool=nci01.new_native_pool()
    admit_counts={"tp":0,"fp":0,"fn":0,"calls":0}
    def observe(pool,a,b,verb):
        sentence=f"e{a} {verb} e{b}."
        with torch.no_grad():
            prediction=bool(torch.sigmoid(admit(nci01.token_features(sentence))).item()>=.5)
        truth=(verb=="stores")
        admit_counts["calls"]+=1
        if prediction and truth:admit_counts["tp"]+=1
        elif prediction and not truth:admit_counts["fp"]+=1
        elif not prediction and truth:admit_counts["fn"]+=1
        if prediction:nci01.memory_write(pool,a,b)
    for i in range(len(links)):
        a,b=links[(i+seed%len(links))%len(links)]
        observe(pool,a,b,"stores")
    observe(pool,80+seed%5,84+seed%5,"observes")
    edges=memory_edges(pool)
    two=reached(weights,bias,cut,edges,nodes[0],nodes[2],2,work)
    three=reached(weights,bias,cut,edges,nodes[0],nodes[3],3,work)
    neg_two=not reached(weights,bias,cut,edges,nodes[0],nodes[3],2,work)
    neg_three=not reached(weights,bias,cut,edges,nodes[0],nodes[4],3,work)
    direct_only=(nodes[0],nodes[2]) in edges
    oracle_two=((nodes[0],nodes[1]) in edges and (nodes[1],nodes[2]) in edges)
    checkpoint=copy.deepcopy(pool.state_dict())
    restored=nci01.new_native_pool()
    restored.load_state_dict(checkpoint)
    edges=memory_edges(restored)
    interrupted=reached(weights,bias,cut,edges,nodes[0],nodes[2],2,work)
    observe(restored,nodes[3],nodes[4],"stores")
    final_edges=memory_edges(restored)
    retained=reached(weights,bias,cut,final_edges,nodes[0],nodes[2],2,work)
    fresh=reached(weights,bias,cut,final_edges,nodes[0],nodes[4],4,work)
    assert len(final_edges)<=7 and restored.sample_shape==(16,3,3)
    return {"seed":seed,"distinct_start":offset,"topology_class":topology_class,"two_hop":two,
            "three_hop":three,"two_hop_negative":neg_two,
            "three_hop_negative":neg_three,"interrupted":interrupted,
            "old_retained":retained,"new_four_hop":fresh,
            "direct_only_baseline":direct_only,"oracle_two_hop":oracle_two,
            "admission":admit_counts,"active_entries":len(final_edges),
            "state_bytes":576}

def run(phase="development"):
    if phase not in ("development","sealed"):raise ValueError(phase)
    weights,bias,cut,dev=join_training()
    admit,dev_admit,ntrain=nci01.learned_admission()
    result={"schema":"yggdrasil.nci03.motif-join-transfer.v1",
            "phase":phase,"source_parent":"da3163f28596a956fb98ebb76e74ba5995edeb58",
            "join_train_distinct_pairs":768,"join_gradient_updates":200,
            "join_learned_parameters":6,"admission_learned_parameters":4,
            "join_dev_accuracy":dev,"join_threshold":cut,
            "join_weights":weights,"join_bias":bias,
            "admission_dev_accuracy":dev_admit,"admission_train_sentences":ntrain,
            "state_pool_channels":16,"state_bytes":576,"active_limit":7,
            "retained_limit":9,"sealed_heldout_seeds":list(SEALED),
            "learned_join_predicate":True,"learned_relational_storage":False,
            "nci01_full_acceptance":False,
            "external_llm_calls":0,"accepted_ref_mutation":False,
            "verdict":"DEVELOPMENT_ONLY"}
    if phase=="development":return result
    counts={"join_candidate_evaluations":0}
    trials=[eval_case(admit,weights,bias,cut,seed,counts) for seed in SEALED]
    metric_keys=("two_hop","three_hop","two_hop_negative","three_hop_negative",
                 "interrupted","old_retained","new_four_hop",
                 "direct_only_baseline","oracle_two_hop")
    metric={key:sum(bool(t[key]) for t in trials)/len(trials) for key in metric_keys}
    agg={key:sum(t["admission"][key] for t in trials) for key in ("tp","fp","fn","calls")}
    motif_metric={}
    accepted=True
    for motif in range(4):
        group=[row for row in trials if row["topology_class"]==motif]
        assert len(group)==6
        group_accuracy={
            k:sum(bool(row[k]) for row in group)/len(group)
            for k in ("two_hop","three_hop","two_hop_negative",
                      "three_hop_negative","interrupted","new_four_hop")
        }
        motif_metric[str(motif)]=group_accuracy
        if min(group_accuracy.values())<5/6:accepted=False
    verdict=("NATIVE_JOIN_MOTIF_TRANSFER_BOUNDED" if accepted
             else "NATIVE_JOIN_MOTIF_TRANSFER_FALSIFIED")
    result.update({"verdict":verdict,"records":trials,"metric":metric,
                   "motif_metric":motif_metric,
                   "admission":agg,"join_candidate_evaluations":counts["join_candidate_evaluations"],
                   "checkpoint_restores":len(trials),
                   "peak_active_entries":max(t["active_entries"] for t in trials)})
    assert len(trials)==24 and result["peak_active_entries"]<=7
    return result

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=("development","sealed"),default="development")
    args=ap.parse_args()
    print(json.dumps(run(args.phase),sort_keys=True,indent=2))

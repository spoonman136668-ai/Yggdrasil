"""Y-NCI10-R2: development-learned linear merge utility for future queries.

Unlike NCI10's supervised edge-membership proxy, this small bounded policy
portfolio is fitted and selected directly on DEVELOPMENT downstream two-query
performance. Future questions are never given to memory at inference time.
Everything except the merge decision (fixed span encoding/search, pretrained
admission, retention and join) remains the previously frozen native system.
"""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import torch
from torch import nn

HERE=Path(__file__).resolve().parent
P=HERE.parent/"20261014-y-nci10"/"execute.py"
S=importlib.util.spec_from_file_location("y_nci10_frozen",P)
assert S and S.loader
p=importlib.util.module_from_spec(S);S.loader.exec_module(p)
torch.set_num_threads(1)
SEEDS=tuple(range(32512,32536))
TRAIN=tuple(range(32352,32360))
VALID=tuple(range(32384,32392))
# Deliberately tiny hypothesis portfolio; no paid model and no sealed tuning.
CANDIDATES=(
 (0.,0.,0.,0.,0.),
 (2.,1.,0.,0.,-1.),
 (-2.,-1.,0.,0.,1.),
 (0.,0.,-2.,2.,0.),
 (0.,0.,2.,-2.,0.),
 (0.,0.,0.,0.,-1.),
 (0.,0.,0.,0.,1.),
 (1.,0.,-1.,1.,-.5),
 (-1.,0.,1.,-1.,.5),
)
THRESHOLDS=(.4,.6)
_JOIN_CACHE=None
_RETENTION_CACHE=None
def set_model(vec):
    learner=nn.Linear(4,1)
    with torch.no_grad():
        learner.weight.copy_(torch.tensor([vec[:4]],dtype=torch.float32))
        learner.bias.fill_(vec[4])
    return learner
def evaluate(model,threshold,seeds):
    score=ops=merges=0
    # Frozen dev trained-native models cached across policy candidates.
    global _JOIN_CACHE, _RETENTION_CACHE
    if _JOIN_CACHE is None:_JOIN_CACHE=p.nci02.join_training()
    if _RETENTION_CACHE is None:_RETENTION_CACHE=p.prior.train()[0]
    w,b,c,_=_JOIN_CACHE
    p.prior_model=_RETENTION_CACHE
    for seed in seeds:
        for family in range(4):
            chains,facts,_=p.fixture(seed,family)
            public=[{key:f[key] for key in ("edge","exposure","time")} for f in facts]
            _,chunks,nmerge,_,_,ngate=p.learned_retain(public,model,threshold)
            ops+=ngate;merges+=nmerge
            for side in (0,1):
                work={"join_candidate_evaluations":0}
                answer=p.p.compressed_reach(chunks,chains[side][0],chains[side][4],
                                            4,w,b,c,work)
                score+=int(answer)
                ops+=work["join_candidate_evaluations"]
    return score/(len(seeds)*8),ops,merges
def fit_future_query():
    measured=[]
    for i,vec in enumerate(CANDIDATES):
        for threshold in THRESHOLDS:
            learner=set_model(vec)
            score,ops,merges=evaluate(learner,threshold,TRAIN)
            measured.append({"index":i,"threshold":threshold,
              "training_query_accuracy":score,"training_operations":ops,
              "training_merges":merges,"weights":vec})
    # Outcome-trained model selection on development; validation is wholly
    # separated, and all policy values are frozen before sealed cohort.
    measured.sort(key=lambda z:(-z["training_query_accuracy"],
                                z["training_operations"],z["index"],z["threshold"]))
    finalists=measured[:4]
    validated=[]
    for row in finalists:
        score,ops,merges=evaluate(set_model(row["weights"]),row["threshold"],VALID)
        validated.append((score,ops,row["index"],row["threshold"],row["weights"],merges))
    selected=sorted(validated,key=lambda z:(-z[0],z[1],z[2],z[3]))[0]
    accuracy,ops,index,threshold,weights,merges=selected
    return set_model(weights),threshold,len(measured)*len(TRAIN)*8,len(finalists)*len(VALID)*8,accuracy
def run(phase="development"):
    if phase not in ("development","sealed"):raise ValueError(phase)
    p.SEALED=SEEDS
    p.train=fit_future_query
    result=p.run(phase)
    result["schema"]="yggdrasil.nci10r2.future-question-utility-learned-policy.v1"
    result["sealed_seed_range"]=[32512,32536]
    result["scientific_parent"]="ad76ca35ce37531d879cc4371c8c06235f3637dc"
    result["development_training_seeds"]=list(TRAIN)
    result["development_validation_seeds"]=list(VALID)
    result["utility_candidate_count"]=len(CANDIDATES)*len(THRESHOLDS)
    result["utility_finalist_count"]=4
    result["training_objective"]="Two delayed compositional answers per dev state; no future questions at inference"
    result["merge_gate_learned_by"]="Bounded deterministic development query-utility search"
    result["new_representation_learned"]=False
    result["new_graph_search_learned"]=False
    result["future_query_visible_during_inference"]=False
    if phase=="sealed":
        accuracy=result["paired_accuracy"]
        delta=accuracy["learned"]-accuracy["coded"]
        novelty=all(result["family_accuracy"][f]["learned"]>=
                    result["family_accuracy"][f]["coded"]-.10
                    for f in p.FAMILIES[1:])
        if accuracy["oracle"]!=1:verdict="R2_NOVEL_ORACLE_INVALID"
        elif accuracy["learned"]>=.70 and delta>=.10 and novelty:
            verdict="R2_LEARNED_UTILITY_POLICY_TRANSFER"
        elif delta>=.05:verdict="R2_PARTIAL_UTILITY_POLICY_GAIN"
        else:verdict="R2_NO_LEARNED_UTILITY_POLICY_TRANSFER"
        result["verdict"]=verdict
    return result
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=("development","sealed"),default="development")
    print(json.dumps(run(ap.parse_args().phase),indent=2,sort_keys=True))

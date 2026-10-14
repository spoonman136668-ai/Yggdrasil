"""Y-NCI10: learn a bounded two-link merge gate and test exposure-shift falsification.

Only the merge decision is trained (Torch linear model). Adjacency checks,
span-two representation, eviction and graph traversal remain programmed.
Train labels are available only in DEVELOPMENT, never at test inference.
"""
from __future__ import annotations
import copy,importlib.util,json,math
from pathlib import Path
import torch
from torch import nn
P=Path(__file__).resolve().parent.parent/"20261014-y-nci09"/"execute.py"
S=importlib.util.spec_from_file_location("y_nci09_pinned",P)
assert S and S.loader
p=importlib.util.module_from_spec(S);S.loader.exec_module(p)
prior=p.prior
nci02=p.nci02
nci01=p.nci01
torch.set_num_threads(1)
CAP=7
SEALED=tuple(range(31616,31640))
FAMILIES=("development_like","reversed_exposure","uniform_exposure","alternating_decoys")
DEV_TRAIN=tuple(range(30720,30768))
DEV_VALID=tuple(range(30816,30832))
FEATURES=4
def fixture(seed,family):
    # Novel graph grammar: distractors touch target chains rather than being
    # disconnected. The two length-four paths remain independently recoverable.
    a=[64+(seed*3+5*i)%16 for i in range(5)]
    b=[96+(seed*7+3*i)%16 for i in range(5)]
    main=[(nodes[i],nodes[i+1]) for nodes in (a,b) for i in range(4)]
    d=[(a[1],146+seed%3),(b[2],152+seed%3),
       (160+seed%3,a[2]),(168+seed%3,b[1])]
    edges=main+d
    assert len(edges)==len(set(edges))==12
    order=[
       (0,4,8,1,5,9,2,6,10,3,7,11),
       (8,0,9,4,1,10,5,2,11,6,3,7),
       (0,1,8,4,5,9,2,6,10,3,7,11),
       (8,4,0,9,5,1,10,6,2,11,7,3)][family]
    facts=[]
    for t,index in enumerate(order):
        main_edge=index<8
        exposure=4 if main_edge else 1
        if family==1:exposure=1 if main_edge else 4
        elif family==2:exposure=2
        elif family==3:exposure=(4 if (index%2)==0 else 1)
        facts.append({"edge":edges[index],"exposure":exposure,"time":t,
                      "development_truth_main":main_edge})
    return (a,b),facts,edges
def feature(old,new,all_chunks):
    # Candidate adjacency already established by hard-coded source matching.
    oa,ob=old["a"],old["b"]
    na,nb=new["a"],new["b"]
    degree=sum(1 for ch in all_chunks if ch["span"]==1
               and (ch["a"] in (oa,ob,na,nb) or ch["b"] in (oa,ob,na,nb)))
    return [min(old["exposure"],new["exposure"])/4,
        (old["exposure"]+new["exposure"])/8,
        abs(old["time"]-new["time"])/12,
        min(4,degree)/4]
def dev_examples(seeds):
    xx,yy=[],[]
    for seed in seeds:
        for family in (0,3):
            _,facts,_=fixture(seed,family)
            previous=[]
            for fact in facts:
                a,b=fact["edge"]
                item={"a":a,"b":b,"span":1,"exposure":fact["exposure"],
                      "time":fact["time"],"development_truth_main":fact["development_truth_main"]}
                for old in previous:
                    if old["b"]==a or b==old["a"]:
                        xx.append(feature(old,item,previous+[item]))
                        yy.append(float(old["development_truth_main"] and item["development_truth_main"]))
                previous.append(item)
    assert len(xx)>0 and len(xx)==len(yy)
    return torch.tensor(xx,dtype=torch.float32),torch.tensor(yy,dtype=torch.float32).view(-1,1)
def train():
    x,y=dev_examples(DEV_TRAIN)
    torch.manual_seed(1818)
    model=nn.Linear(FEATURES,1)
    opt=torch.optim.Adam(model.parameters(),lr=.08)
    for _ in range(160):
        opt.zero_grad()
        loss=nn.functional.binary_cross_entropy_with_logits(model(x),y)
        loss.backward();opt.step()
    vx,vy=dev_examples(DEV_VALID)
    with torch.no_grad():
        probs=torch.sigmoid(model(vx)).view(-1).tolist()
        truth=vy.view(-1).tolist()
    thresholds=(.35,.45,.5,.55,.65,.75)
    best=max(thresholds,key=lambda cut:
        (sum(int((p>=cut)==bool(t)) for p,t in zip(probs,truth))/len(truth),-abs(cut-.5)))
    acc=sum(int((p>=best)==bool(t)) for p,t in zip(probs,truth))/len(truth)
    return model,best,len(x),len(vx),acc
def learned_retain(facts,model,threshold):
    pool=nci01.new_native_pool()
    merges=rejects=multiplications=merge_logits=0
    for fact in facts:
        a,b=fact["edge"]
        kept=p.chunks_from_pool(pool)
        incoming={"a":a,"b":b,"span":1,"exposure":fact["exposure"],"time":fact["time"]}
        compatible=[]
        for k,old in enumerate(kept):
            if old["span"]==1 and (old["b"]==a or b==old["a"]):
                compatible.append((k,feature(old,incoming,kept+[incoming])))
        idx=None
        if compatible:
            with torch.no_grad():
                v=torch.tensor([f for _,f in compatible],dtype=torch.float32)
                probs=torch.sigmoid(model(v)).view(-1).tolist()
            merge_logits+=len(probs)
            matches=[(score,k) for (k,_),score in zip(compatible,probs) if score>=threshold]
            if matches:idx=max(matches,key=lambda item:(item[0],-item[1]))[1]
        if idx is not None:
            old=kept[idx]
            kept[idx]={"a":old["a"] if old["b"]==a else a,
                "b":b if old["b"]==a else old["b"],
                "span":2,"exposure":max(old["exposure"],incoming["exposure"]),
                "time":min(old["time"],incoming["time"])}
            merges+=1
        else:kept.append(incoming)
        if len(kept)>CAP:
            considered=p.retained_features(kept)
            inputs=torch.tensor([prior.features(v,considered) for v in considered],
                                dtype=torch.float32)
            with torch.no_grad():scores=torch.sigmoid(prior_model(inputs)).view(-1).tolist()
            multiplications+=len(kept)*3
            victim=min(range(len(kept)),key=lambda k:(scores[k],k))
            if victim==len(kept)-1:rejects+=1
            kept.pop(victim)
        p.restore_native(pool,kept)
    return pool,p.chunks_from_pool(pool),merges,rejects,multiplications,merge_logits
prior_model=None
def run(phase="development"):
    global prior_model
    if phase not in ("development","sealed"):raise ValueError(phase)
    gate,threshold,train_n,dev_n,dev_acc=train()
    prior_model,_,_=prior.train()
    result={"schema":"yggdrasil.nci10.learned-merge-gate.v1",
       "phase":phase,"scientific_parent":"033d3618aa006ee7b9502dc2ff522744d74affe2",
       "training_examples":train_n,"validation_examples":dev_n,
       "development_accuracy":dev_acc,"merge_threshold":threshold,
       "merge_weights":[float(v) for v in gate.weight.detach().view(-1)],
       "merge_bias":float(gate.bias.detach().item()),"merge_gate_parameters":5,
       "features_hand_coded":True,"span_representation_learned":False,
       "retention_parameters":4,"join_parameters":6,
       "sealed_seed_range":[31616,31640],"family_names":list(FAMILIES),
       "active_slots":7,"native_state_bytes":576,"native_memory_byte_matched":True,
       "external_llm_calls":0,"accepted_ref_mutation":False,
       "nci01_full_acceptance":False,"verdict":"DEVELOPMENT_ONLY"}
    if phase=="development":
        pool,chunks,_,_,_,_=learned_retain(
          [{"edge":(1,2),"exposure":4,"time":0},
           {"edge":(2,3),"exposure":4,"time":1}],gate,threshold)
        assert len(chunks)<=2 and pool.state_dict()["storage"].numel()*4==576
        return result
    admission,_,_=nci01.learned_admission()
    weights,bias,cut,_=nci02.join_training()
    summary={mode:0 for mode in ("learned","coded","graph","oracle")}
    byfam={f:{mode:0 for mode in summary} for f in FAMILIES}
    work={"learned":0,"coded":0,"graph":0}
    mergers={"learned":0,"coded":0}
    feature_work=merge_evaluations=rejected=admitted=missed=restored=0
    records=[]
    for seed in SEALED:
      for family in range(4):
        chains,raw,oracle_edges=fixture(seed,family)
        stream=[]
        for fact in raw:
            a,b=fact["edge"]
            with torch.no_grad():
                predicted=bool(torch.sigmoid(admission(nci01.token_features(
                           f"e{a} stores e{b}."))).item()>=.5)
            if predicted:
                stream.append({k:fact[k] for k in ("edge","exposure","time")})
                admitted+=1
            else:missed+=1
        learned_pool,learned_chunks,merged,deny,mul,logits=learned_retain(
             stream,gate,threshold)
        coded_pool,coded_chunks,coded_merge,_,_=p.retain(stream,prior_model)
        graph_pool,graph_edges,_,_=prior.retain(stream,prior_model)
        mergers["learned"]+=merged;mergers["coded"]+=coded_merge
        feature_work+=mul;merge_evaluations+=logits;rejected+=deny
        snapshot=copy.deepcopy(learned_pool.state_dict())
        recovered=nci01.new_native_pool();recovered.load_state_dict(snapshot)
        assert p.chunks_from_pool(recovered)==learned_chunks
        restored+=1
        assert len(learned_chunks)<=CAP and len(coded_chunks)<=CAP and len(graph_edges)==CAP
        row={"seed":seed,"family":FAMILIES[family],
          "learned_chunks":len(learned_chunks),"coded_chunks":len(coded_chunks),
          "learned_merges":merged,"coded_merges":coded_merge,
          "learned_coverage":sum(v["span"] for v in learned_chunks)}
        for side in (0,1):
            for name,items in (("learned",p.chunks_from_pool(recovered)),
                               ("coded",coded_chunks)):
                count={"join_candidate_evaluations":0}
                answer=p.compressed_reach(items,chains[side][0],chains[side][4],
                         4,weights,bias,cut,count)
                work[name]+=count["join_candidate_evaluations"]
                row[f"{name}_{side}"]=answer
                summary[name]+=int(answer)
                byfam[FAMILIES[family]][name]+=int(answer)
            count={"join_candidate_evaluations":0}
            found=nci02.reached(weights,bias,cut,graph_edges,
                     chains[side][0],chains[side][4],4,count)
            work["graph"]+=count["join_candidate_evaluations"]
            oracle=p.previous.exact_oracle(oracle_edges,chains[side][0],chains[side][4],4)
            for name,value in (("graph",found),("oracle",oracle)):
                row[f"{name}_{side}"]=value
                summary[name]+=int(value);byfam[FAMILIES[family]][name]+=int(value)
        records.append(row)
    assert len(records)==96
    accuracies={name:value/192 for name,value in summary.items()}
    per={fam:{name:value/48 for name,value in data.items()} for fam,data in byfam.items()}
    delta=accuracies["learned"]-accuracies["coded"]
    # Strong acceptance needs both overall transfer and strict novel shifts.
    shifted_safe=all(per[f]["learned"]>=per[f]["coded"]-.10 for f in FAMILIES[1:])
    if accuracies["oracle"]!=1:verdict="NOVEL_GRAPH_ORACLE_INVALID"
    elif accuracies["learned"]>=.70 and delta>=.10 and shifted_safe:
        verdict="LEARNED_MERGE_GATE_TRANSFER"
    elif delta>=.05:verdict="PARTIAL_LEARNED_MERGE_GAIN"
    else:verdict="NO_LEARNED_MERGE_TRANSFER"
    result.update({"verdict":verdict,"records":records,"paired_accuracy":accuracies,
       "family_accuracy":per,"learned_minus_coded":delta,
       "join_candidate_evaluations":work,"merges":mergers,
       "gate_inference_evaluations":merge_evaluations,
       "graph_feature_multiplies":feature_work,"incoming_rejections":rejected,
       "admission_tp":admitted,"admission_fn":missed,
       "checkpoint_restores":restored})
    return result
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=("development","sealed"),default="development")
    print(json.dumps(run(ap.parse_args().phase),indent=2,sort_keys=True))

"""Y-NCI09: prospective bounded path-chunk compression in native StatePool.

The existing Torch 4-weight retention and 6-weight learned relation join
remain frozen. The experimental native memory stores a two-edge path as one
span-2 item when its two edges have both been publicly observed. Compression,
path-span arithmetic and adjacency checks are explicit code, NOT learned.
No future task identity or sealed oracle enters memory decisions.
"""
from __future__ import annotations
import copy,importlib.util,json,math
from pathlib import Path
import torch
P=Path(__file__).resolve().parent.parent/"20261014-y-nci07"/"execute.py"
S=importlib.util.spec_from_file_location("y_nci07_frozen",P)
assert S and S.loader
prior=importlib.util.module_from_spec(S);S.loader.exec_module(prior)
previous=prior.previous
nci02=prior.nci02
nci01=prior.nci01
torch.set_num_threads(1)
SEEDS=tuple(range(30208,30232))
FAMILIES=("interleaved","first_early","second_early","noise_interleaved")
CAP=7
BYTES=576
def fixture(seed,family):
    # Same task grammar as NCI08, disjoint prospective seeds: mechanism test,
    # not an independent new grammar or broad generalization claim.
    chains=(
      [64+(seed*3+5*i)%16 for i in range(5)],
      [96+(seed*7+3*i)%16 for i in range(5)])
    edges=[(chains[c][i],chains[c][i+1]) for c in range(2) for i in range(4)]
    edges += [(128+4*i+seed%3,150+4*i+seed%3) for i in range(4)]
    order=((0,4,1,5,2,6,3,7,8,9,10,11),
           (0,1,2,3,4,5,6,7,8,9,10,11),
           (4,5,6,7,0,1,2,3,8,9,10,11),
           (8,0,4,9,1,5,10,2,6,11,3,7))[family]
    facts=[{"edge":edges[i],"exposure":1+(seed+t)%4,"time":t} for t,i in enumerate(order)]
    assert len(set(edges))==12
    return chains,facts,edges
def chunks_from_pool(pool):
    state=pool.state_dict()["storage"][0]
    out=[]
    for i in range(CAP):
        row,col=divmod(i,nci01.GRID)
        if float(state[2,row,col])>0:
            out.append({"a":int(state[0,row,col])-1,
                        "b":int(state[1,row,col])-1,
                        "span":int(state[3,row,col]),
                        "exposure":int(state[4,row,col]),
                        "time":int(state[5,row,col])})
    return out
def restore_native(pool,chunks):
    assert len(chunks)<=CAP and all(1<=c["span"]<=2 for c in chunks)
    state=torch.zeros_like(pool.state_dict()["storage"])
    for idx,c in enumerate(chunks):
        row,col=divmod(idx,nci01.GRID)
        for channel,value in enumerate((c["a"]+1,c["b"]+1,1,c["span"],c["exposure"],c["time"])):
            state[0,channel,row,col]=float(value)
    pool.update(torch.tensor([0]),state)
    assert pool.state_dict()["storage"].numel()*4==BYTES
def retained_features(chunks):
    return [{"edge":(x["a"],x["b"]),"exposure":x["exposure"],"time":x["time"]} for x in chunks]
def retain(facts,model):
    pool=nci01.new_native_pool()
    merges=rejects=score_muls=0
    for fact in facts:
        a,b=fact["edge"]
        current=chunks_from_pool(pool)
        next_chunk={"a":a,"b":b,"span":1,"exposure":fact["exposure"],"time":fact["time"]}
        matching=next((i for i,old in enumerate(current) if old["span"]==1
             and (old["b"]==a or b==old["a"])),None)
        if matching is not None:
            old=current[matching]
            current[matching]={"a":old["a"] if old["b"]==a else a,
               "b":b if old["b"]==a else old["b"],"span":2,
               "exposure":max(old["exposure"],next_chunk["exposure"]),
               "time":min(old["time"],next_chunk["time"])}
            merges+=1
        else:
            current.append(next_chunk)
        if len(current)>CAP:
            features=retained_features(current)
            inputs=torch.tensor([prior.features(v,features) for v in features],dtype=torch.float32)
            with torch.no_grad():
                score=torch.sigmoid(model(inputs)).view(-1).tolist()
            score_muls+=len(current)*3
            victim=min(range(len(current)),key=lambda k:(score[k],k))
            if victim==len(current)-1:rejects+=1
            current.pop(victim)
        restore_native(pool,current)
    chunks=chunks_from_pool(pool)
    assert len(chunks)<=CAP
    return pool,chunks,merges,rejects,score_muls
def compressed_reach(chunks,source,target,length,weights,bias,cut,work):
    # Only public stored macro boundaries and their exact hop spans are used.
    frontier=[(source,0,None)]
    for _ in range(length):
        nxt=[]
        for node,hops,prior_edge in frontier:
            for item in chunks:
                if item["a"]!=node or hops+item["span"]>length:continue
                edge=(item["a"],item["b"])
                if prior_edge is not None:
                    work["join_candidate_evaluations"]+=1
                    features=nci02.join_features(prior_edge,edge)
                    z=bias+sum(w*x for w,x in zip(weights,features))
                    if 1/(1+math.exp(-max(-60.,min(60.,z))))<cut:continue
                new_hops=hops+item["span"]
                if new_hops==length and item["b"]==target:return True
                if new_hops<length:nxt.append((item["b"],new_hops,edge))
        if not nxt:break
        if len(nxt)>256:return False
        frontier=nxt
    return False
def run(phase="development"):
    if phase not in ("development","sealed"):raise ValueError(phase)
    model,ntrain,dev=prior.train()
    result={"schema":"yggdrasil.nci09.native-two-link-chunk-memory.v1",
        "phase":phase,"source_parent":"f1ca8e60a11ce2e9568287f8d6d3cd5d8ea2d3c3",
        "dev_examples":ntrain,"dev_accuracy":dev,"retention_parameters":4,
        "learned_join_parameters":6,"native_state_bytes":BYTES,"active_cap":CAP,
        "sealed_seed_range":[30208,30232],"families":list(FAMILIES),
        "compressed_spans_learned":False,"join_model_unchanged":True,
        "compression_rule_hand_coded":True,"external_llm_calls":0,
        "accepted_ref_mutation":False,"nci01_full_acceptance":False,
        "verdict":"DEVELOPMENT_ONLY"}
    if phase=="development":
        p,_,merged,_,_=retain([
          {"edge":(1,2),"exposure":1,"time":0},
          {"edge":(2,3),"exposure":1,"time":1}],model)
        assert merged==1 and chunks_from_pool(p)[0]["span"]==2
        return result
    previous_model,_,_=previous.learner()
    weights,bias,cut,_=nci02.join_training()
    admit,_,_=nci01.learned_admission()
    records=[]
    total_work={"compressed":{"join_candidate_evaluations":0},
                "graph":{"join_candidate_evaluations":0}}
    merges=rejected=score_muls=admitted=missed=restores=0
    answers={"compressed":0,"graph":0,"oracle":0}
    families={f:{"compressed":0,"graph":0,"oracle":0} for f in FAMILIES}
    for seed in SEEDS:
        for family in range(4):
            chains,facts,full_edges=fixture(seed,family)
            stream=[]
            for fact in facts:
                a,b=fact["edge"]
                with torch.no_grad():
                    accepted=bool(torch.sigmoid(admit(nci01.token_features(f"e{a} stores e{b}."))).item()>=.5)
                if accepted:stream.append(fact);admitted+=1
                else:missed+=1
            pool,compressed,merged,denied,mults=retain(stream,model)
            graph_pool,graph_edges,_,_=prior.retain(stream,model)
            merges+=merged;rejected+=denied;score_muls+=mults
            snapshot=copy.deepcopy(pool.state_dict())
            recovered=nci01.new_native_pool();recovered.load_state_dict(snapshot)
            assert chunks_from_pool(recovered)==compressed
            restores+=1
            row={"seed":seed,"family":FAMILIES[family],
                "native_edges":len(compressed),"compressed_chunk_count":sum(x["span"]==2 for x in compressed),
                "compressed_coverage":sum(x["span"] for x in compressed),"merged_count":merged,
                "graph_edges":len(graph_edges)}
            for side in range(2):
                c=compressed_reach(chunks_from_pool(recovered),chains[side][0],
                      chains[side][4],4,weights,bias,cut,total_work["compressed"])
                g=nci02.reached(weights,bias,cut,graph_edges,chains[side][0],
                      chains[side][4],4,total_work["graph"])
                o=previous.exact_oracle(full_edges,chains[side][0],chains[side][4],4)
                for name,value in (("compressed",c),("graph",g),("oracle",o)):
                    row[f"{name}_{side}"]=value
                    answers[name]+=int(value);families[FAMILIES[family]][name]+=int(value)
            records.append(row)
    assert len(records)==96
    acc={name:score/192 for name,score in answers.items()}
    by_family={f:{name:score/48 for name,score in per.items()} for f,per in families.items()}
    safe=all(x["native_edges"]<=CAP and x["compressed_coverage"]<=14 for x in records)
    verdict="NO_TWO_LINK_CHUNK_COMPOSITION_GAIN"
    if acc["oracle"]==1 and safe and acc["compressed"]>=.75 and acc["compressed"]-acc["graph"]>=.15:
        verdict="CODED_TWO_LINK_COMPRESSION_RESTORES_BOUNDED_RECALL"
    elif acc["compressed"]-acc["graph"]>=.05:
        verdict="PARTIAL_TWO_LINK_CHUNK_RECALL_GAIN"
    result.update({"records":records,"paired_accuracy":acc,"per_family":by_family,
       "join_candidate_evaluations":{k:v["join_candidate_evaluations"] for k,v in total_work.items()},
       "compression_merges":merges,"incoming_rejections":rejected,
       "graph_scorer_feature_multiplies":score_muls,
       "checkpoint_restores":restores,"admission_true_positive":admitted,
       "admission_false_negative":missed,"verdict":verdict})
    return result
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--phase",choices=("development","sealed"),default="development")
    print(json.dumps(run(ap.parse_args().phase),indent=2,sort_keys=True))

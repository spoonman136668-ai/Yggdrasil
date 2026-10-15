"""Y-F17: no-retuning scalarization of F15 frozen neural stopping decision.

Original model, source witness, threshold and recurrent core remain frozen.
Replace repeated tiny torch policy invocations with identical scalar MLP
math, amortized into model initialization; keep full typed core unchanged.
Original Torch decisions MUST equal scalar decisions for every new case.
"""
from __future__ import annotations
import importlib.util, math, statistics, json, time
from collections import Counter
from pathlib import Path
import torch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf15_original",HERE.parent/"20261014-y-f15"/"execute.py")
assert spec and spec.loader
f15=importlib.util.module_from_spec(spec)
spec.loader.exec_module(f15)
f10=f15.f10
FAMS=(80,81,82,83)
SEEDS=range(70800,70806)
REPEATS=3
torch.set_num_threads(1)

def frozen_scalar_params(core,head):
    with torch.no_grad():
        w=head.m[0].weight.tolist()
        b=head.m[0].bias.tolist()
        v=head.m[2].weight[0].tolist()
        c=float(head.m[2].bias[0])
        lut=[[1/(1+math.exp(-float(x))) for x in row]
             for row in core.role_logits.detach().tolist()]
    return (w,b,v,c),lut

def scalar_risk(params,feat):
    w,b,v,c=params
    z=c
    for i in range(12):
        h=math.tanh(b[i]+sum(w[i][j]*feat[j] for j in range(8)))
        z+=v[i]*h
    return 1/(1+math.exp(-z)) if z>=0 else math.exp(z)/(1+math.exp(z))

def novel(seed,family,k,shift):
    # Declared generator derivation: previously qualified F15 motifs,
    # freshly authored seeds, then replace one distractor with a NEW
    # post-target branch, preserving all exact labeled paths.
    original=f15.graph(seed,family-4,k,shift)
    chain={(f10.f1.relabel(i,seed,2),f10.f1.relabel(i+1,seed,2))
           for i in range(k)}
    out=[]
    for edges,roles,q,pattern,label,variant in original:
        new=list(edges)
        candidates=[i for i,e in enumerate(new) if e not in chain]
        assert len(candidates)>=2
        branch=(f10.f1.relabel(k,seed,2),
                f10.f1.relabel(k+20+family,seed,2))
        assert branch not in new
        new[candidates[0]]=branch
        assert f10.typed_exact(new,roles,*q,pattern)==label
        out.append((new,roles,q,pattern,label,variant))
    return out

def scalar_online(core,params,lut,edges,types,q,seq):
    with torch.no_grad():
        facts=torch.tensor([edges],dtype=torch.int32)
        typ=torch.tensor([types],dtype=torch.int64)
        query=torch.tensor([q],dtype=torch.int32)
        state=core.encode(facts,typ)
        assert tuple(state.shape)==(1,144) and state.element_size()==4
        bits=state[:,:12].contiguous().view(torch.int32).long()
        src=(bits>>16)&65535
        dst=bits&65535
        tag=state[:,12:24].long()
        link=core.core.similarity(dst[:,:,None],src[:,None,:])*f10.f6.f4.MASK.to(src)
        act=core.core.similarity(query[:,0,None],src)
        finish=core.core.similarity(dst,query[:,1,None])
        k=len(seq)
        prev=0.
        for step,role in enumerate(seq):
            gate=torch.sigmoid(core.role_logits[tag,torch.tensor([[role]])])
            if step:
                msg=torch.bmm(act.unsqueeze(1),link).squeeze(1)
                act=torch.sigmoid(core.core.message_gain*msg+
                    core.core.recurrent_gain*act+core.core.activation_bias)
            act=act*gate
            prob=float(torch.sigmoid(core.core.output_gain*(act*finish).sum(-1)
                                    +core.core.output_bias))
            halt=False
            if prob<.5:
                vals=act[0].tolist()
                mean=sum(vals)/12
                std=(sum((x-mean)**2 for x in vals)/12)**.5
                nextmax=max(lut[int(r)][seq[step+1]] for r in types) if step+1<k else 0.
                feat=(prob,prob-prev,max(vals),mean,std,
                      (step+1)/k,1-(step+1)/k,nextmax)
                halt=scalar_risk(params,feat)>=.7
            if halt or step==k-1:
                return {"answer":bool(prob>=.5),"steps":step+1,
                        "halt":bool(halt and step<k-1)}
            prev=prob
    raise AssertionError("missing terminal")

def evaluate():
    start=time.perf_counter()
    core,head,frozen_sha=f15.recovered()
    assert len(frozen_sha)==64 # new train-only reconstructed identity; NOT exact F15 archived head
    params,lut=frozen_scalar_params(core,head)
    rows=[]
    for seed in SEEDS:
      for family in FAMS:
       for k in (7,8):
        for shift in (0,1):
         for edges,roles,q,seq,truth,variant in novel(seed,family,k,shift):
            row={"seed":seed,"family":family,"depth":len(seq),
                 "variant":variant,"shift":shift,"truth":truth,
                 "answers":{},"timing_ns":{}}
            modes=("scalar","old_nn","full","static")
            def call(mode):
                if mode=="scalar":
                    return scalar_online(core,params,lut,edges,roles,q,seq)
                return f15.online(core,head,edges,roles,q,seq,
                                  "risk" if mode=="old_nn" else mode)
            for mode in modes:
                row["answers"][mode]=call(mode)
            if row["answers"]["scalar"]!=row["answers"]["old_nn"]:
                raise AssertionError(("FROZEN_SCALAR_STOP_MISMATCH",seed,family,k,shift,variant,
                       row["answers"]["scalar"],row["answers"]["old_nn"]))
            row["timing_ns"]={mode:[0]*REPEATS for mode in modes}
            for repeat in range(REPEATS):
                offset=(seed+family+variant+repeat)%4
                for j in range(4):
                    mode=modes[(offset+j)%4]
                    begin=time.perf_counter_ns()
                    result=call(mode)
                    elapsed=time.perf_counter_ns()-begin
                    assert result==row["answers"][mode],"NONDETERMINISTIC_ANSWER"
                    row["timing_ns"][mode][repeat]=elapsed
            rows.append(row)
    assert len(rows)==576
    stats={}
    for mode in ("scalar","old_nn","full","static"):
        correct=fp=fn=steps=full=0
        duration=[0]*REPEATS
        family_errors=Counter()
        for row in rows:
            out=row["answers"][mode]
            correct+=out["answer"]==row["truth"]
            if row["truth"] and not out["answer"]:
                fn+=1;family_errors[(row["family"],"fn")]+=1
            if not row["truth"] and out["answer"]:
                fp+=1;family_errors[(row["family"],"fp")]+=1
            steps+=out["steps"];full+=row["depth"]
            for i in range(REPEATS):duration[i]+=row["timing_ns"][mode][i]
        stats[mode]={"correct":correct,"accuracy":correct/576,
            "false_positive_count":fp,"false_negative_count":fn,
            "worst_family_FNR":max(family_errors[(fam,"fn")]/48 for fam in FAMS),
            "worst_family_FPR":max(family_errors[(fam,"fp")]/96 for fam in FAMS),
            "steps":steps,"full_steps":full,"step_saving":1-steps/full,
            "wall_ns_by_repeat":duration}
    gains={arm:[1-n/f for n,f in zip(stats[arm]["wall_ns_by_repeat"],
             stats["full"]["wall_ns_by_repeat"])]
           for arm in ("scalar","old_nn","static")}
    versus=[1-a/b for a,b in zip(stats["scalar"]["wall_ns_by_repeat"],
                                 stats["old_nn"]["wall_ns_by_repeat"])]
    s=stats["scalar"];full=stats["full"]
    robust=(s["accuracy"]>=.95 and s["worst_family_FNR"]<=.05 and
        s["worst_family_FPR"]<=.05 and s["accuracy"]>=full["accuracy"]-.03)
    efficient=(s["step_saving"]>=.15 and
        statistics.median(gains["scalar"])>=.05 and
        statistics.median(versus)>=.05 and
        statistics.median(gains["scalar"])>=statistics.median(gains["static"])+.05)
    verdict=("DEVELOPMENT_FROZEN_SCALAR_OUTPERFORMS_CHEAP_STATIC" if robust and efficient else
       "DEVELOPMENT_FROZEN_SCALAR_ROBUST_NO_NET_GAIN" if robust else
       "DEVELOPMENT_FROZEN_SCALAR_POLICY_NOT_ROBUST")
    if full["accuracy"]<.95:verdict="INVALID_TYPED_FULL_CONTROL"
    return {"schema":"yggdrasil.f17.reconstructed-risk-scalar-development.v1",
        "stage":"DEVELOPMENT_ONLY","parent_F15_sha":"ada4c0a3d5a8f674beb693f12d5640e6dad951c6",
        "original_F15_result_sha256":"0d1259b885d90607f4076d6f0ddea5fab69cc2ef5a34c494cb2a28a83c425d97",
        "frozen_head_sha256":frozen_sha,
        "exact_F15_checkpoint_recovered":False,
        "reconstructed_from_historical_training_only":True,
        "archived_new_policy_parameters":{k:v.detach().tolist() for k,v in head.state_dict().items()},"frozen_threshold":.7,
        "source_born_independently":False,"sealed_first_use":False,
        "accepted_ref_mutation":False,"model_retrained":False,
        "families":list(FAMS),"family_derivation_disclosed":True,
        "new_seed_bounds":[70800,70806],"graphs":96,"questions":576,
        "positives":192,"negatives":384,"state_bytes":576,"repeats":REPEATS,
        "scalar_model_precomputed_at_load":True,"same_answer_and_halt_step":True,
        "timing_includes_feature_and_policy_overhead":True,
        "timing_excludes_one_time_model_load":True,"machine_local_only":True,
        "wall_saved_by_repeat":gains,"scalar_vs_old_nn_saved_by_repeat":versus,
        "scores":stats,"rows":rows,"registered_verdict":("DEVELOPMENT_RECONSTRUCTED_SOURCE_"+verdict),
        "original_wall_ms":round((time.perf_counter()-start)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))

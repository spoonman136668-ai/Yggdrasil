"""Y-NCI11-R2 prospective first-use: frozen trained native state-former.

New unseen graph grammars 8-11, balanced graph-counterfactual questions, native
StatePool 576-byte checkpoints. Model source/seed and development-fit state SHA
are locked BEFORE cohort generation. Exact programmed compressor is only a
frozen control, never part of learned memory.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, struct, time
from pathlib import Path
import torch
import torch.nn.functional as F
from yggdrasil.pool import StatePool

BASE=Path(__file__).resolve().parent.parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
r2=load("nci11r2_frozen_dev",BASE/"20261014-y-nci11r2"/"execute.py")
old=r2.prior
coded=load("nci09_frozen_coded_control",BASE/"20261014-y-nci09"/"execute.py")
torch.set_num_threads(1)
SEEDS=tuple(range(36544,36568))
FAMILIES=(8,9,10,11)
def train_frozen():
    torch.manual_seed(900)
    model=r2.LearnedRecurrentState("recurrent_write_gate")
    x,y,labels=old.dataset(r2.TRAIN,(0,1))
    opt=torch.optim.Adam(model.parameters(),lr=.018)
    for _ in range(100):
        opt.zero_grad()
        loss=F.binary_cross_entropy_with_logits(model(x,y),labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(),3)
        opt.step()
    vx,vq,vt=old.dataset(r2.VALID,(2,3))
    with torch.no_grad():
        val=r2.accuracy(model(vx,vq),vt)
        zero=r2.accuracy(model.logits(torch.zeros((len(vx),12,12)),vq),vt)
    # Byte-exact development model witness; hash includes ordered tensor name,
    # dtype, shape and little-endian float contents; never sealed labels.
    hasher=hashlib.sha256()
    for name,tensor in sorted(model.state_dict().items()):
        t=tensor.detach().cpu().contiguous()
        hasher.update(name.encode()+b"\0")
        hasher.update(str(t.dtype).encode()+b"\0")
        hasher.update(repr(tuple(t.shape)).encode()+b"\0")
        for value in t.reshape(-1).tolist():
            hasher.update(struct.pack("<f",float(value)))
    return model,{"frozen_weight_sha256":hasher.hexdigest(),
        "development_validation_accuracy":val,"development_zero_memory":zero,
        "trained_parameter_count":sum(p.numel() for p in model.parameters()),
        "trained_parameter_bytes_float32":sum(p.numel() for p in model.parameters())*4}
def fixture(seed,family,ca,cb):
    observed,questions,truth,full=old.fixture(seed,family-8,ca,cb)
    a=[64+(seed*3+5*i)%16 for i in range(5)]
    b=[96+(seed*7+3*i)%16 for i in range(5)]
    x,y,z,w=[400+(seed%11)*4+i for i in range(4)]
    patterns={
        8:[(a[1],x),(x,a[1]),(b[2],y),(y,b[2])],
        9:[(x,a[1]),(a[1],y),(z,b[2]),(b[2],w)],
        10:[(a[2],x),(a[2],y),(b[1],z),(b[1],w)],
        11:[(x,a[1]),(y,a[2]),(z,b[1]),(w,b[2])],
    }
    decoys=patterns[family]
    original=full[-4:]
    assert len(set(original))==4
    mapping=dict(zip(original,decoys))
    current=[mapping.get(e,e) for e in observed]
    all_edges=full[:8]+decoys
    assert len(current)==12 and len(set(current))==12
    assert set(current)==set(all_edges)
    return current,questions,truth,all_edges
def encoded():
    records=[]
    for seed in SEEDS:
        for fam in FAMILIES:
            for ca in (False,True):
                for cb in (False,True):
                    edges,questions,truth,full=fixture(seed,fam,ca,cb)
                    records.append((seed,fam,ca,cb,edges,questions,truth,full))
    assert len(records)==384
    return records
def evaluate(model):
    rows=encoded()
    features=torch.stack([old.feature(torch.tensor(r[4],dtype=torch.long)) for r in rows])
    queries=torch.stack([old.feature(torch.tensor(r[5],dtype=torch.long)) for r in rows])
    with torch.no_grad():
        learned_state=model.memory(features)
        learned_logits=model.logits(learned_state,queries)
        zero_logits=model.logits(torch.zeros_like(learned_state),queries)
        torch.manual_seed(900)
        initial=r2.LearnedRecurrentState("recurrent_write_gate")
        init_logits=initial(features,queries)
    original_retainer,_,_=coded.prior.train()
    join,bias,threshold,_=coded.nci02.join_training()
    outcomes=[]
    summary={key:0 for key in ("trained","initial","zero","coded","oracle")}
    groups={str(f):{key:0 for key in summary} for f in FAMILIES}
    coded_ops=restore_count=0
    state_start=time.perf_counter()
    for ix,(seed,fam,ca,cb,edges,qs,truth,full) in enumerate(rows):
        tensor=learned_state[ix].reshape(1,16,3,3)
        native=StatePool(torch.zeros((1,16,3,3),dtype=torch.float32),capacity=1)
        native.update(torch.tensor([0]),tensor.detach())
        checkpoint=copy.deepcopy(native.state_dict())
        recovered=StatePool(torch.zeros((1,16,3,3),dtype=torch.float32),capacity=1)
        recovered.load_state_dict(checkpoint)
        if not torch.equal(recovered.state_dict()["storage"],tensor):
            raise RuntimeError("native StatePool checkpoint not identical")
        restore_count+=1
        stream=[{"edge":e,"exposure":2,"time":i} for i,e in enumerate(edges)]
        _,chunks,_,_,_=coded.retain(stream,original_retainer)
        assert len(chunks)<=7
        row={"seed":seed,"family":fam,"cut_a":ca,"cut_b":cb,
             "truth":[bool(t) for t in truth],"memory_bytes":576,
             "stored_compressed_edges":len(chunks),"answer":{}}
        for side in (0,1):
            answer={
                "trained":bool((learned_logits[ix,side]>=0).item()),
                "initial":bool((init_logits[ix,side]>=0).item()),
                "zero":bool((zero_logits[ix,side]>=0).item()),
                "oracle":bool(old.exact_reach(full,*qs[side],4))}
            work={"join_candidate_evaluations":0}
            answer["coded"]=bool(coded.compressed_reach(chunks,*qs[side],4,
                           join,bias,threshold,work))
            coded_ops+=work["join_candidate_evaluations"]
            for name,val in answer.items():
                if val==bool(truth[side]):
                    summary[name]+=1
                    groups[str(fam)][name]+=1
            row["answer"][str(side)]=answer
        outcomes.append(row)
    elapsed=time.perf_counter()-state_start
    accuracy={k:v/(len(rows)*2) for k,v in summary.items()}
    byfam={f:{name:x/(24*4*2) for name,x in d.items()} for f,d in groups.items()}
    if accuracy["oracle"]!=1:
        verdict="NCI11R2_ORIGINAL_ORACLE_INVALID"
    elif (accuracy["trained"]>=.70
          and accuracy["trained"]-accuracy["initial"]>=.10
          and accuracy["trained"]-accuracy["zero"]>=.10
          and all(byfam[str(f)]["trained"]>=.60 for f in FAMILIES)):
        verdict="NCI11R2_PROSPECTIVE_NATIVE_LATENT_TRANSFER"
    else:
        verdict="NCI11R2_PROSPECTIVE_NO_ROBUST_LATENT_TRANSFER"
    return {"records":outcomes,"question_count":len(rows)*2,
      "accuracy":accuracy,"family_accuracy":byfam,"native_checkpoint_restores":restore_count,
      "coded_join_candidate_evaluations":coded_ops,
      "programmed_four_step_matvec_multiplications_lower_bound":len(rows)*2*4*12*12,
      "evaluation_wall_ms":int(elapsed*1000),"verdict":verdict}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=("development","sealed"),default="development")
    ap.add_argument("--expected-weight-sha",default="")
    args=ap.parse_args()
    start=time.perf_counter()
    model,witness=train_frozen()
    result={"schema":"yggdrasil.nci11r2.prospective-gated-state.v1",
      "phase":args.phase,"frozen_parent":"ae6b5b851ac126ab6fe72142381a904c2e84dcc4",
      "original_dev_run":38623894009,"selected_architecture":"recurrent_write_gate",
      "sealed_seed_bounds":[36544,36568],"sealed_novel_families":list(FAMILIES),
      "new_structures":["bidirectional_decoy_cycles","mixed_incoming_fanout",
        "double_fanout","four_distinct_incoming_decoys"],
      "native_state_bytes":576,"learned_memory_state":True,
      "model_parameters_separate_from_state":True,
      "fixed_outer_product_and_matrix_composition":True,
      "no_future_queries_to_memory":True,
      "sealed_first_use_consumed":args.phase=="sealed",
      "external_llm_calls":0,"accepted_ref_mutation":False,
      "nci01_full_acceptance":False,
      **witness}
    if abs(witness["development_validation_accuracy"]-.7552083134651184)>1e-6:
        raise RuntimeError("FROZEN_DEVELOPMENT_VALIDATION_DRIFT")
    if witness["development_validation_accuracy"]-witness["development_zero_memory"]<.10:
        raise RuntimeError("FROZEN_DEVELOPMENT_MEMORY_ABLATION_FAILED")
    if args.phase=="sealed":
        if not args.expected_weight_sha or args.expected_weight_sha!=witness["frozen_weight_sha256"]:
            raise RuntimeError("MODEL_IDENTITY_NOT_VERIFIED_BEFORE_SEALED_USE")
        result.update(evaluate(model))
    else:
        result["verdict"]="MODEL_IDENTITY_FROZEN_DEV_ONLY"
    result["total_wall_ms"]=int((time.perf_counter()-start)*1000)
    print(json.dumps(result,sort_keys=True,indent=2))
if __name__=="__main__":main()

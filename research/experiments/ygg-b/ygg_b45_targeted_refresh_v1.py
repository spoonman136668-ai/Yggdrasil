#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b27_read_update_read_v1 as b27
import ygg_b29_read1_interference_attribution_v1 as b29

PREREG="91049d95dc2581eb85c0d9a1666b11590a375094"
PARENT_RUN="36277246562"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90
EXPECTED={
111:{0:0.5167464017868042,1:0.4915824830532074,2:0.6297577619552612,3:0.7216312289237976,4:0.8615916967391968},
222:{0:0.47231268882751465,1:0.5025728940963745,2:0.6638513803482056,3:0.7062937021255493,4:0.8322368264198303},
333:{0:0.4682675898075104,1:0.4843205511569977,2:0.6612111330032349,3:0.7182130813598633,4:0.8595041036605835},
444:{0:0.46065574884414673,1:0.5055467486381531,2:0.6666666865348816,3:0.7233676910400391,4:0.8453608155250549},
555:{0:0.47971782088279724,1:0.4602888226509094,2:0.6480541229248047,3:0.7097843885421753,4:0.8604651093482971},
}
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def logits_after_refresh(model,x,qevent,control=False):
    n=x.shape[0]
    M=torch.zeros((n,b27.VALUE_DIM,b27.ADDRESS_DIM),dtype=torch.float32)
    pending=torch.zeros((n,b27.ADDRESS_DIM),dtype=torch.float32)
    for tick in range(28):
        token=x[:,tick]; mod=tick%4
        if mod==0: pending=model.key_emb(token)
        elif mod==1: pending=model.bind_role(pending,token-b27.ROLE_BASE)
        elif mod==2: pending=model.bind_slot(pending,token-b27.SLOT_BASE)
        else:
            M=model._write(M,pending,token-b27.VALUE_BASE)
            pending=torch.zeros_like(pending)
    rows=torch.arange(n,dtype=torch.long)
    pos=((qevent+1)%7) if control else qevent
    k=x[rows,4*pos]
    r=x[rows,4*pos+1]-b27.ROLE_BASE
    s=x[rows,4*pos+2]-b27.SLOT_BASE
    v=x[rows,4*pos+3]-b27.VALUE_BASE
    q=model.key_emb(k); q=model.bind_role(q,r); q=model.bind_slot(q,s)
    M=model._write(M,q,v)
    pending=model.key_emb(x[:,28]-b27.QUERY_KEY_BASE)
    pending=model.bind_role(pending,x[:,29]-b27.QUERY_ROLE_BASE)
    qread=model.bind_slot(pending,x[:,30]-b27.QUERY_SLOT_BASE)
    read=torch.bmm(M,qread.unsqueeze(2)).squeeze(2)
    return model.readout(read),pos

def one():
    rows=[]
    for seed in SEEDS:
        x,y,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True)
        with torch.no_grad():
            original=b29.immediate_read1_logits(model,x)
            target,tpos=logits_after_refresh(model,x,qev,False)
            control,cpos=logits_after_refresh(model,x,qev,True)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("empty q stratum")
            oa=float((original[mask].argmax(1)==y[mask]).float().mean())
            ta=float((target[mask].argmax(1)==y[mask]).float().mean())
            ca=float((control[mask].argmax(1)==y[mask]).float().mean())
            strata.append({"query_position":q,"count":count,"original":oa,"target_refresh":ta,"control_refresh":ca,
                           "target_capable":ta>=TH,"control_capable":ca>=TH})
        rows.append({"seed":seed,"strata":strata,
                     "target_positions_exact":bool(torch.all(tpos==qev)),
                     "control_positions_exact":bool(torch.all(cpos!=qev))})
    flat=[s for r in rows for s in r["strata"]]
    t_all=all(s["target_capable"] for s in flat)
    c_all=all(s["control_capable"] for s in flat)
    rescued=sum((s["original"]<TH) and s["target_capable"] for s in flat)
    if t_all and not c_all: cat="TARGET_SPECIFIC_UNIVERSAL_REFRESH"
    elif t_all and c_all: cat="GENERAL_EXTRA_WRITE_RESCUE"
    elif rescued>0: cat="PARTIAL_TARGET_REFRESH"
    elif rescued==0: cat="NO_TARGET_REFRESH_RESCUE"
    else: cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"target_capable_count":sum(s["target_capable"] for s in flat),
            "control_capable_count":sum(s["control_capable"] for s in flat),
            "original_subthreshold_count":sum(s["original"]<TH for s in flat),
            "target_rescued_count":rescued,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
      "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
      "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
      "all_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
      "original_endpoints_reproduced":all(abs(s["original"]-EXPECTED[r["seed"]][s["query_position"]])<1e-12 for r in a["rows"] for s in r["strata"]),
      "all_original_strata_subthreshold":all(s["original"]<TH for r in a["rows"] for s in r["strata"]),
      "target_refresh_identity_exact":all(r["target_positions_exact"] for r in a["rows"]),
      "control_refresh_nonquery_exact":all(r["control_positions_exact"] for r in a["rows"]),
      "one_added_write_per_refresh_arm":True,
      "threshold_exact":TH==.90,
      "state_exact":b27.PERSISTENT_SCALARS==32,
      "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
      "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]; allowed={"TARGET_SPECIFIC_UNIVERSAL_REFRESH","GENERAL_EXTRA_WRITE_RESCUE","PARTIAL_TARGET_REFRESH","NO_TARGET_REFRESH_RESCUE","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B45","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B45_TARGETED_REFRESH":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()

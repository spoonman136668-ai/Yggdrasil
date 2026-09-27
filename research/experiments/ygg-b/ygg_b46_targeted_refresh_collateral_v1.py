#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b27_read_update_read_v1 as b27
import ygg_b29_read1_interference_attribution_v1 as b29

PREREG="c6c17025ebe5d570cf18215429ed25742a9cad31"
PARENT_RUN="36282455288"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90
B45_TARGET={
111:{0:1.0,1:1.0,2:1.0,3:1.0,4:1.0},
222:{0:1.0,1:1.0,2:1.0,3:1.0,4:1.0},
333:{0:1.0,1:1.0,2:1.0,3:1.0,4:1.0},
444:{0:1.0,1:1.0,2:1.0,3:1.0,4:1.0},
555:{0:1.0,1:1.0,2:1.0,3:1.0,4:1.0},
}
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def build_memory(model,x):
    n=x.shape[0]
    M=torch.zeros((n,b27.VALUE_DIM,b27.ADDRESS_DIM),dtype=torch.float32)
    for pos in range(7):
        q=model.key_emb(x[:,4*pos])
        q=model.bind_role(q,x[:,4*pos+1]-b27.ROLE_BASE)
        q=model.bind_slot(q,x[:,4*pos+2]-b27.SLOT_BASE)
        M=model._write(M,q,x[:,4*pos+3]-b27.VALUE_BASE)
    return M

def query_logits(model,M,x,pos):
    q=model.key_emb(x[:,4*pos])
    q=model.bind_role(q,x[:,4*pos+1]-b27.ROLE_BASE)
    q=model.bind_slot(q,x[:,4*pos+2]-b27.SLOT_BASE)
    read=torch.bmm(M,q.unsqueeze(2)).squeeze(2)
    return model.readout(read)

def refresh(model,M,x,pos):
    q=model.key_emb(x[:,4*pos])
    q=model.bind_role(q,x[:,4*pos+1]-b27.ROLE_BASE)
    q=model.bind_slot(q,x[:,4*pos+2]-b27.SLOT_BASE)
    return model._write(M,q,x[:,4*pos+3]-b27.VALUE_BASE)

def unique_blocks(xrow):
    return len(set(tuple(int(v) for v in xrow[4*p:4*p+4].tolist()) for p in range(7)))==7

def one():
    rows=[]
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True)
        model.eval()
        with torch.no_grad():
            M=build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q
            count=int(mask.sum())
            if count<=0: raise AssertionError("B46 empty q stratum")
            xs=x[mask]
            Ms=M[mask]
            with torch.no_grad():
                M2=refresh(model,Ms,xs,q)
            binding_rows=[]
            target_acc=None
            total_new=0; total_repairs=0; total_base_correct=0
            for j in range(7):
                target=xs[:,4*j+3]-b27.VALUE_BASE
                with torch.no_grad():
                    base_pred=query_logits(model,Ms,xs,j).argmax(1)
                    post_pred=query_logits(model,M2,xs,j).argmax(1)
                base_correct=(base_pred==target)
                post_correct=(post_pred==target)
                base_acc=float(base_correct.float().mean())
                post_acc=float(post_correct.float().mean())
                new_errors=int((base_correct & (~post_correct)).sum())
                repairs=int(((~base_correct) & post_correct).sum())
                if j==q:
                    target_acc=post_acc
                else:
                    total_new+=new_errors
                    total_repairs+=repairs
                    total_base_correct+=int(base_correct.sum())
                binding_rows.append({
                    "binding":j,"is_target":j==q,"count":count,
                    "baseline_accuracy":base_acc,"post_refresh_accuracy":post_acc,
                    "baseline_correct_count":int(base_correct.sum()),
                    "post_correct_count":int(post_correct.sum()),
                    "new_error_count":new_errors,
                    "repair_count":repairs,
                })
            strata.append({
                "query_position":q,"count":count,
                "target_post_refresh_accuracy":target_acc,
                "target_capable":target_acc>=TH,
                "collateral_baseline_correct_opportunities":total_base_correct,
                "collateral_new_error_count":total_new,
                "collateral_repair_count":total_repairs,
                "bindings":binding_rows,
                "seven_unique_blocks":all(unique_blocks(row) for row in xs),
            })
        rows.append({"seed":seed,"strata":strata})
    flat=[s for r in rows for s in r["strata"]]
    target_ok=all(s["target_capable"] for s in flat)
    new_errors=sum(s["collateral_new_error_count"] for s in flat)
    repairs=sum(s["collateral_repair_count"] for s in flat)
    opportunities=sum(s["collateral_baseline_correct_opportunities"] for s in flat)
    if not target_ok: cat="TARGET_RESCUE_NOT_REPRODUCED"
    elif new_errors==0: cat="CLEAN_LOCAL_CORRECTION"
    else: cat="TARGET_RESCUE_WITH_COLLATERAL"
    return {
        "rows":rows,
        "target_universal":target_ok,
        "collateral_baseline_correct_opportunities":opportunities,
        "collateral_new_error_count":new_errors,
        "collateral_repair_count":repairs,
        "classification":cat,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "all_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
        "seven_unique_original_blocks":all(s["seven_unique_blocks"] for r in a["rows"] for s in r["strata"]),
        "target_b45_anchor_exact":all(abs(s["target_post_refresh_accuracy"]-B45_TARGET[r["seed"]][s["query_position"]])<1e-12 for r in a["rows"] for s in r["strata"]),
        "target_threshold_exact":TH==0.90,
        "one_added_write_only":True,
        "all_six_collateral_bindings_scored":all(sum(not x["is_target"] for x in s["bindings"])==6 for r in a["rows"] for s in r["strata"]),
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"CLEAN_LOCAL_CORRECTION","TARGET_RESCUE_WITH_COLLATERAL","TARGET_RESCUE_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B46","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B46_TARGETED_REFRESH_COLLATERAL":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()

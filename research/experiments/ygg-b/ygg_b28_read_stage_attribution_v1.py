#!/usr/bin/env python3
import hashlib,json,statistics,sys
from pathlib import Path

import torch
from torch import nn

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b27_read_update_read_v1 as b27

PREREG="843745c0d4a4dfb142f44edcbc90195c63c8a4db"
PARENT_CLOSURE="ac13545b7d5844b01cd5506bbd9eb0088c71b1ca"
THRESHOLD=0.90

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def metrics(model,x,y1,y2,reset=False):
    model.eval()
    with torch.no_grad():
        l1,l2=model(x,reset_each=reset)
        p1=l1.argmax(dim=1)
        p2=l2.argmax(dim=1)
    a1=float((p1==y1).float().mean().item())
    a2=float((p2==y2).float().mean().item())
    joint=float(((p1==y1)&(p2==y2)).float().mean().item())
    return a1,a2,joint

def train_seed(seed):
    torch.manual_seed(seed)
    model=b27.ReadUpdateRead()
    opt=torch.optim.Adam(model.parameters(),lr=b27.LR)
    loss_fn=nn.CrossEntropyLoss()

    xtr,y1tr,y2tr,*_=b27.training_data(seed,b27.TRAIN_N)
    xev,y1ev,y2ev,q1eev,q2eev,q1kev,q1rev,q1sev,q2kev,q2rev,q2sev,_,_=b27.evaluation_data(seed,b27.EVAL_N)

    train_full=b27.training_data(seed,b27.TRAIN_N)
    q2ktr,q2rtr,q2str=train_full[8],train_full[9],train_full[10]
    train_holdout=b27.heldout_targets_in_training(q2ktr,q2rtr,q2str,y2tr)
    eval_count=b27.heldout_count(q2kev,q2rev,q2sev,y2ev)

    gen=torch.Generator(device="cpu")
    gen.manual_seed(seed*100000+93)
    for _ in range(b27.EPOCHS):
        model.train()
        order=torch.randperm(b27.TRAIN_N,generator=gen)
        for i in range(0,b27.TRAIN_N,b27.BATCH):
            idx=order[i:i+b27.BATCH]
            opt.zero_grad(set_to_none=True)
            l1,l2=model(xtr[idx])
            loss=loss_fn(l1,y1tr[idx])+loss_fn(l2,y2tr[idx])
            loss.backward()
            opt.step()

    read1,read2,joint=metrics(model,xev,y1ev,y2ev,False)
    r_read1,r_read2,r_joint=metrics(model,xev,y1ev,y2ev,True)
    qswap=b27.joint_accuracy(model,b27.swapped_queries(xev),y1ev,y2ev,False)
    vshuffle=b27.joint_accuracy(model,b27.shuffled_write_values(xev,seed),y1ev,y2ev,False)
    rflip=b27.joint_accuracy(model,b27.flipped_query_roles(xev),y1ev,y2ev,False)
    sflip=b27.joint_accuracy(model,b27.flipped_query_slots(xev),y1ev,y2ev,False)

    return {
        "seed":seed,
        "read1_accuracy":read1,
        "read2_accuracy":read2,
        "joint_accuracy":joint,
        "reset_read1_accuracy":r_read1,
        "reset_read2_accuracy":r_read2,
        "reset_joint_accuracy":r_joint,
        "query_identity_swap_joint_accuracy":qswap,
        "write_value_shuffle_joint_accuracy":vshuffle,
        "query_role_flip_joint_accuracy":rflip,
        "query_slot_flip_joint_accuracy":sflip,
        "causal_direction":bool(joint>r_joint and joint>qswap and joint>vshuffle and joint>rflip and joint>sflip),
        "parameter_count":sum(p.numel() for p in model.parameters()),
        "persistent_state_scalars":b27.PERSISTENT_SCALARS,
        "train_read2_heldout_targets":train_holdout,
        "eval_distinct_read2_heldout_quadruples":eval_count,
        "read_addresses_distinct":bool(torch.all(q1eev!=q2eev)),
    }

def classify(rows):
    min1=min(r["read1_accuracy"] for r in rows)
    min2=min(r["read2_accuracy"] for r in rows)
    minj=min(r["joint_accuracy"] for r in rows)
    p1=min1>=THRESHOLD
    p2=min2>=THRESHOLD
    pj=minj>=THRESHOLD
    if pj:
        return "NO_REPRODUCED_LIMIT"
    if not p1 and p2:
        return "READ1_LIMITED"
    if p1 and not p2:
        return "READ2_LIMITED"
    if not p1 and not p2:
        return "BOTH_INDIVIDUAL_LIMITED"
    return "JOINT_COMPOSITION_LIMIT"

def one_pass():
    rows=[train_seed(s) for s in b27.SEEDS]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=b27.mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B28_MECHANICAL_GATE_FAILED")
    first=one_pass()
    second=one_pass()
    b1=canonical(first); b2=canonical(second)
    rows=first["rows"]
    allowed={"READ1_LIMITED","READ2_LIMITED","BOTH_INDIVIDUAL_LIMITED","JOINT_COMPOSITION_LIMIT","NO_REPRODUCED_LIMIT"}
    validity={
        "mechanical_gate":bool(mech["all_pass"]),
        "threshold_inherited_exact":THRESHOLD==0.90,
        "duplicate_complete_execution_byte_identical":b1==b2,
        "all_causal_direction":all(r["causal_direction"] for r in rows),
        "state_exactly_32":all(r["persistent_state_scalars"]==32 for r in rows),
        "parameter_count_exactly_120":all(r["parameter_count"]==120 for r in rows),
        "no_read2_heldout_target_in_training":all(r["train_read2_heldout_targets"]==0 for r in rows),
        "all_64_read2_heldout_quadruples_scored":all(r["eval_distinct_read2_heldout_quadruples"]==64 for r in rows),
        "read_addresses_distinct":all(r["read_addresses_distinct"] for r in rows),
    }
    category=first["classification"]
    out={
        "schema":1,
        "experiment":"YGG-B28",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "inherited_threshold":THRESHOLD,
        "mechanical":mech,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":{
            "YGG_B28_READ_STAGE_ATTRIBUTION":bool(all(validity.values()) and category in allowed),
            "classification":category,
            "min_read1_accuracy":min(r["read1_accuracy"] for r in rows),
            "min_read2_accuracy":min(r["read2_accuracy"] for r in rows),
            "min_joint_accuracy":min(r["joint_accuracy"] for r in rows),
        },
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

import torch
from torch import nn

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b27_read_update_read_v1 as b27
import ygg_b28_read_stage_attribution_v1 as b28

PREREG="ce2b20b3962fc6b006c5c71407dedf6887dfceee"
PARENT_RUN="0faacaae883e1e5ee2dbb040cea335fdf88098e3"
THRESHOLD=0.90

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def accuracy(logits,target):
    return float((logits.argmax(dim=1)==target).float().mean().item())

def immediate_read1_logits(model,x):
    n=x.shape[0]
    M=torch.zeros((n,b27.VALUE_DIM,b27.ADDRESS_DIM),dtype=torch.float32)
    pending=torch.zeros((n,b27.ADDRESS_DIM),dtype=torch.float32)
    for tick in range(31):
        token=x[:,tick]
        if tick<28:
            mod=tick%4
            if mod==0:
                pending=model.key_emb(token)
            elif mod==1:
                pending=model.bind_role(pending,token-b27.ROLE_BASE)
            elif mod==2:
                pending=model.bind_slot(pending,token-b27.SLOT_BASE)
            else:
                M=model._write(M,pending,token-b27.VALUE_BASE)
                pending=torch.zeros_like(pending)
        elif tick==28:
            pending=model.key_emb(token-b27.QUERY_KEY_BASE)
        elif tick==29:
            pending=model.bind_role(pending,token-b27.QUERY_ROLE_BASE)
        elif tick==30:
            q=model.bind_slot(pending,token-b27.QUERY_SLOT_BASE)
            read=torch.bmm(M,q.unsqueeze(2)).squeeze(2)
            return model.readout(read)
    raise AssertionError("B29 immediate READ1 not produced")

def train_model(seed,read1_only):
    torch.manual_seed(seed)
    model=b27.ReadUpdateRead()
    opt=torch.optim.Adam(model.parameters(),lr=b27.LR)
    loss_fn=nn.CrossEntropyLoss()
    xtr,y1tr,y2tr,*_=b27.training_data(seed,b27.TRAIN_N)
    gen=torch.Generator(device="cpu")
    gen.manual_seed(seed*100000+93)
    for _ in range(b27.EPOCHS):
        model.train()
        order=torch.randperm(b27.TRAIN_N,generator=gen)
        for i in range(0,b27.TRAIN_N,b27.BATCH):
            idx=order[i:i+b27.BATCH]
            opt.zero_grad(set_to_none=True)
            l1,l2=model(xtr[idx])
            loss=loss_fn(l1,y1tr[idx])
            if not read1_only:
                loss=loss+loss_fn(l2,y2tr[idx])
            loss.backward()
            opt.step()
    return model

def seed_result(seed):
    xev,y1ev,y2ev,q1eev,q2eev,q1kev,q1rev,q1sev,q2kev,q2rev,q2sev,_,_=b27.evaluation_data(seed,b27.EVAL_N)
    train_full=b27.training_data(seed,b27.TRAIN_N)
    q2ktr,q2rtr,q2str=train_full[8],train_full[9],train_full[10]
    train_holdout=b27.heldout_targets_in_training(q2ktr,q2rtr,q2str,train_full[2])
    eval_count=b27.heldout_count(q2kev,q2rev,q2sev,y2ev)

    model_a=train_model(seed,False)
    model_a.eval()
    with torch.no_grad():
        a_l1,a_l2=model_a(xev)
        b_l1=immediate_read1_logits(model_a,xev)
    a_read1=accuracy(a_l1,y1ev)
    b_read1=accuracy(b_l1,y1ev)
    a_read2=accuracy(a_l2,y2ev)
    a_joint=float(((a_l1.argmax(dim=1)==y1ev)&(a_l2.argmax(dim=1)==y2ev)).float().mean().item())

    r1,r2,rj=b28.metrics(model_a,xev,y1ev,y2ev,True)
    qswap=b27.joint_accuracy(model_a,b27.swapped_queries(xev),y1ev,y2ev,False)
    vshuffle=b27.joint_accuracy(model_a,b27.shuffled_write_values(xev,seed),y1ev,y2ev,False)
    rflip=b27.joint_accuracy(model_a,b27.flipped_query_roles(xev),y1ev,y2ev,False)
    sflip=b27.joint_accuracy(model_a,b27.flipped_query_slots(xev),y1ev,y2ev,False)

    model_c=train_model(seed,True)
    model_c.eval()
    with torch.no_grad():
        c_l1=immediate_read1_logits(model_c,xev)
    c_read1=accuracy(c_l1,y1ev)

    return {
        "seed":seed,
        "arm_a_read1_accuracy":a_read1,
        "arm_a_read2_accuracy":a_read2,
        "arm_a_joint_accuracy":a_joint,
        "arm_b_immediate_read1_accuracy":b_read1,
        "arm_c_read1_only_accuracy":c_read1,
        "arm_a_b_logits_byte_identical":canonical(a_l1.tolist())==canonical(b_l1.tolist()),
        "reset_read1_accuracy":r1,
        "reset_read2_accuracy":r2,
        "reset_joint_accuracy":rj,
        "query_identity_swap_joint_accuracy":qswap,
        "write_value_shuffle_joint_accuracy":vshuffle,
        "query_role_flip_joint_accuracy":rflip,
        "query_slot_flip_joint_accuracy":sflip,
        "causal_direction":bool(a_joint>rj and a_joint>qswap and a_joint>vshuffle and a_joint>rflip and a_joint>sflip),
        "parameter_count_a":sum(p.numel() for p in model_a.parameters()),
        "parameter_count_c":sum(p.numel() for p in model_c.parameters()),
        "persistent_state_scalars":b27.PERSISTENT_SCALARS,
        "train_read2_heldout_targets":train_holdout,
        "eval_distinct_read2_heldout_quadruples":eval_count,
        "read_addresses_distinct":bool(torch.all(q1eev!=q2eev)),
    }

def classify(rows):
    a=min(r["arm_a_read1_accuracy"] for r in rows)
    b=min(r["arm_b_immediate_read1_accuracy"] for r in rows)
    c=min(r["arm_c_read1_only_accuracy"] for r in rows)
    if a>=THRESHOLD:
        return "NO_REPRODUCED_LIMIT"
    if b>=THRESHOLD:
        return "OVERWRITE_INTERFERENCE"
    if c>=THRESHOLD:
        return "MULTIOUTPUT_OPTIMIZATION_INTERFERENCE"
    if c<THRESHOLD:
        return "INTRINSIC_READ1_LIMIT"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[seed_result(s) for s in b27.SEEDS]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=b27.mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B29_MECHANICAL_GATE_FAILED")
    first=one_pass()
    second=one_pass()
    b1=canonical(first); b2=canonical(second)
    rows=first["rows"]
    allowed={
        "OVERWRITE_INTERFERENCE","MULTIOUTPUT_OPTIMIZATION_INTERFERENCE",
        "INTRINSIC_READ1_LIMIT","NO_REPRODUCED_LIMIT","OTHER_VALID_PATTERN",
    }
    validity={
        "mechanical_gate":bool(mech["all_pass"]),
        "threshold_inherited_exact":THRESHOLD==0.90,
        "duplicate_complete_execution_byte_identical":b1==b2,
        "arm_a_b_immediate_read_equivalent":all(r["arm_a_b_logits_byte_identical"] for r in rows),
        "all_causal_direction":all(r["causal_direction"] for r in rows),
        "state_exactly_32":all(r["persistent_state_scalars"]==32 for r in rows),
        "parameter_count_exactly_120":all(r["parameter_count_a"]==120 and r["parameter_count_c"]==120 for r in rows),
        "no_read2_heldout_target_in_training":all(r["train_read2_heldout_targets"]==0 for r in rows),
        "all_64_read2_heldout_quadruples_scored":all(r["eval_distinct_read2_heldout_quadruples"]==64 for r in rows),
        "read_addresses_distinct":all(r["read_addresses_distinct"] for r in rows),
    }
    category=first["classification"]
    out={
        "schema":1,
        "experiment":"YGG-B29",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "inherited_threshold":THRESHOLD,
        "mechanical":mech,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":{
            "YGG_B29_READ1_INTERFERENCE_ATTRIBUTION":bool(all(validity.values()) and category in allowed),
            "classification":category,
            "min_arm_a_read1":min(r["arm_a_read1_accuracy"] for r in rows),
            "min_arm_b_immediate_read1":min(r["arm_b_immediate_read1_accuracy"] for r in rows),
            "min_arm_c_read1_only":min(r["arm_c_read1_only_accuracy"] for r in rows),
        },
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

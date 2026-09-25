#!/usr/bin/env python3
import hashlib,json,statistics,sys
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b26_three_entity_seven_binding_temporal_v1 as b26

PREREG="968ddbc85106e0589f0d412ebd5cba2849ce7bd1"
PARENT_CLOSURE="f1b9726614af1c57841310c25f5d1daa57c5e2fa"

KEYS=b26.KEYS
ROLES=b26.ROLES
SLOTS=b26.SLOTS
VALUES=b26.VALUES
ACTIVE_BINDINGS=7
WRITES=8
SEQ=38
ADDRESS_DIM=b26.ADDRESS_DIM
VALUE_DIM=b26.VALUE_DIM
PERSISTENT_SCALARS=b26.PERSISTENT_SCALARS
PARAMETERS=b26.PARAMETERS
TRAIN_N=b26.TRAIN_N
EVAL_N=b26.EVAL_N
BATCH=b26.BATCH
EPOCHS=b26.EPOCHS
LR=b26.LR
SEEDS=b26.SEEDS

ROLE_BASE=b26.ROLE_BASE
SLOT_BASE=b26.SLOT_BASE
VALUE_BASE=b26.VALUE_BASE
QUERY_KEY_BASE=b26.QUERY_KEY_BASE
QUERY_ROLE_BASE=b26.QUERY_ROLE_BASE
QUERY_SLOT_BASE=b26.QUERY_SLOT_BASE

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def choose_events(gen,n):
    q1=torch.randint(0,ACTIVE_BINDINGS,(n,),generator=gen,dtype=torch.long)
    raw=torch.randint(0,ACTIVE_BINDINGS-1,(n,),generator=gen,dtype=torch.long)
    q2=raw+(raw>=q1).long()
    if torch.any(q1==q2):
        raise AssertionError("query events must differ")
    return q1,q2

def make_data(seed,n,evaluation):
    gen=torch.Generator(device="cpu")
    gen.manual_seed(seed*100000+(92 if evaluation else 91))
    keys10,roles10,slots10,entity_keys,heavy,update_source_unused,query_entity_unused=b26.structural_events(gen,n)
    keys=keys10[:,:ACTIVE_BINDINGS].clone()
    roles=roles10[:,:ACTIVE_BINDINGS].clone()
    slots=slots10[:,:ACTIVE_BINDINGS].clone()

    choice=torch.randint(0,b26.ALLOWED.shape[3],(n,ACTIVE_BINDINGS),generator=gen,dtype=torch.long)
    vals=b26.ALLOWED[keys,roles,slots,choice].clone()

    q1_event,q2_event=choose_events(gen,n)
    rows=torch.arange(n,dtype=torch.long)

    q1k=keys[rows,q1_event]
    q1r=roles[rows,q1_event]
    q1s=slots[rows,q1_event]
    y1=vals[rows,q1_event]

    q2k=keys[rows,q2_event]
    q2r=roles[rows,q2_event]
    q2s=slots[rows,q2_event]
    old2=vals[rows,q2_event]

    new2=torch.empty((n,),dtype=torch.long)
    for row in range(n):
        k=int(q2k[row]); r=int(q2r[row]); s=int(q2s[row]); old=int(old2[row])
        if evaluation:
            cand=b26.HELDOUT[k,r,s]
            pick=int(torch.randint(0,cand.shape[0],(1,),generator=gen).item())
            v=int(cand[pick].item())
            if v==old:
                raise AssertionError("heldout overwrite equals allowed original")
        else:
            v=b26.choose_distinct_allowed(k,r,s,old,gen)
        new2[row]=v

    x=torch.empty((n,SEQ),dtype=torch.long)
    for i in range(ACTIVE_BINDINGS):
        x[:,4*i]=keys[:,i]
        x[:,4*i+1]=ROLE_BASE+roles[:,i]
        x[:,4*i+2]=SLOT_BASE+slots[:,i]
        x[:,4*i+3]=VALUE_BASE+vals[:,i]

    x[:,28]=QUERY_KEY_BASE+q1k
    x[:,29]=QUERY_ROLE_BASE+q1r
    x[:,30]=QUERY_SLOT_BASE+q1s

    x[:,31]=q2k
    x[:,32]=ROLE_BASE+q2r
    x[:,33]=SLOT_BASE+q2s
    x[:,34]=VALUE_BASE+new2

    x[:,35]=QUERY_KEY_BASE+q2k
    x[:,36]=QUERY_ROLE_BASE+q2r
    x[:,37]=QUERY_SLOT_BASE+q2s

    return x,y1,new2,q1_event,q2_event,q1k,q1r,q1s,q2k,q2r,q2s,entity_keys,heavy

def training_data(seed,n):
    return make_data(seed,n,False)

def evaluation_data(seed,n):
    return make_data(seed,n,True)

WRITE_VALUE_COLS=torch.tensor([3,7,11,15,19,23,27,34],dtype=torch.long)

def swapped_queries(x):
    out=x.clone()
    a=out[:,28:31].clone()
    b=out[:,35:38].clone()
    out[:,28:31]=b
    out[:,35:38]=a
    return out

def shuffled_write_values(x,seed):
    gen=torch.Generator(device="cpu")
    gen.manual_seed(9910000+seed)
    out=x.clone()
    vals=x[:,WRITE_VALUE_COLS]
    order=torch.argsort(torch.rand((x.shape[0],WRITE_VALUE_COLS.numel()),generator=gen),dim=1)
    out[:,WRITE_VALUE_COLS]=torch.gather(vals,1,order)
    return out

def flipped_query_roles(x):
    out=x.clone()
    for col in (29,36):
        role=x[:,col]-QUERY_ROLE_BASE
        out[:,col]=QUERY_ROLE_BASE+(1-role)
    return out

def flipped_query_slots(x):
    out=x.clone()
    for col in (30,37):
        slot=x[:,col]-QUERY_SLOT_BASE
        out[:,col]=QUERY_SLOT_BASE+(1-slot)
    return out

class ReadUpdateRead(nn.Module):
    def __init__(self):
        super().__init__()
        self.key_emb=nn.Embedding(KEYS,ADDRESS_DIM)
        self.value_emb=nn.Embedding(VALUES,VALUE_DIM)
        self.readout=nn.Linear(VALUE_DIM,VALUES)

    def bind_role(self,v,r):
        return F.normalize(v*b26.ROLE_MASK[r],p=2,dim=1,eps=1e-12)

    def bind_slot(self,v,s):
        return F.normalize(v*b26.SLOT_MASK[s],p=2,dim=1,eps=1e-12)

    def _write(self,M,q,value):
        vv=self.value_emb(value)
        return b26.projection_write(M,q,vv)

    def forward(self,x,reset_each=False):
        n=x.shape[0]
        M=torch.zeros((n,VALUE_DIM,ADDRESS_DIM),dtype=torch.float32)
        pending=torch.zeros((n,ADDRESS_DIM),dtype=torch.float32)
        outputs=[]
        for tick in range(SEQ):
            if reset_each:
                M=torch.zeros_like(M)
                pending=torch.zeros_like(pending)
            token=x[:,tick]

            if tick<28:
                mod=tick%4
                if mod==0:
                    pending=self.key_emb(token)
                elif mod==1:
                    pending=self.bind_role(pending,token-ROLE_BASE)
                elif mod==2:
                    pending=self.bind_slot(pending,token-SLOT_BASE)
                else:
                    M=self._write(M,pending,token-VALUE_BASE)
                    pending=torch.zeros_like(pending)
            elif tick==28:
                pending=self.key_emb(token-QUERY_KEY_BASE)
            elif tick==29:
                pending=self.bind_role(pending,token-QUERY_ROLE_BASE)
            elif tick==30:
                q=self.bind_slot(pending,token-QUERY_SLOT_BASE)
                read=torch.bmm(M,q.unsqueeze(2)).squeeze(2)
                outputs.append(self.readout(read))
                pending=torch.zeros_like(pending)
            elif tick==31:
                pending=self.key_emb(token)
            elif tick==32:
                pending=self.bind_role(pending,token-ROLE_BASE)
            elif tick==33:
                pending=self.bind_slot(pending,token-SLOT_BASE)
            elif tick==34:
                M=self._write(M,pending,token-VALUE_BASE)
                pending=torch.zeros_like(pending)
            elif tick==35:
                pending=self.key_emb(token-QUERY_KEY_BASE)
            elif tick==36:
                pending=self.bind_role(pending,token-QUERY_ROLE_BASE)
            elif tick==37:
                q=self.bind_slot(pending,token-QUERY_SLOT_BASE)
                read=torch.bmm(M,q.unsqueeze(2)).squeeze(2)
                outputs.append(self.readout(read))
        if len(outputs)!=2:
            raise AssertionError("two outputs not produced")
        return outputs[0],outputs[1]

def joint_accuracy(model,x,y1,y2,reset=False):
    model.eval()
    with torch.no_grad():
        l1,l2=model(x,reset_each=reset)
        p1=l1.argmax(dim=1)
        p2=l2.argmax(dim=1)
    return float(((p1==y1)&(p2==y2)).float().mean().item())

def heldout_count(qk,qr,qs,y):
    return len(set((int(k),int(r),int(s),int(v)) for k,r,s,v in zip(qk.tolist(),qr.tolist(),qs.tolist(),y.tolist())))

def heldout_targets_in_training(qk,qr,qs,y):
    return int((((qk+2*qr+3*qs+y)%4)==0).sum().item())

def train_seed(seed):
    torch.manual_seed(seed)
    model=ReadUpdateRead()
    opt=torch.optim.Adam(model.parameters(),lr=LR)
    loss_fn=nn.CrossEntropyLoss()

    xtr,y1tr,y2tr,q1etr,q2etr,q1ktr,q1rtr,q1str,q2ktr,q2rtr,q2str,ektr,hetr=training_data(seed,TRAIN_N)
    xev,y1ev,y2ev,q1eev,q2eev,q1kev,q1rev,q1sev,q2kev,q2rev,q2sev,ekev,heev=evaluation_data(seed,EVAL_N)

    train_holdout=heldout_targets_in_training(q2ktr,q2rtr,q2str,y2tr)
    eval_count=heldout_count(q2kev,q2rev,q2sev,y2ev)
    if train_holdout!=0:
        raise AssertionError("heldout READ-2 target leaked into training")
    if torch.any(((q2kev+2*q2rev+3*q2sev+y2ev)%4)!=0):
        raise AssertionError("evaluation READ-2 target not heldout")
    if torch.any(q1eev==q2eev):
        raise AssertionError("READ addresses not distinct")

    gen=torch.Generator(device="cpu")
    gen.manual_seed(seed*100000+93)
    for _ in range(EPOCHS):
        model.train()
        order=torch.randperm(TRAIN_N,generator=gen)
        for i in range(0,TRAIN_N,BATCH):
            idx=order[i:i+BATCH]
            opt.zero_grad(set_to_none=True)
            l1,l2=model(xtr[idx])
            loss=loss_fn(l1,y1tr[idx])+loss_fn(l2,y2tr[idx])
            loss.backward()
            opt.step()

    persistent=joint_accuracy(model,xev,y1ev,y2ev,False)
    reset=joint_accuracy(model,xev,y1ev,y2ev,True)
    qswap=joint_accuracy(model,swapped_queries(xev),y1ev,y2ev,False)
    vshuffle=joint_accuracy(model,shuffled_write_values(xev,seed),y1ev,y2ev,False)
    rflip=joint_accuracy(model,flipped_query_roles(xev),y1ev,y2ev,False)
    sflip=joint_accuracy(model,flipped_query_slots(xev),y1ev,y2ev,False)

    return {
        "seed":seed,
        "persistent_joint_accuracy":persistent,
        "reset_joint_accuracy":reset,
        "query_identity_swap_accuracy":qswap,
        "write_value_shuffle_accuracy":vshuffle,
        "query_role_flip_accuracy":rflip,
        "query_slot_flip_accuracy":sflip,
        "persistent_reset_gap":persistent-reset,
        "query_identity_swap_degradation":persistent-qswap,
        "write_value_shuffle_degradation":persistent-vshuffle,
        "query_role_flip_degradation":persistent-rflip,
        "query_slot_flip_degradation":persistent-sflip,
        "causal_direction":bool(
            persistent>reset and persistent>qswap and persistent>vshuffle
            and persistent>rflip and persistent>sflip
        ),
        "parameter_count":sum(p.numel() for p in model.parameters()),
        "persistent_state_scalars":PERSISTENT_SCALARS,
        "train_read2_heldout_targets":train_holdout,
        "eval_distinct_read2_heldout_quadruples":eval_count,
    }

def mechanical():
    torch.manual_seed(992)
    model=ReadUpdateRead()
    x,y1,y2,q1e,q2e,q1k,q1r,q1s,q2k,q2r,q2s,entity_keys,heavy=make_data(992,4096,True)
    checks={
        "seven_active_bindings_exact":ACTIVE_BINDINGS==7,
        "one_intervening_overwrite_exact":WRITES==8,
        "two_distinct_query_addresses":bool(torch.all(q1e!=q2e)),
        "sequence_length_exactly_38":SEQ==38,
        "value_dimension_exactly_3":VALUE_DIM==3,
        "memory_shape_3x8":VALUE_DIM==3 and ADDRESS_DIM==8,
        "persistent_state_exactly_32":PERSISTENT_SCALARS==32,
        "parameter_count_exactly_120":sum(p.numel() for p in model.parameters())==PARAMETERS,
        "all_three_entity_positions_exercised":set(heavy.tolist())=={0,1,2},
        "read2_targets_heldout":bool(torch.all(((q2k+2*q2r+3*q2s+y2)%4)==0)),
    }
    return {"all_pass":all(checks.values()),"checks":checks,"parameter_count":sum(p.numel() for p in model.parameters())}

def one_pass():
    rows=[train_seed(s) for s in SEEDS]
    p=[r["persistent_joint_accuracy"] for r in rows]
    reset=[r["reset_joint_accuracy"] for r in rows]
    gap=[r["persistent_reset_gap"] for r in rows]
    qd=[r["query_identity_swap_degradation"] for r in rows]
    vd=[r["write_value_shuffle_degradation"] for r in rows]
    rd=[r["query_role_flip_degradation"] for r in rows]
    sd=[r["query_slot_flip_degradation"] for r in rows]
    q={
        "min_persistent_joint_ge_090":min(p)>=0.90,
        "median_persistent_joint_ge_095":statistics.median(p)>=0.95,
        "max_reset_joint_le_020":max(reset)<=0.20,
        "min_gap_ge_060":min(gap)>=0.60,
        "min_query_identity_swap_drop_ge_040":min(qd)>=0.40,
        "min_write_value_shuffle_drop_ge_040":min(vd)>=0.40,
        "min_query_role_flip_drop_ge_040":min(rd)>=0.40,
        "min_query_slot_flip_drop_ge_040":min(sd)>=0.40,
        "all_causal_direction":all(r["causal_direction"] for r in rows),
        "state_exactly_32":all(r["persistent_state_scalars"]==32 for r in rows),
        "parameter_count_exactly_120":all(r["parameter_count"]==120 for r in rows),
        "no_read2_heldout_target_in_training":all(r["train_read2_heldout_targets"]==0 for r in rows),
        "all_64_read2_heldout_quadruples_scored":all(r["eval_distinct_read2_heldout_quadruples"]==64 for r in rows),
    }
    q["YGG_B27_READ_UPDATE_READ_SEQUENCE_EPISODE"]=all(q.values())
    return {"rows":rows,"qualification":q}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B27_MECHANICAL_GATE_FAILED")
    p1=one_pass()
    p2=one_pass()
    b1=canonical(p1)
    b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B27",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "mechanical":mech,
        "duplicate_byte_identical":b1==b2,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":p1,
    }
    if not out["duplicate_byte_identical"]:
        raise SystemExit("duplicate evidence mismatch")
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

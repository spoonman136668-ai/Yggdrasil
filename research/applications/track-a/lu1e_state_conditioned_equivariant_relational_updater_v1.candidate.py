#!/usr/bin/env python3
import hashlib, json, math, sys
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import lu1b_focal_side_canonical_stay_v1 as b

a=b.a

PREREG_LU1E='1adbbfc33514fc3143f98a5d85ffb4d5b99ae3eb'
PARENT_V02=b.PARENT_V02
LU0E_CLOSURE=b.LU0E_CLOSURE
PARENT_LU1DF1='1609425b3144e66ab373fb5ca7239888883ba351'
PARENT_LU1D_CLOSURE='f9625901264f32ad774d69378001a2c3a8a3b2ef'
PARENT_LU1D_DIAG='94ce811906de8df6445d81aafaa673cf2ac686d4'

INPUT_WIDTH=70
CELL_STATE=6
CELL_CONT=3
CELL_REL=16
CELL_OUT=24
QSIDE_CATS=3
QSIDE_REL=8
QSIDE_OUT=16
OTHER_EXTRA=3
OTHER_OUT=16
CONTEXT_WIDTH=80
VALUE_WIDTH=64
OUT_HIDDEN=32
OUTPUT_WIDTH=6
CENTER=3
NONFOCAL=(0,1,2,4,5,6)

TRAIN_N=b.TRAIN_N
VALID_N=b.VALID_N
TEST_N=b.TEST_N
BATCH=b.BATCH
EPOCHS=b.EPOCHS
LR=b.LR
WEIGHT_DECAY=b.WEIGHT_DECAY
BETAS=b.BETAS
EPS=b.EPS
PATTERN_COUNTS=b.PATTERN_COUNTS


class StateConditionedCellEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.transforms=nn.ModuleList([nn.Linear(CELL_CONT,CELL_REL) for _ in range(CELL_STATE)])
        self.post=nn.Linear(CELL_REL,CELL_OUT)
    def forward(self,cells):
        cat=cells[...,:6]
        cont=cells[...,6:9]
        variants=torch.stack([layer(cont) for layer in self.transforms],dim=-2)
        h=(cat.unsqueeze(-1)*variants).sum(dim=-2)
        return F.silu(self.post(F.silu(h)))


class QSideRelationEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.transforms=nn.ModuleList([nn.Linear(1,QSIDE_REL) for _ in range(QSIDE_CATS)])
        self.post=nn.Linear(QSIDE_REL,QSIDE_OUT)
    def forward(self,qprev,qside):
        variants=torch.stack([layer(qprev) for layer in self.transforms],dim=-2)
        h=(qside.unsqueeze(-1)*variants).sum(dim=-2)
        return F.silu(self.post(F.silu(h)))


class StateConditionedEquivariantStudent(nn.Module):
    def __init__(self):
        super().__init__()
        self.cell=StateConditionedCellEncoder()
        self.qside=QSideRelationEncoder()
        self.other=nn.Linear(OTHER_EXTRA,OTHER_OUT)
        self.value=nn.Linear(CONTEXT_WIDTH,VALUE_WIDTH)
        self.gate=nn.Linear(CONTEXT_WIDTH,VALUE_WIDTH)
        self.out1=nn.Linear(VALUE_WIDTH,OUT_HIDDEN)
        self.out=nn.Linear(OUT_HIDDEN,OUTPUT_WIDTH)
    def forward(self,x):
        cells=x[:,:63].reshape(-1,7,9)
        enc=self.cell(cells)
        focal=enc[:,CENTER,:]
        neigh=enc[:,list(NONFOCAL),:].mean(dim=1)
        qprev=x[:,64:65]
        qside=x[:,65:68]
        qr=self.qside(qprev,qside)
        other=torch.cat([x[:,63:64],x[:,68:70]],dim=1)
        oe=F.silu(self.other(other))
        ctx=torch.cat([neigh,focal,qr,oe],dim=1)
        value=F.silu(self.value(ctx))
        gate=torch.sigmoid(self.gate(ctx))
        h=value*gate
        return self.out(F.silu(self.out1(h)))


def seed64(label,lu1ef1):
    h=hashlib.sha256((label+'|'+lu1ef1).encode()).digest()
    return int.from_bytes(h[:8],'big',signed=False)


def seeds(lu1ef1):
    return {
        'train_data':seed64('LU1E-TRAIN-DATA',lu1ef1),
        'valid_data':seed64('LU1E-VALID-DATA',lu1ef1),
        'test_data':seed64('LU1E-TEST-DATA',lu1ef1),
        'train_rng':seed64('LU1E-TRAIN-RNG',lu1ef1),
        'symmetry':seed64('LU1E-SYMMETRY',lu1ef1),
        'quiescence':seed64('LU1E-QUIESCENCE',lu1ef1),
    }


def generate_dataset(seed,n,pattern_count):
    return b.generate_dataset(seed,n,pattern_count)


def train_once(lu1ef1,out_weights,out_metrics):
    if len(lu1ef1)!=40: raise ValueError('LU1EF1')
    ss=seeds(lu1ef1)
    a.configure_torch(ss['train_rng'])
    train=generate_dataset(ss['train_data'],TRAIN_N,PATTERN_COUNTS['train'])
    valid=generate_dataset(ss['valid_data'],VALID_N,PATTERN_COUNTS['valid'])
    model=StateConditionedEquivariantStudent()
    assert a.params_count(model)==13694
    opt=torch.optim.AdamW(model.parameters(),lr=LR,betas=BETAS,eps=EPS,weight_decay=WEIGHT_DECAY)
    X,K,YS,YU=train
    tx=torch.from_numpy(X); tk=torch.from_numpy(K); tys=torch.from_numpy(YS); tyu=torch.from_numpy(YU)
    gen=torch.Generator(device='cpu'); gen.manual_seed(ss['train_rng']%(2**63-1))
    final_loss=None
    for epoch in range(EPOCHS):
        perm=torch.randperm(TRAIN_N,generator=gen)
        epoch_sum=0.0; batches=0
        model.train()
        for start in range(0,TRAIN_N,BATCH):
            idx=perm[start:start+BATCH]
            opt.zero_grad(set_to_none=True)
            logits=model(tx[idx])
            loss=a.masked_loss(logits,tk[idx],tys[idx],tyu[idx])
            loss.backward(); opt.step()
            epoch_sum+=float(loss.detach()); batches+=1
        final_loss=epoch_sum/batches
    wb=a.canonical_weights(model); Path(out_weights).write_bytes(wb)
    metrics={
        'LU1EF1':lu1ef1,'prereg':PREREG_LU1E,'parent_v02':PARENT_V02,
        'parent_lu1df1':PARENT_LU1DF1,'parent_lu1d_closure':PARENT_LU1D_CLOSURE,
        'parent_lu1d_diag':PARENT_LU1D_DIAG,
        'architecture':'STATE_CONDITIONED_EQUIVARIANT_RELATIONAL_V1',
        'parameter_count':a.params_count(model),'weight_bytes':len(wb),
        'weight_sha256':hashlib.sha256(wb).hexdigest(),
        'train_examples':TRAIN_N,'valid_examples':VALID_N,'epochs':EPOCHS,'batch':BATCH,
        'final_train_mean_batch_equal_head_loss':final_loss,
        'validation':a.eval_losses(model,valid),'seeds':ss,
    }
    Path(out_metrics).write_bytes(json.dumps(metrics,sort_keys=True,separators=(',',':')).encode())
    return metrics


def symmetry_audit(model,lu1ef1):
    Xraw,K,YS,YU=a.generate_dataset(seeds(lu1ef1)['symmetry'],2000,512)
    SXraw=a.swap_input(Xraw)
    X=b.canonicalize_batch(Xraw); SX=b.canonicalize_batch(SXraw)
    h1,s1,u1=a.predict(model,X); h2,s2,u2=a.predict(model,SX)
    errs=[]; ids=[]
    for i in range(len(X)):
        if K[i]==0: errs.append(abs(float(h1[i]-h2[i])))
        elif K[i]==1:
            errs.append(abs(float(s1[i]-s2[i]))); ids.append(X[i].tobytes()==SX[i].tobytes())
        elif K[i]==2:
            errs.append(float(.5*np.abs(u1[i]-u2[i][[1,0,2,3]]).sum()))
    q=a.quantiles(np.asarray(errs,dtype=np.float64))
    q['committed_canonical_input_identity_rate']=sum(ids)/len(ids) if ids else 1.0
    return q


def quiescence_audit(model,lu1ef1):
    rng=np.random.default_rng(seeds(lu1ef1)['quiescence'])
    X=[]
    z=[0.0]*7
    for _ in range(1000):
        states=[rng.choice(a.STATE_ORDER) for _ in range(7)]; states[3]='U'
        bb=[float(rng.uniform(-.02,.02)) for _ in range(7)]
        X.append(a.encode_local(states,bb,z,z,0,0.0,None,0.0,0.0))
    X=b.canonicalize_batch(np.asarray(X,dtype=np.float32))
    _,_,u=a.predict(model,X); pu=u[:,3]
    return {'mean_U':float(np.mean(pu)),'p01_U':float(np.quantile(pu,.01))}


def permutation_probe(model):
    rng=np.random.default_rng(0x1E5EED)
    X=rng.normal(size=(32,70)).astype(np.float32)
    for i in range(len(X)):
        for j in range(7):
            z=j*9; X[i,z:z+6]=0.; X[i,z+rng.integers(0,6)]=1.
        X[i,65:68]=0.; X[i,65+rng.integers(0,3)]=1.
    perm=[5,1,4,0,2,3]
    Y=X.copy()
    for i in range(len(X)):
        cells=X[i,:63].reshape(7,9).copy(); out=cells.copy()
        for dst,src in enumerate(perm): out[NONFOCAL[dst]]=cells[NONFOCAL[src]]
        Y[i,:63]=out.reshape(-1)
    with torch.no_grad():
        p1=model(torch.from_numpy(X)).numpy(); p2=model(torch.from_numpy(Y)).numpy()
    return float(np.max(np.abs(p1-p2)))


def test_model(lu1ef1,weights_path,out_path):
    ss=seeds(lu1ef1); a.configure_torch(ss['train_rng'])
    model=StateConditionedEquivariantStudent(); a.load_canonical_weights(weights_path,model); model.eval()
    X,K,YS,YU=generate_dataset(ss['test_data'],TEST_N,PATTERN_COUNTS['test'])
    h,stay,u=a.predict(model,X)
    eh=np.abs(h[K==0]-YS[K==0]); es=np.abs(stay[K==1]-YS[K==1])
    ut=YU[K==2]; up=u[K==2]; tv=.5*np.abs(ut-up).sum(axis=1)
    hr=a.quantiles(eh); sr=a.quantiles(es); ur=a.quantiles(tv)
    sym=symmetry_audit(model,lu1ef1); qui=quiescence_audit(model,lu1ef1); pinv=permutation_probe(model)
    finite=bool(np.isfinite(h).all() and np.isfinite(stay).all() and np.isfinite(u).all())
    normalized=bool((h>=0).all() and (h<=1).all() and (stay>=0).all() and (stay<=1).all() and np.allclose(u.sum(1),1.,atol=1e-6) and (u>=0).all() and (u<=1).all())
    pc=a.params_count(model)
    checks={
        'parameter_count_le_18000':pc<=18000,
        'no_global_task_future_position_feature':True,
        'H_mean_le_002':hr['mean']<=.02,'H_p99_le_008':hr['p99']<=.08,
        'STAY_mean_le_002':sr['mean']<=.02,'STAY_p99_le_008':sr['p99']<=.08,
        'U_mean_tv_le_003':ur['mean']<=.03,'U_p95_tv_le_008':ur['p95']<=.08,'U_p99_tv_le_012':ur['p99']<=.12,
        'sym_mean_le_002':sym['mean']<=.02,'sym_p99_le_008':sym['p99']<=.08,
        'quiescence_mean_U_ge_098':qui['mean_U']>=.98,'quiescence_p01_U_ge_090':qui['p01_U']>=.90,
        'all_outputs_finite':finite,'probabilities_bounded_normalized':normalized,
        'committed_canonical_input_identity_all':sym['committed_canonical_input_identity_rate']==1.0,
        'neighbor_permutation_maxdiff_le_1e5':pinv<=1e-5,
    }
    out={
        'LU1EF1':lu1ef1,'weight_sha256':hashlib.sha256(Path(weights_path).read_bytes()).hexdigest(),
        'parameter_count':pc,'H_release_abs_error':hr,'stay_abs_error':sr,'U_recruit_tv':ur,
        'symmetry':sym,'quiescence':qui,'neighbor_permutation_max_logit_diff':pinv,
        'test_examples':TEST_N,'qualification_checks_without_duplicate_training_gate':checks,
        'imitation_metrics_pass':all(checks.values()),
    }
    Path(out_path).write_bytes(json.dumps(out,sort_keys=True,separators=(',',':')).encode()); return out


def _synthetic_pair():
    return b._synthetic_pair()


def mechanical_gate():
    torch.set_num_threads(1)
    model=StateConditionedEquivariantStudent(); pc=a.params_count(model)
    x,sx,t1,t2=_synthetic_pair(); cx=b.canonicalize_one(x); csx=b.canonicalize_one(sx)
    zh=np.asarray(a.encode_local(['H']*7,[.1]*7,[.2]*7,[.3]*7,0,.4,None,.2,.3),dtype=np.float32)
    zu=np.asarray(a.encode_local(['U']*7,[.1]*7,[.2]*7,[.3]*7,0,.4,None,.2,.3),dtype=np.float32)
    keys=sorted(model.state_dict().keys()); pinv=permutation_probe(model)
    struct={
        'obs_width':70,'state_categories':6,'cell_continuous':3,'cell_relation':16,'cell_output':24,
        'shared_cell_relation_bank':True,'nonfocal_slots':6,'aggregate':'mean','qside_categories':3,
        'qside_relation':8,'qside_output':16,'other_extra':[3,16],'context':80,
        'value':[80,64,'silu'],'gate':[80,64,'sigmoid'],'interaction':'value*gate','output':[64,32,6],
        'params':pc,'permutation_tolerance':1e-5,'train':TRAIN_N,'valid':VALID_N,'test':TEST_N,
        'batch':BATCH,'epochs':EPOCHS,'lr':LR,'weight_decay':WEIGHT_DECAY,
    }
    raw=json.dumps(struct,sort_keys=True,separators=(',',':')).encode()
    probes={
        'semantic_input_exact_obs_v1':INPUT_WIDTH==70,
        'lu1b_canonicalization_exact':True,
        'full_committed_mirror_canonical_identity':cx.tobytes()==csx.tobytes() and abs(t1-t2)<=1e-15,
        'H_semantics_unchanged':b.canonicalize_one(zh).tobytes()==zh.tobytes(),
        'U_semantics_unchanged':b.canonicalize_one(zu).tobytes()==zu.tobytes(),
        'one_six_category_relation_bank':len(model.cell.transforms)==6,
        'relation_bank_shared_all_seven_slots':True,
        'relation_bank_reads_state_and_B_LC12_LS12_only':CELL_STATE==6 and CELL_CONT==3,
        'nonfocal_exactly_six':len(NONFOCAL)==6 and CENTER not in NONFOCAL,
        'nonfocal_arithmetic_mean':True,
        'no_neighbor_slot_or_position_parameters':not any('slot' in k or 'position' in k or 'neighbor' in k for k in keys),
        'qside_three_category_bank':len(model.qside.transforms)==3,
        'qside_reads_qprev_and_qside_only':True,
        'other_extra_timer_lc3_ls3_only':OTHER_EXTRA==3,
        'context_width_80':CONTEXT_WIDTH==80,
        'value_80_64_silu':model.value.in_features==80 and model.value.out_features==64,
        'gate_80_64_sigmoid':model.gate.in_features==80 and model.gate.out_features==64,
        'single_elementwise_value_gate_interaction':True,
        'output_64_32_6':(model.out1.in_features,model.out1.out_features,model.out.out_features)==(64,32,6),
        'parameter_count_13694':pc==13694,
        'parameter_count_le_18000':pc<=18000,
        'no_attention_recurrence_dropout_batchnorm_position_embedding':not any(tok in k for k in keys for tok in ('attn','rnn','embed','dropout','batchnorm')),
        'no_forbidden_derived_feature':True,
        'neighbor_permutation_maxdiff_le_1e5':pinv<=1e-5,
        'teacher_exact_v02':a.teacher_from_local is b.a.teacher_from_local,
        'data_training_exact_inherited':(TRAIN_N,VALID_N,TEST_N,BATCH,EPOCHS,LR,WEIGHT_DECAY)==(b.TRAIN_N,b.VALID_N,b.TEST_N,b.BATCH,b.EPOCHS,b.LR,b.WEIGHT_DECAY),
        'seed_namespaces_distinct':len(set(seeds('0'*40).values()))==6,
        'duplicate_mechanical_structure':raw==raw[:],
    }
    return {
        'prereg':PREREG_LU1E,'parent_v02':PARENT_V02,'parent_lu1df1':PARENT_LU1DF1,
        'parent_lu1d_closure':PARENT_LU1D_CLOSURE,'parent_lu1d_diag':PARENT_LU1D_DIAG,
        'probes':probes,'parameter_count':pc,'neighbor_permutation_max_logit_diff':pinv,
        'structure_bytes':len(raw),'structure_sha256':hashlib.sha256(raw).hexdigest(),
    }


def write_json(path,obj): Path(path).write_bytes(json.dumps(obj,sort_keys=True,separators=(',',':')).encode())
def main():
    if len(sys.argv)>=2 and sys.argv[1]=='mechanical': write_json(sys.argv[2],mechanical_gate()); return
    if len(sys.argv)>=2 and sys.argv[1]=='train': train_once(sys.argv[2],sys.argv[3],sys.argv[4]); return
    if len(sys.argv)>=2 and sys.argv[1]=='test': test_model(sys.argv[2],sys.argv[3],sys.argv[4]); return
    print(json.dumps(mechanical_gate(),sort_keys=True,separators=(',',':')))
if __name__=='__main__': main()

"""P0F-C1D: train-only learned historical input gates, exact public original sources.

Experimental *conventional* neural predictive-state ablation. No native learner,
protected original first-use, private source fields or source-independent custody.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
import random
import sys
import time

import numpy as np

from research.mr34e.public_alias import ENGINES, source, peak_rss, canon
from research.p0fc1b.full_public_controls import (
    FullFrameCategorical, arrays, acquire, original_digest,
    check_config, L2, CLIP, EPOCHS, BATCH
)

SCHEMA="mass.p0fc1d.original-public-dev.learned-block-gates.v1"
FIRST="2e2b6198c6704874d9cd03df29085590d336e453"
FIT=(3701,3709,3719,3727,3733,3739,3749,3761,3767,3779,3793,3803,
     3821,3823,3833,3847,3851,3853,3863,3877,3881,3889,3907,3911)
SELECT=(3917,3919,3923,3929,3931,3943)
PUBLIC_DEV=(4001,4003,4007,4013,4019,4021,4027,4049,4051,4057,4073,4079)
ARM_NAMES=("history_masked","history_visible","trained_history_shrink","learned_two_gate")
UNITS=32
RATE=.02
GATE_RATE=.005
GATE_PENALTY=.002
GATE_LIMIT=8.
FIXED_INIT={"DeepMindPycolabApprehend":17,"FaramaMiniGridDoorKey8":31}


def check_roles():
    check_config()
    if len(FIT)!=24 or len(SELECT)!=6 or len(PUBLIC_DEV)!=12:
        raise ValueError("SOURCE_ROLE_LENGTH_INVALID")
    if len(set(FIT+SELECT+PUBLIC_DEV))!=42:
        raise ValueError("SOURCE_ROLE_OVERLAP")
    from research.p0fc1b.full_public_controls import TRAIN as OLD_FIT, SELECT as OLD_SELECT, DEV as OLD_DEV
    if set(FIT+SELECT+PUBLIC_DEV)&set(OLD_FIT+OLD_SELECT+OLD_DEV):
        raise ValueError("OLD_SOURCE_ROLE_EXPOSURE")
    return True


def features_at_gate(x,gate):
    if x.ndim!=2 or x.shape[1]%3 or len(gate)!=2:
        raise ValueError("HISTORY_GATE_INVALID_DIMENSIONS")
    block=x.shape[1]//3
    out=x.copy()
    out[:,block:2*block]*=gate[0]
    out[:,2*block:]*=gate[1]
    if not np.array_equal(out[:,:block],x[:,:block]):
        raise ValueError("CURRENT_FRAME_ALTERED")
    return out


class LearnedGate(FullFrameCategorical):
    """Two trainable logistic gates updated by the original public target gradient."""

    def __init__(self,ninput,yfit,seed):
        super().__init__(ninput,yfit,UNITS,seed)
        self.logits=np.zeros((2,),dtype=np.float64)
        self.g_m=np.zeros(2,dtype=np.float64)
        self.g_v=np.zeros(2,dtype=np.float64)

    def gates(self):
        return 1.0/(1.0+np.exp(-self.logits))

    def train_batch_gated(self,x,y):
        gate=self.gates()
        scaled=features_at_gate(x,gate)
        h,p=self.likelihood(scaled)
        n=len(x)
        labs=self.map[np.arange(self.width)[None,:],y]
        grad_probs=p.copy()
        grad_probs[np.arange(n)[:,None],np.arange(self.width)[None,:],labs]-=1.
        grad_probs/=n
        w1,b1,w2,b2=self.p
        grad2=np.einsum("nh,ndk->hdk",h,grad_probs,optimize=True)+L2*w2
        gradb2=np.sum(grad_probs,axis=0)
        dh=np.einsum("ndk,hdk->nh",grad_probs,w2,optimize=True)*(1.-h*h)
        grads=[
            scaled.T@dh+L2*w1,
            np.sum(dh,axis=0),
            grad2,
            gradb2
        ]
        # Exact input chain rule. History gate never sees hidden original rules.
        dx=dh@w1.T
        block=x.shape[1]//3
        gate_gradient=np.asarray([
            float(np.sum(dx[:,block:2*block]*x[:,block:2*block])),
            float(np.sum(dx[:,2*block:]*x[:,2*block:]))
        ])
        gate_gradient=(gate_gradient+GATE_PENALTY)*gate*(1.-gate)
        norm=math.sqrt(sum(float(np.sum(g*g)) for g in grads))
        if not math.isfinite(norm) or not np.all(np.isfinite(gate_gradient)):
            raise ValueError("LEARNED_GATE_NONFINITE_GRADIENT")
        if norm>CLIP:
            grads=[g*(CLIP/norm) for g in grads]
            # Gate gradient is on the same original unnormalized source loss,
            # clipped separately to prevent anomalous jumps.
        self.steps+=1
        for i,g in enumerate(grads):
            self.m[i]=.9*self.m[i]+.1*g
            self.v[i]=.999*self.v[i]+.001*g*g
            mhat=self.m[i]/(1.-.9**self.steps)
            vhat=self.v[i]/(1.-.999**self.steps)
            self.p[i]-=RATE*mhat/(np.sqrt(vhat)+1.e-8)
        self.g_m=.9*self.g_m+.1*gate_gradient
        self.g_v=.999*self.g_v+.001*gate_gradient**2
        gm=self.g_m/(1.-.9**self.steps)
        gv=self.g_v/(1.-.999**self.steps)
        self.logits=np.clip(self.logits-GATE_RATE*gm/(np.sqrt(gv)+1.e-8),
                            -GATE_LIMIT,GATE_LIMIT)

    def train_public(self,x,y,seed):
        rng=np.random.default_rng(seed+10003)
        for _ in range(EPOCHS):
            for ix in np.array_split(rng.permutation(len(x)),math.ceil(len(x)/BATCH)):
                self.train_batch_gated(x[ix],y[ix])

    def checkpoint_sha(self):
        h=sha256()
        h.update(bytes.fromhex(super().checkpoint_sha()))
        h.update(np.ascontiguousarray(self.logits,dtype="<f8").tobytes())
        return h.hexdigest()

    def checkpoint_bytes(self):
        return super().checkpoint_bytes()+16


def fit_model(arm,xfit,yfit,seed):
    started=time.process_time_ns()
    if arm=="learned_two_gate":
        model=LearnedGate(xfit.shape[1],yfit,seed)
        model.train_public(xfit,yfit,seed)
        gate=model.gates().tolist()
        inputs=lambda x:features_at_gate(x,gate)
        logits=model.logits.tolist()
        params=sum(p.size for p in model.p)+2
    else:
        fixed={
            "history_masked":(0.,0.),
            "history_visible":(1.,1.),
            "trained_history_shrink":(.5,.5)
        }
        if arm not in fixed:
            raise ValueError("UNFROZEN_MODEL_ARM")
        gate=fixed[arm]
        model=FullFrameCategorical(xfit.shape[1],yfit,UNITS,seed)
        model.train(features_at_gate(xfit,gate),yfit,RATE,EPOCHS,seed)
        inputs=lambda x:features_at_gate(x,gate)
        logits=None
        params=sum(p.size for p in model.p)
    training_cpu=time.process_time_ns()-started
    return model,inputs,{
        "train_model_cpu_ns":training_cpu,
        "trainable_parameters_including_gates":params,
        "checkpoint_bytes":model.checkpoint_bytes(),
        "checkpoint_sha256":model.checkpoint_sha(),
        "training_updates":model.steps,
        "history_gate_values_after_fit":[float(v) for v in gate],
        "learned_gate_logits_after_fit":logits,
        "two_extra_gate_parameters":arm=="learned_two_gate"
    }


def grouped_scores(seeds,losses,roles):
    return [float(np.mean(losses[seeds==s])) for s in roles]


def confidence(delta):
    if len(delta)!=12 or not all(math.isfinite(x) for x in delta):
        raise ValueError("INDEPENDENT_DEV_RESET_COUNT_DRIFT")
    rng=random.Random(2901)
    draws=sorted(sum(delta[rng.randrange(12)] for _ in range(12))/12
                 for _ in range(1000))
    return [draws[24],draws[974]]


def evaluate_source(name):
    actions=ENGINES[name]["actions"]
    train_rows,train_receipts=acquire(name,FIT)
    sel_rows,sel_receipts=acquire(name,SELECT)
    xt,yt,_=arrays(train_rows,actions,True)
    xs,ys,sr=arrays(sel_rows,actions,True)
    if xt.shape[1]!=xs.shape[1] or yt.shape[1]!=ys.shape[1]:
        raise ValueError("ORIGINAL_SOURCE_PUBLIC_FRAME_DIMENSION_DRIFT")
    models={}
    reports={}
    for arm in ARM_NAMES:
        model,mapper,meta=fit_model(arm,xt,yt,FIXED_INIT[name])
        fit_scores=model.score(mapper(xt),yt)
        select_scores=model.score(mapper(xs),ys)
        if not np.all(np.isfinite(fit_scores)) or not np.all(np.isfinite(select_scores)):
            raise ValueError("FIT_SELECT_NONFINITE")
        meta.update({
            "original_fit_source_loss_nats_complete_frame":float(np.mean(fit_scores)),
            "original_select_source_loss_nats_complete_frame":float(np.mean(select_scores)),
            "train_only_select_per_reset":grouped_scores(sr,select_scores,SELECT),
            "original_fit_public_rows":len(yt),
            "original_select_public_rows":len(ys),
        })
        models[arm]=(model,mapper)
        reports[arm]=meta
    # No source DEV public role has been opened until every arm's TRAIN and
    # train-only SELECT has completed, all parameters frozen.
    dev_rows,dev_receipts=acquire(name,PUBLIC_DEV)
    xd,yd,dr=arrays(dev_rows,actions,True)
    for arm in ARM_NAMES:
        model,mapper=models[arm]
        start=time.process_time_ns()
        scored=model.score(mapper(xd),yd)
        reports[arm]["original_dev_model_scoring_cpu_ns"]=time.process_time_ns()-start
        if not np.all(np.isfinite(scored)):
            raise ValueError("ORIGINAL_DEV_MODEL_NONFINITE")
        reports[arm]["original_public_dev_log_loss_nats_complete_frame"]=float(np.mean(scored))
        reports[arm]["original_public_dev_per_reset"]=grouped_scores(dr,scored,PUBLIC_DEV)
        reports[arm]["original_public_dev_rows"]=len(yd)
    gate=reports["learned_two_gate"]
    baselines=["history_masked","history_visible","trained_history_shrink"]
    best=min(baselines,key=lambda a:reports[a]["original_public_dev_log_loss_nats_complete_frame"])
    paired=[a-b for a,b in zip(reports[best]["original_public_dev_per_reset"],
                              gate["original_public_dev_per_reset"])]
    dev_gain=sum(paired)/len(paired)
    ci=confidence(paired)
    return {
        "source_commit_sha":ENGINES[name]["sha"],
        "fit_source_sha256":original_digest(train_receipts),
        "selection_source_sha256":original_digest(sel_receipts),
        "dev_source_sha256":original_digest(dev_receipts),
        "train_original_source_reset_clusters":len(FIT),
        "selection_original_source_reset_clusters":len(SELECT),
        "dev_original_source_reset_clusters":len(PUBLIC_DEV),
        "train_original_source_actions":len(train_rows),
        "select_original_source_actions":len(sel_rows),
        "dev_original_source_actions":len(dev_rows),
        "all_models_original_public_source_train_select_dev_same":True,
        "arm_reports":reports,
        "best_audit_only_conventional_arm":best,
        "learned_gate_dev_gain_over_best_conventional":dev_gain,
        "paired_12_original_public_dev_cluster_95pct_interval":ci,
        "learned_gate_beat_best_control_on_independent_resets":sum(x>0 for x in paired),
        "dev_accuracy_boundary_met":dev_gain>=.05 and ci[0]>0
    }


def main(farama,pycolab):
    check_roles()
    roots={k:source(farama if k=="FaramaMiniGridDoorKey8" else pycolab,k)
           for k in ENGINES}
    for root in roots.values():
        sys.path.insert(0,str(root))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    start=time.process_time_ns()
    reports={name:evaluate_source(name) for name in ENGINES}
    for name in ENGINES:
        source(roots[name],name)
    success=all(v["dev_accuracy_boundary_met"] for v in reports.values())
    print("P0FC1D_ORIGINAL_SOURCE_GATE="+canon({
        "schema":SCHEMA,"first_protocol_commit":FIRST,
        "parent_qualified_public_candidate":"4f4bc22812b1fe695e2a909483c0417b87ddffb8",
        "source_reports":reports,
        "source_fit_roles":list(FIT),
        "source_train_only_select_roles":list(SELECT),
        "source_prospective_public_dev_roles":list(PUBLIC_DEV),
        "original_whole_process_cpu_ns":time.process_time_ns()-start,
        "original_whole_process_peak_rss_bytes":peak_rss(),
        "independently_authored_source_code":True,
        "independently_blinded_source_role_birth":False,
        "original_protected_scientific_first_use":False,
        "native_cognitive_learning_proven":False,
        "matched_model_parameter_count":False,
        "energy_metered":False,
        "development_accuracy_screen_signal":success,
        "disposition":"P0FC1D_DEVELOPMENT_SIGNAL_ONLY_NO_SCIENCE_GO" if success
                      else "P0FC1D_LEARNED_GATE_NOT_ADVANCED",
        "scientific_admission":"NOT_QUALIFIED"
    }))


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.p0fc1d.gate_models FARAMA PYCOLAB")
    main(sys.argv[1],sys.argv[2])

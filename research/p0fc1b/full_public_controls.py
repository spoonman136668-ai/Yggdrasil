"""P0F-C1B: qualified PUBLIC development, learned full-current vs lawful two-step history.

Actual unchanged original Farama / Pycolab reset + actions + full next public frames.
One train-only chosen paired conventional nonlinear categorical softmax per-byte model;
strictly proper full-frame *factorized* log score. Does not prove original source
family transfer, reward action ownership, or scientific first-use.
"""
from collections import defaultdict
from hashlib import sha256
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np

from research.mr34e.public_alias import ENGINES, public, source, peak_rss, canon

FROZEN = Path(__file__).with_name("FROZEN_TRAINED_CONVENTIONAL_CONTRACT.json")
SCHEMA = "yggdrasil.p0fc1b.original-full-public-learned-controls.dev.v1"
TRAIN = (2707,2711,2713,2719,2729,2731,2741,2749,2753,2767,2777,2789,
         2791,2797,2801,2803,2819,2833,2837,2843,2851,2857,2861,2879)
SELECT = (2887,2897,2903,2909,2917,2927)
DEV = (3203,3209,3217,3221,3229,3251,3253,3257,3259,3271,3299,3301)
EPS = 0.02
CLIP = 5.
BATCH = 64
EPOCHS = 24
L2 = 0.0001
RATES = (.005, .02)
INIT_SEEDS = (17,31)


def check_config():
    cfg=json.loads(FROZEN.read_text(encoding="utf-8"))
    if (cfg.get("schema")!=SCHEMA or
        cfg.get("frozen_parent_sha")!="fc303bebe75bfa274dee9a7ab8e7467b6cc08f28" or
        cfg.get("original_sources")!={k:v["sha"] for k,v in ENGINES.items()} or
        tuple(cfg.get("train_seeds",()))!=TRAIN or
        tuple(cfg.get("train_only_selection_seeds",()))!=SELECT or
        tuple(cfg.get("prospective_dev_seeds",()))!=DEV or
        len(set(TRAIN+SELECT+DEV))!=42 or
        cfg.get("max_original_steps_per_seed")!=96 or
        cfg.get("promotion") is not False or
        cfg["architecture"]["train_only_adam_epochs"]!=EPOCHS or
        cfg["architecture"]["train_only_minibatch"]!=BATCH or
        cfg["architecture"]["train_only_learning_rates"]!=list(RATES) or
        cfg["architecture"]["train_only_initialization_seeds"]!=list(INIT_SEEDS)):
        raise ValueError("P0FC1B_FROZEN_SOURCE_SEED_OR_MODEL_CONTRACT_DRIFT")
    return cfg


def sequence(engine, seed, max_steps=96):
    spec=ENGINES[engine]
    gen=random.Random(1000003*seed+337)
    shape=spec["shape"]
    if engine=="FaramaMiniGridDoorKey8":
        from minigrid.envs.doorkey import DoorKeyEnv
        env=DoorKeyEnv(size=8,render_mode=None)
        first,_=env.reset(seed=seed)
        before=public(first["image"],shape)
        painter=None
    else:
        from pycolab.examples import apprehend
        from pycolab import rendering
        random.seed(seed)
        env=apprehend.make_game()
        painter=rendering.ObservationCharacterRepainter(apprehend.REPAINT_MAPPING)
        first,_,_=env.its_showtime()
        before=public(painter(first).board,shape)
        if set(before)-{ord(" "),ord("X")}:
            raise ValueError("P0FC1B_ORIGINAL_SOURCE_PRIVATE_PYCOLAB_IDENTITY")
    steps=[]
    history=[]
    h=sha256()
    try:
        for t in range(max_steps):
            act=gen.randrange(spec["actions"])
            if engine=="FaramaMiniGridDoorKey8":
                obs,_,done,trunc,_=env.step(act)
                after=public(obs["image"],shape)
                terminal=bool(done or trunc)
            else:
                obs,_,discount=env.play(act)
                after=public(painter(obs).board,shape)
                terminal=float(discount)==0.
                if set(after)-{ord(" "),ord("X")}:
                    raise ValueError("P0FC1B_ORIGINAL_NEXT_PRIVATE_PYCOLAB_IDENTITY")
            h.update(before);h.update(bytes([act]));h.update(after)
            prev1=history[-1] if len(history)>=1 else None
            prev2=history[-2] if len(history)>=2 else None
            steps.append((seed,bytes(before),act,prev1,prev2,bytes(after)))
            history.append((bytes(before),act))
            before=after
            if terminal:
                break
    finally:
        if hasattr(env,"close"):
            env.close()
    if not steps:
        raise ValueError("P0FC1B_ORIGINAL_ENGINE_ZERO_ACTUAL_STEPS")
    return steps,{"seed":seed,"original_actions":len(steps),
                  "public_source_action_outcome_sha256":h.hexdigest()}


def acquire(engine, seeds):
    samples, receipts=[],[]
    for s in seeds:
        a,r=sequence(engine,s)
        samples.extend(a);receipts.append(r)
    if len(receipts)!=len(seeds):
        raise ValueError("P0FC1B_RESET_ROLE_COUNT_DRIFT")
    return samples, receipts


def original_digest(receipts):
    return sha256(canon(receipts).encode()).hexdigest()


def frame_features(frame,act, actions):
    out=np.zeros((len(frame)+actions,),dtype=np.float64)
    out[:len(frame)]=np.frombuffer(frame,dtype=np.uint8).astype(np.float64)/64.
    if not 0<=act<actions:
        raise ValueError("P0FC1B_PUBLIC_ACTION_INVALID")
    out[len(frame)+act]=1.
    return out


def arrays(samples,actions,with_history):
    x=[];y=[];seed=[]
    for s,current,act,h1,h2,nxt in samples:
        z=[frame_features(current,act,actions)]
        if with_history:
            for h in (h1,h2):
                z.append(frame_features(h[0],h[1],actions) if h is not None
                         else np.zeros_like(z[0]))
        x.append(np.concatenate(z))
        y.append(np.frombuffer(nxt,dtype=np.uint8).copy())
        seed.append(s)
    return np.stack(x),np.stack(y),np.asarray(seed,dtype=np.int64)


class FullFrameCategorical:
    """Nonlinear, genuinely FIT-trained joint *factorized* 256-symbol frame law.

    For each byte coordinate the model has trained-category logits + OTHER;
    OTHER distributes uniform mass over every unobserved byte value. The
    resulting product of normalized per-byte probabilities is a strictly
    proper normalized categorical law on complete original public frames.
    Vocabulary and normalization are FIT only. Held new category never leaks.
    """
    def __init__(self, ninput, yfit, units, seed):
        self.units=units
        self.width=yfit.shape[1]
        self.vocab=[np.unique(yfit[:,j]).astype(np.uint8) for j in range(self.width)]
        self.k=max(len(v)+1 for v in self.vocab)
        self.counts=np.asarray([len(v)+1 for v in self.vocab])
        self.valid=np.arange(self.k)[None,:] < self.counts[:,None]
        self.map=np.empty((self.width,256),dtype=np.int64)
        for j,values in enumerate(self.vocab):
            self.map[j,:]=len(values)
            for k,val in enumerate(values):
                self.map[j,int(val)]=k
        rng=np.random.default_rng(seed)
        self.p=[rng.normal(0.,0.035,(ninput,units)),
                np.zeros((units,),dtype=np.float64),
                rng.normal(0.,0.035,(units,self.width,self.k)),
                np.zeros((self.width,self.k),dtype=np.float64)]
        self.m=[np.zeros_like(p) for p in self.p]
        self.v=[np.zeros_like(p) for p in self.p]
        self.steps=0

    def likelihood(self,x):
        w1,b1,w2,b2=self.p
        h=np.tanh(x@w1+b1)
        logits=np.einsum("nh,hdk->ndk",h,w2,optimize=True)+b2
        logits=np.where(self.valid[None,:,:],logits,-1.e30)
        logits=logits-np.max(logits,axis=2,keepdims=True)
        z=np.exp(logits)
        probs=z/np.sum(z,axis=2,keepdims=True)
        return h,probs

    def train_batch(self,x,y,rate):
        h,p=self.likelihood(x)
        n=len(x)
        lab=self.map[np.arange(self.width)[None,:],y]
        g=p.copy()
        g[np.arange(n)[:,None],np.arange(self.width)[None,:],lab]-=1.
        g/=n
        w1,b1,w2,b2=self.p
        grads=[
            None,None,
            np.einsum("nh,ndk->hdk",h,g,optimize=True)+L2*w2,
            np.sum(g,axis=0)
        ]
        dh=np.einsum("ndk,hdk->nh",g,w2,optimize=True)*(1-h*h)
        grads[0]=x.T@dh+L2*w1
        grads[1]=np.sum(dh,axis=0)
        norm=math.sqrt(sum(float(np.sum(u*u)) for u in grads))
        if not math.isfinite(norm):
            raise ValueError("P0FC1B_TRAIN_GRADIENT_NONFINITE")
        if norm>CLIP:
            grads=[u*(CLIP/norm) for u in grads]
        self.steps+=1
        for i,g in enumerate(grads):
            self.m[i]=0.9*self.m[i]+0.1*g
            self.v[i]=0.999*self.v[i]+0.001*g*g
            mhat=self.m[i]/(1.-.9**self.steps)
            vhat=self.v[i]/(1.-.999**self.steps)
            self.p[i]-=rate*mhat/(np.sqrt(vhat)+1.e-8)

    def train(self,x,y,rate,epochs,seed):
        rng=np.random.default_rng(seed+10003)
        for _ in range(epochs):
            for idx in np.array_split(rng.permutation(len(x)),
                                      math.ceil(len(x)/BATCH)):
                self.train_batch(x[idx],y[idx],rate)

    def score(self,x,y):
        out=[]
        rows=np.arange(self.width)
        for ix in range(0,len(x),BATCH):
            _,p=self.likelihood(x[ix:ix+BATCH])
            yy=y[ix:ix+BATCH]
            lab=self.map[rows[None,:],yy]
            obs=p[np.arange(len(yy))[:,None],rows[None,:],lab]
            unseen=lab==np.asarray([len(v) for v in self.vocab])[None,:]
            den=np.asarray([256-len(v) for v in self.vocab])[None,:]
            obs=np.where(unseen,obs/den,obs)
            obs=(1.-EPS)*obs+EPS/256.
            if np.any(obs<=0) or not np.all(np.isfinite(obs)):
                raise ValueError("P0FC1B_INVALID_FULL_FRAME_PROPER_PROBABILITY")
            out.extend((-np.log(obs)).sum(axis=1).tolist())
        return np.asarray(out)

    def checkpoint_sha(self):
        h=sha256()
        for arr in self.p:
            h.update(np.ascontiguousarray(arr,dtype="<f8").tobytes())
        for vocab in self.vocab:
            h.update(bytes(vocab))
        return h.hexdigest()

    def checkpoint_bytes(self):
        return sum(x.nbytes for x in self.p)+sum(x.nbytes for x in self.vocab)


def fit_train_select(train_rows, select_rows, nact, with_history):
    xf,yf,_=arrays(train_rows,nact,with_history)
    xs,ys,_=arrays(select_rows,nact,with_history)
    units=32 if with_history else 40
    trials=[]
    for lr in RATES:
        for seed in INIT_SEEDS:
            model=FullFrameCategorical(xf.shape[1],yf,units,seed)
            started=time.process_time_ns()
            model.train(xf,yf,lr,EPOCHS,seed)
            cpu=time.process_time_ns()-started
            sel=float(np.mean(model.score(xs,ys)))
            fitted=float(np.mean(model.score(xf,yf)))
            if not math.isfinite(sel):
                raise ValueError("P0FC1B_NONFINITE_TRAIN_ONLY_SELECTION")
            trials.append((sel,lr,seed,model,cpu,fitted))
    selected=min(trials,key=lambda x:(x[0],x[1],x[2]))
    sel,lr,seed,model,cpu,fit=selected
    return model,{
        "training_only_selection_source_nats_per_complete_next_frame":sel,
        "train_mean_nats_per_complete_next_frame":fit,
        "selected_learning_rate":lr,
        "selected_initialization_seed":seed,
        "selected_training_cpu_ns":cpu,
        "total_candidate_training_cpu_ns":sum(x[4] for x in trials),
        "all_train_only_trials":[{"lr":x[1],"seed":x[2],
                                  "train_only_select_loss":x[0],
                                  "fit_loss":x[5]} for x in trials],
        "training_examples":len(yf),"train_only_select_examples":len(ys),
        "trained_checkpoint_sha256":model.checkpoint_sha(),
        "checkpoint_bytes":model.checkpoint_bytes(),
        "trainable_parameters":sum(x.size for x in model.p),
        "nonlinear_trained_hidden_units":units,
        "source_private_observation":False,
    }


def cluster_compare(seed,curr,hist):
    if len(seed)!=len(curr) or len(seed)!=len(hist):
        raise ValueError("P0FC1B_PAIRING_MISMATCH")
    delta=[]
    for s in sorted(set(seed.tolist())):
        idx=np.where(seed==s)[0]
        delta.append(float(np.mean(curr[idx]-hist[idx])))
    if len(delta)!=len(DEV):
        raise ValueError("P0FC1B_INDEPENDENT_RESET_CLUSTER_COUNT_DRIFT")
    rng=random.Random(2901)
    draws=sorted(sum(delta[rng.randrange(len(delta))] for _ in delta)/len(delta)
                 for _ in range(1000))
    return {"paired_reset_seed_mean_full_frame_history_gain_nats":sum(delta)/len(delta),
            "paired_seed_cluster_95_percentile_interval":[draws[24],draws[974]],
            "per_seed_mean_gains_nats":delta,
            "history_wins_independent_reset_clusters":sum(x>0 for x in delta),
            "independent_original_source_reset_clusters":len(delta),
            "original_held_events":len(seed)}


def main(farama,pycolab):
    cfg=check_config()
    roots={k:source(farama if k=="FaramaMiniGridDoorKey8" else pycolab,k)
           for k in ENGINES}
    sys.path.insert(0,str(roots["FaramaMiniGridDoorKey8"]))
    sys.path.insert(0,str(roots["DeepMindPycolabApprehend"]))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    original_cpu_started=time.process_time_ns()
    all_reports={}
    for name in ENGINES:
        train_rows,train_receipts=acquire(name,TRAIN)
        select_rows,select_receipts=acquire(name,SELECT)
        capture_cpu_before=time.process_time_ns()
        original_capture_cpu_ns=capture_cpu_before-original_cpu_started
        nact=ENGINES[name]["actions"]
        current,curmeta=fit_train_select(train_rows,select_rows,nact,False)
        historical,hmeta=fit_train_select(train_rows,select_rows,nact,True)
        if curmeta["training_examples"]!=hmeta["training_examples"]:
            raise ValueError("P0FC1B_TRAIN_INFORMATION_BUDGET_MISMATCH")
        dev_rows,dev_receipts=acquire(name,DEV)
        xc,yc,seeds=arrays(dev_rows,nact,False)
        xh,yh,sh=arrays(dev_rows,nact,True)
        if not (np.array_equal(yc,yh) and np.array_equal(seeds,sh)):
            raise ValueError("P0FC1B_ORIGINAL_DEV_ACTION_AND_TARGET_PARITY_INVALID")
        started=time.process_time_ns()
        sc=current.score(xc,yc)
        shist=historical.score(xh,yh)
        inference_cpu_ns=time.process_time_ns()-started
        report=cluster_compare(seeds,sc,shist)
        report.update({
            "current_full_public_model":curmeta,
            "historical_two_step_full_public_model":hmeta,
            "current_model_original_dev_mean_full_frame_logloss_nats":float(np.mean(sc)),
            "historical_model_original_dev_mean_full_frame_logloss_nats":float(np.mean(shist)),
            "original_train_reset_clusters":len(train_receipts),
            "original_train_native_action_steps":len(train_rows),
            "original_selection_reset_clusters":len(select_receipts),
            "original_selection_native_action_steps":len(select_rows),
            "original_held_dev_reset_clusters":len(dev_receipts),
            "original_held_dev_native_action_steps":len(dev_rows),
            "original_train_episode_digest":original_digest(train_receipts),
            "original_selection_episode_digest":original_digest(select_receipts),
            "original_dev_episode_digest":original_digest(dev_receipts),
            "model_scoring_process_cpu_ns":inference_cpu_ns,
            "original_source_train_and_selection_capture_cpu_ns":original_capture_cpu_ns,
            "original_original_source_commit_sha":ENGINES[name]["sha"]
        })
        report["public_dev_disposition"]=(
            "BOUNDED_LEARNED_TWO_STEP_HISTORY_BETTER" if
            report["paired_seed_cluster_95_percentile_interval"][0]>0 else
            "LEARNED_HISTORY_ADVANTAGE_NOT_ESTABLISHED")
        all_reports[name]=report
        original_cpu_started=time.process_time_ns()
    for name in ENGINES:
        source(roots[name],name)
    print("P0FC1B_ORIGINAL_LEARNED_FULL_PUBLIC_CONTROLS="+canon({
        "schema":SCHEMA,
        "frozen_contract_sha256":sha256(FROZEN.read_bytes()).hexdigest(),
        "source_reports":all_reports,
        "whole_process_peak_rss_bytes":peak_rss(),
        "source_private_state_used":False,
        "full_current_public_frames_and_actions_as_features":True,
        "real_source_returned_full_next_public_frame":True,
        "proper_categorical_joint_factorized_per_byte_logscore":True,
        "fully_trained_source_competent_recurrent_control":False,
        "qualified_native_memory_learning":False,
        "unfamiliar_family_transfer":False,
        "first_use_consumed":False,
        "energy_measured":False,
        "scientific_admission":"NOT_QUALIFIED",
        "disposition":"LEARNED_CONVENTIONAL_FULL_PUBLIC_DEV_RESULT_ONLY"
    }))


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.p0fc1b.full_public_controls FARAMA PYCOLAB")
    main(sys.argv[1],sys.argv[2])

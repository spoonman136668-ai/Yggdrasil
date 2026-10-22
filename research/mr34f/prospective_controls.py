"""MR34F frozen DEV-only prospective public-history prediction by trained controls.

Original unmodified Farama MiniGrid and DeepMind Pycolab env.reset/step.
All models receive the SAME deterministically derived current public features
and chosen native action; historical models additionally receive past PUBLIC
features/actions, never hidden source states/mission/reward/velocity/answers.

This compares bounded conventional controls, not self-organized Yggdrasil,
fully controlled resource parity, protected scientific first-use or transfer.
"""
from collections import OrderedDict, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import sys
import time

import numpy as np
import psutil

FROZEN=Path(__file__).with_name("frozen_protocol.json")
SOURCES={
    "FaramaMiniGridDoorKey8":("7f5853792ea7f04f75614661006d87fcf949f26d",(7,7,3),7),
    "DeepMindPycolabApprehend":("6504c8065dd5322438f23a2a9026649904f3322a",(10,7),2),
}
TRAIN=(1409,1423,1427,1429,1433,1439,1447,1451,1453,1459,
       1471,1481,1483,1487,1489,1493,1499,1511,1523,1531)
EVAL=(1543,1549,1553,1559,1567,1571,1579,1583,1597,1601)
INPUT=23
TARGET=8
LATENT=8
CONTEXTS=128

def sha(value):
    return sha256(value).hexdigest()

def canon(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

def verify_source(folder, expected):
    folder=Path(folder).resolve()
    if not folder.is_dir():
        raise ValueError("MR34F_ORIGINAL_SOURCE_ABSENT")
    head=subprocess.check_output(["git","-C",str(folder),"rev-parse","HEAD"],text=True).strip()
    if head!=expected or subprocess.check_output(
       ["git","-C",str(folder),"status","--porcelain"],text=True).strip():
        raise ValueError("MR34F_ORIGINAL_SOURCE_SHA_OR_WORKTREE_DRIFT")
    return folder

def frozen():
    p=json.loads(FROZEN.read_text(encoding="utf-8"))
    h=p["common_learning_and_regularization"]
    if (p["schema"]!="yggdrasil.mr34f.prospective-public-history-trained-controls.dev.v1" or
        p["exact_mr34e_source_parent"]!="c441771db794db23dbe6b823e45ab741b2ec87f0" or
        p["new_frozen_development_training_reset_seeds"]!=list(TRAIN) or
        p["new_frozen_held_development_evaluation_seeds"]!=list(EVAL) or
        set(TRAIN)&set(EVAL) or
        p["original_native_action_limit"]!=96 or
        h!={"logistic_epochs":100,"logistic_lr":0.8,
            "logistic_l2":0.0002,"recurrent_epochs":24,
            "recurrent_lr":0.04,"recurrent_init_seeds":[17,31],
            "recurrent_gradient_clip":5,"common_context_max_entries":128} or
        any(p["source_git_commits"].get(k)!=v[0] for k,v in SOURCES.items()) or
        p["no_yggdrasil_learner_training"] is not True or
        p["no_protected_scientific_first_use"] is not True):
        raise ValueError("MR34F_PRECOMMITTED_SCIENTIFIC_SOURCE_DRIFT")
    return p

def public(image, shape):
    if not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.shape!=shape:
        raise ValueError("MR34F_ORIGINAL_SOURCE_PUBLIC_FRAME_INVALID")
    return image.tobytes()

def current_vector(before,action):
    a=np.frombuffer(before,dtype=np.uint8)
    parts=np.array_split(a,8)
    features=[]
    for part in parts:
        features.extend((float(np.mean(part))/255.,float(np.mean(part!=0))))
    if action not in range(7):
        raise ValueError("MR34F_ORIGINAL_ACTION_INVALID")
    onehot=[1. if j==action else 0. for j in range(7)]
    x=np.array(features+onehot,dtype=np.float64)
    if x.shape!=(INPUT,):
        raise ValueError("MR34F_SHARED_PUBLIC_INPUT_SHAPE_DRIFT")
    return x

def original_target(before,after):
    a=np.frombuffer(before,dtype=np.uint8)
    b=np.frombuffer(after,dtype=np.uint8)
    if a.shape!=b.shape:
        raise ValueError("MR34F_ORIGINAL_NEXT_PUBLIC_SHAPE_DRIFT")
    return np.array([float(np.any(a[k]!=b[k])) for k in np.array_split(
        np.arange(a.size),TARGET)],dtype=np.float64)

def episodes(source, mode, seeds):
    limit=96
    results=[]
    custody=[]
    for seed in seeds:
        actor=random.Random(1000003*seed+337)
        if mode=="FaramaMiniGridDoorKey8":
            from minigrid.envs.doorkey import DoorKeyEnv
            env=DoorKeyEnv(size=8,render_mode=None)
            obs,_=env.reset(seed=seed)
            first=public(obs["image"],SOURCES[mode][1])
        else:
            from pycolab.examples import apprehend
            from pycolab import rendering
            random.seed(seed)
            env=apprehend.make_game()
            painter=rendering.ObservationCharacterRepainter(
                apprehend.REPAINT_MAPPING)
            obs,_,_=env.its_showtime()
            first=public(painter(obs).board,SOURCES[mode][1])
            if set(first)-{ord(" "),ord("X")}:
                raise ValueError("MR34F_SOURCE_PUBLIC_IDENTITY_NOT_MASKED")
        rows=[]
        full=sha256()
        prev=[np.zeros(INPUT),np.zeros(INPUT)]
        for _ in range(limit):
            action=actor.randrange(SOURCES[mode][2])
            x=current_vector(first,action)
            if mode=="FaramaMiniGridDoorKey8":
                nxt,_,done,truncated,_=env.step(action)
                after=public(nxt["image"],SOURCES[mode][1])
                terminated=bool(done or truncated)
            else:
                nxt,_,discount=env.play(action)
                after=public(painter(nxt).board,SOURCES[mode][1])
                if set(after)-{ord(" "),ord("X")}:
                    raise ValueError("MR34F_ORIGINAL_PUBLIC_NEXT_IDENTITY_LEAK")
                terminated=float(discount)==0.
            y=original_target(first,after)
            full.update(first)
            full.update(bytes([action]))
            full.update(after)
            rows.append((x,np.concatenate([x,prev[1],prev[0]]),y))
            prev=[prev[1],x]
            first=after
            if terminated:
                break
        if hasattr(env,"close"):
            env.close()
        if not rows:
            raise ValueError("MR34F_EMPTY_ORIGINAL_NATIVE_EPISODE")
        results.append(rows)
        custody.append({"source_reset_seed":seed,"original_source_actions":len(rows),
                        "source_public_action_consequence_sha256":full.hexdigest()})
    return results,custody

def sigmoid(z):
    return 1./(1.+np.exp(-np.clip(z,-30.,30.)))

class Logistic:
    def __init__(self,wide,cfg):
        self.dim=INPUT*3 if wide else INPUT
        self.w=np.zeros((self.dim,TARGET))
        self.b=np.zeros(TARGET)
        self.cfg=cfg
        self.wide=wide
        self.train_cpu=0
        self.loss_start=None
        self.loss_end=None

    def features(self,episode):
        return np.array([r[1] if self.wide else r[0] for r in episode])

    def fit(self,ep):
        start=time.process_time_ns()
        xx=np.vstack([self.features(e) for e in ep])
        yy=np.vstack([[z[2] for z in e] for e in ep])
        if self.wide is True and xx.shape[1]!=69:
            raise ValueError("MR34F_HISTORY_INPUT_INVALID")
        n=len(xx)
        for step in range(self.cfg["logistic_epochs"]):
            p=sigmoid(xx@self.w+self.b)
            val=float(np.mean((p-yy)**2))
            if step==0:
                self.loss_start=val
            dw=xx.T@(p-yy)/n+self.cfg["logistic_l2"]*self.w
            db=np.mean(p-yy,axis=0)
            self.w-=self.cfg["logistic_lr"]*dw
            self.b-=self.cfg["logistic_lr"]*db
        self.loss_end=float(np.mean((sigmoid(xx@self.w+self.b)-yy)**2))
        self.train_cpu=time.process_time_ns()-start

    def forecast(self,episode,ablate=False):
        x=self.features(episode)
        if ablate and self.wide:
            x=x.copy()
            x[:,INPUT:]=0.
        return sigmoid(x@self.w+self.b)

    def checkpoint_bytes(self):
        return self.w.nbytes+self.b.nbytes

class Counts:
    def __init__(self,history):
        self.history=history
        self.table=OrderedDict()
        self.global_n=np.zeros(7)
        self.global_sum=np.zeros((7,TARGET))
        self.train_cpu=0

    def key(self,r):
        x,three,_=r
        # All model controls derive from exactly the same public 16-dimensional
        # pooling and original announced action; finite rule keys quantize it.
        key=tuple(int(round(float(v)*4)) for v in x[:16])
        action=int(np.argmax(x[16:]))
        if self.history:
            old=tuple(int(round(float(v)*4)) for v in three[INPUT:])
            key=key+(action,)+old
        else:
            key=key+(action,)
        return key,action

    def fit(self,episodes):
        now=time.process_time_ns()
        for ep in episodes:
            for r in ep:
                key,action=self.key(r)
                if key not in self.table:
                    if len(self.table)>=CONTEXTS:
                        self.table.popitem(last=False)
                    self.table[key]=[0,np.zeros(TARGET)]
                entry=self.table[key]
                entry[0]+=1
                entry[1]+=r[2]
                self.global_n[action]+=1
                self.global_sum[action]+=r[2]
        self.train_cpu=time.process_time_ns()-now

    def forecast(self,episode):
        out=[]
        for r in episode:
            key,action=self.key(r)
            prior=(self.global_sum[action]+1)/(self.global_n[action]+2)
            if key in self.table:
                n,success=self.table[key]
                prior=(success+2*prior)/(n+2)
            out.append(prior)
        return np.array(out)

    def checkpoint_bytes(self):
        # Logical serialized state, not Python heap size.
        payload=[[list(k),n,success.tolist()] for k,(n,success) in self.table.items()]
        return len(canon([payload,self.global_n.tolist(),
                          self.global_sum.tolist()]).encode())

class Recurrent:
    def __init__(self,seed,cfg):
        gen=np.random.RandomState(seed)
        self.wx=gen.normal(0,.08,(INPUT,LATENT))
        self.wh=gen.normal(0,.08,(LATENT,LATENT))
        self.bh=np.zeros(LATENT)
        self.wy=gen.normal(0,.08,(LATENT,TARGET))
        self.by=np.zeros(TARGET)
        self.cfg=cfg
        self.training_cpu=0
        self.train_start=None
        self.train_end=None

    def params(self):
        return [self.wx,self.wh,self.bh,self.wy,self.by]

    def forward(self,ep,ablate=False):
        h=np.zeros(LATENT)
        hidden=[h]
        predictions=[]
        for x,_,y in ep:
            h=np.tanh(x@self.wx+
                      (np.zeros(LATENT) if ablate else h)@self.wh+self.bh)
            predictions.append(sigmoid(h@self.wy+self.by))
            hidden.append(h)
        return np.array(predictions),hidden

    def train_episode(self,ep):
        predictions,hidden=self.forward(ep)
        length=len(ep)
        gx=np.zeros_like(self.wx)
        gh=np.zeros_like(self.wh)
        gb=np.zeros_like(self.bh)
        gy=np.zeros_like(self.wy)
        gby=np.zeros_like(self.by)
        recur=np.zeros(LATENT)
        for t in reversed(range(length)):
            x,_,y=ep[t]
            p=predictions[t]
            err=(p-y)/(length*TARGET)
            gy+=np.outer(hidden[t+1],err)
            gby+=err
            delta=(err@self.wy.T+recur)*(1-hidden[t+1]**2)
            gx+=np.outer(x,delta)
            gh+=np.outer(hidden[t],delta)
            gb+=delta
            recur=delta@self.wh.T
        grads=[gx,gh,gb,gy,gby]
        total=float(np.sqrt(sum(np.sum(g*g) for g in grads)))
        factor=min(1.,self.cfg["recurrent_gradient_clip"]/max(total,1e-12))
        for p,g in zip(self.params(),grads):
            p-=self.cfg["recurrent_lr"]*factor*g

    def fit(self,episodes):
        now=time.process_time_ns()
        self.train_start=float(np.mean([
            np.mean((self.forward(e)[0]-np.vstack([v[2] for v in e]))**2)
            for e in episodes]))
        for _ in range(self.cfg["recurrent_epochs"]):
            for ep in episodes:
                self.train_episode(ep)
        self.train_end=float(np.mean([
            np.mean((self.forward(e)[0]-np.vstack([v[2] for v in e]))**2)
            for e in episodes]))
        self.training_cpu=time.process_time_ns()-now

    def checkpoint_bytes(self):
        return sum(v.nbytes for v in self.params())+LATENT*8

def score(predictions,episodes):
    total=0.
    n=0
    cluster_losses=[]
    for p,ep in zip(predictions,episodes):
        y=np.array([r[2] for r in ep])
        if len(p)!=len(ep):
            raise ValueError("MR34F_OUTCOME_PREDICTION_ALIGNMENT")
        diff=np.mean((p-y)**2,axis=1)
        cluster_losses.append(float(np.mean(diff)))
        total+=float(np.sum(diff))
        n+=len(ep)
    return total/n,cluster_losses

def experiment(mode,roots,p):
    episodes_train,custody_train=episodes(roots[mode],mode,TRAIN)
    episodes_eval,custody_eval=episodes(roots[mode],mode,EVAL)
    cfg=p["common_learning_and_regularization"]
    mem=Logistic(False,cfg)
    history=Logistic(True,cfg)
    bayesian=Counts(False)
    symbolic=Counts(True)
    mem.fit(episodes_train)
    history.fit(episodes_train)
    bayesian.fit(episodes_train)
    symbolic.fit(episodes_train)
    # Exact training-score choice only; never consult evaluation outcomes for
    # recurrence restart selection or learning budget adjustment.
    trained=[]
    for seed in cfg["recurrent_init_seeds"]:
        m=Recurrent(seed,cfg)
        m.fit(episodes_train)
        trained.append((m.train_end,seed,m))
    _,selected_seed,recur=min(trained,key=lambda x:(x[0],x[1]))
    training_complete=time.process_time_ns()
    models={
        "fully_fitted_memoryless":(mem,lambda ep:mem.forecast(ep)),
        "fully_fitted_two_step_history":(history,lambda ep:history.forecast(ep)),
        "history_same_weights_zeroed":(history,lambda ep:history.forecast(ep,True)),
        "fully_fitted_bayesian_counts":(bayesian,lambda ep:bayesian.forecast(ep)),
        "fully_fitted_symbolic_history_rules":(symbolic,lambda ep:symbolic.forecast(ep)),
        "fully_trained_eight_state_recurrent":(recur,lambda ep:recur.forward(ep)[0]),
        "recurrent_same_weights_state_zeroed":(recur,lambda ep:recur.forward(ep,True)[0])
    }
    estimates={}
    by_seed={}
    total_inference_cpu={}
    for key,(model,fn) in models.items():
        time_start=time.process_time_ns()
        preds=[fn(ep) for ep in episodes_eval]
        total_inference_cpu[key]=time.process_time_ns()-time_start
        mean,losses=score(preds,episodes_eval)
        estimates[key]=mean
        by_seed[key]=losses
    memoryless=by_seed["fully_fitted_memoryless"]
    historyloss=by_seed["fully_fitted_two_step_history"]
    ablated=by_seed["history_same_weights_zeroed"]
    recurrence=by_seed["fully_trained_eight_state_recurrent"]
    count=sum(h<m for h,m in zip(historyloss,memoryless))
    conditional=(estimates["fully_fitted_two_step_history"]<=
                   estimates["history_same_weights_zeroed"])
    return {
        "source_family":mode,
        "original_source_git_sha":SOURCES[mode][0],
        "original_episode_train_receipts":custody_train,
        "original_episode_held_development_receipts":custody_eval,
        "independent_train_reset_seeds":len(episodes_train),
        "independent_held_development_reset_seeds":len(episodes_eval),
        "authentic_original_training_actions":sum(len(e) for e in episodes_train),
        "authentic_original_evaluation_actions":sum(len(e) for e in episodes_eval),
        "original_training_action_public_digest":sha(canon(custody_train).encode()),
        "original_evaluation_action_public_digest":sha(canon(custody_eval).encode()),
        "fully_fitted_prospective_mean_8bit_brier_lower_better":estimates,
        "source_independent_eval_seed_brier":{
            str(seed):{key:by_seed[key][i] for key in by_seed}
            for i,seed in enumerate(EVAL)},
        "history_beats_memoryless_independent_seeds":count,
        "history_beats_same_weights_history_ablation":conditional,
        "native_train_CPU_ns_by_model":{
            "memoryless":mem.train_cpu,"history":history.train_cpu,
            "bayesian":bayesian.train_cpu,"symbolic":symbolic.train_cpu,
            "recurrent_all_frozen_initializations":sum(m.training_cpu for _,_,m in trained)},
        "native_inference_CPU_ns_by_model":total_inference_cpu,
        "serialized_checkpoint_bytes_by_model":{
            "memoryless":mem.checkpoint_bytes(),
            "history":history.checkpoint_bytes(),
            "bayesian":bayesian.checkpoint_bytes(),
            "symbolic":symbolic.checkpoint_bytes(),
            "recurrent":recur.checkpoint_bytes()},
        "recurrent_training_only_model_selection_seed":selected_seed,
        "recurrent_init_development_train_brier":{
            str(seed):loss for loss,seed,_ in trained},
        "regularized_logistic_initial_final_training_loss":{
            "memoryless":[mem.loss_start,mem.loss_end],
            "history":[history.loss_start,history.loss_end]},
        "recurrent_latent_frozen_capacity":LATENT,
        "in_process_recurrent_hidden_state_read_proxy_bytes":
            sum(len(ep) for ep in episodes_eval)*LATENT*8,
        "no_original_source_labels_or_rewards_supplied_to_predictors":True,
        "no_eval_training_or_eval_based_model_selection":True
    }

def peak_rss():
    if sys.platform=="win32":
        v=getattr(psutil.Process().memory_info(),"peak_wset",0)
        if not v:raise ValueError("MR34F_WINDOWS_PEAK_RSS_MISSING")
        return int(v)
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    raise ValueError("MR34F_RESOURCE_UNSUPPORTED_OS")

def main(original_farama,original_pycolab):
    p=frozen()
    roots={
        "FaramaMiniGridDoorKey8":verify_source(original_farama,SOURCES["FaramaMiniGridDoorKey8"][0]),
        "DeepMindPycolabApprehend":verify_source(original_pycolab,SOURCES["DeepMindPycolabApprehend"][0])
    }
    sys.path.insert(0,str(roots["FaramaMiniGridDoorKey8"]))
    sys.path.insert(0,str(roots["DeepMindPycolabApprehend"]))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    start=time.process_time_ns()
    outcome={name:experiment(name,roots,p) for name in SOURCES}
    go=True
    for res in outcome.values():
        m=res["fully_fitted_prospective_mean_8bit_brier_lower_better"]
        go=go and (
          m["fully_fitted_two_step_history"]+0.002<=m["fully_fitted_memoryless"]
          and res["history_beats_memoryless_independent_seeds"]>=7
          and m["fully_fitted_two_step_history"]<m["history_same_weights_zeroed"]
          and m["fully_trained_eight_state_recurrent"]<=m["fully_fitted_memoryless"])
    for name,root in roots.items():
        verify_source(root,SOURCES[name][0])
    print("MR34F_ORIGINAL_PROSPECTIVE_PUBLIC_HISTORY_CONTROLS="+canon({
        "exact_frozen_precode_protocol_sha256":sha(FROZEN.read_bytes()),
        "independently_authored_original_source_results":outcome,
        "precommitted_development_history_information_GO":bool(go),
        "native_original_source_and_all_model_CPU_ns":time.process_time_ns()-start,
        "whole_original_sources_training_evaluation_OS_peak_RSS_bytes":peak_rss(),
        "physical_interprocessor_communication":"NONE_ALL_IN_PROCESS",
        "model_checkpoint_wire_bytes_accounted_separately":True,
        "model_capacity_resource_parity":"NOT_ESTABLISHED",
        "original_source_public_feature_input_dim":INPUT,
        "all_competitors_same_public_sensor_and_action_information":True,
        "same_full_trajectory_training_data":True,
        "protected_scientific_first_use_consumed":False,
        "new_native_yggdrasil_cognitive_model_trained":False,
        "observational_prediction_not_causal_identification":True,
        "preregistered_development_only_no_independent_transfer":True,
        "G29_source_bound_atlas_and_full_regression":"BLOCKED",
        "scientific_admission":"NO_GO"
    }))

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.mr34f.prospective_controls ORIGINAL_FARAMA ORIGINAL_PYCOLAB")
    main(sys.argv[1],sys.argv[2])

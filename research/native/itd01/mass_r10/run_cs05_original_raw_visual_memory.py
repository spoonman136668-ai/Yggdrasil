#!/usr/bin/env python3
"""CS05: learn public encoded-image PCA cue latent, reward-trained fork action.

No private MiniGrid data used. Navigation is publicly scripted, not learned.
PCA is a conventional FIT-learned representation, not native Yggdrasil cognition.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import math
import resource
import subprocess
import time

PIN="7f5853792ea7f04f75614661006d87fcf949f26d"
FIRST="bedf61501057c2bb0f3e6ab367704039352362a9"
BLOBS={
 "minigrid/envs/memory.py":"660b0a1b769948034c87bb421759c2b9a4f24548",
 "minigrid/minigrid_env.py":"eb29e9a902de0715ab77ec981a2113576d7664fa",
 "minigrid/__init__.py":"41b4a731255d19bdf61072b7100e752a759a3ae4",
 "pyproject.toml":"61ab88372ca553af255a42564260994be808ac12"}
ROLE_COUNTS={"FIT":192,"VALID":64,"DEV":128}
REPS=(0,1,2)
CANDIDATE="fit_pca_scalar_memory_logistic"
EPISODIC="trained_raw_pair_reward_table"
FRAME="trained_fork_frame_only"
ERASED="pca_scalar_memory_erased"
FIXED="fixed_upper"
ARMS=(CANDIDATE,EPISODIC,FRAME,ERASED,FIXED)
PASSES=80
ETA=.08
L2=.003

def guard(ok,why):
    if not ok:
        raise RuntimeError(why)
def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def digest(v):
    return hashlib.sha256(canonical(v).encode()).hexdigest()
def seed(role,r,i):
    return {"FIT":980000,"VALID":990000,"DEV":1000000}[role]+1000*r+i
def original_identity(path):
    root=Path(path).resolve()
    def call(args):
        a=subprocess.run(args,cwd=root,text=True,capture_output=True,timeout=25)
        return a.returncode,a.stdout.strip()
    rc,h=call(["git","rev-parse","HEAD"])
    guard(rc==0 and h==PIN,"ORIGINAL_SOURCE_HEAD_DRIFT")
    for path,sha in BLOBS.items():
        rc,actual=call(["git","hash-object","--",path])
        guard(rc==0 and actual==sha,"ORIGINAL_SOURCE_BLOB_DRIFT:"+path)
    rc,_=call(["git","diff","--exit-code","--","minigrid","pyproject.toml"])
    guard(rc==0,"ORIGINAL_SOURCE_TRACKED_DIFF")
    return {"git_sha":PIN,"pinned_blobs":BLOBS}
def image(obs):
    """Raw original public encoded 7x7x3 image; not a semantic cue label."""
    import numpy as np
    guard(isinstance(obs,dict) and "image" in obs and "direction" in obs
          and "mission" in obs,"ORIGINAL_OBS_SCHEMA_INVALID")
    a=obs["image"]
    guard(a.shape==(7,7,3) and np.issubdtype(a.dtype,np.integer),
          "ORIGINAL_ENCODED_IMAGE_INVALID")
    return a.reshape(147).astype(np.uint8).tolist()
def front_is_wall(obs):
    from minigrid.core.constants import OBJECT_TO_IDX
    guard(obs["image"].shape==(7,7,3),"PUBLIC_NAV_VIEW_SHAPE")
    return int(obs["image"][3,5,0])==OBJECT_TO_IDX["wall"]
def navigate(env,initial):
    """Only public MiniGrid observations guide the common nonlearning route."""
    from minigrid.core.actions import Actions
    obs=initial
    guard(int(obs["direction"])==0 and obs["image"].shape==(7,7,3),
          "ORIGINAL_START_PUBLIC_ORIENTATION")
    steps=0
    def step(a):
        nonlocal obs,steps
        guard(a in (Actions.left,Actions.right,Actions.forward),
              "ILLEGAL_ORIGINAL_NAV_ACTION")
        obs,reward,terminated,truncated,info=env.step(a)
        steps+=1
        guard(not terminated and not truncated and float(reward)==0.0 and
              isinstance(info,dict),"EARLY_PUBLIC_NAV_STOP")
    step(Actions.left)
    step(Actions.left)
    guard(int(obs["direction"])==2,"WEST_NAV_ORIENTATION")
    west=0
    while not front_is_wall(obs):
        guard(west<11,"WEST_BOUND_NOT_PUBLICLY_REACHABLE")
        step(Actions.forward)
        west+=1
    step(Actions.right)
    guard(int(obs["direction"])==3,"CUE_VIEW_ORIENTATION")
    cue_raw=image(obs)
    step(Actions.right)
    east=0
    while not front_is_wall(obs):
        guard(east<12,"FORK_BOUND_NOT_PUBLICLY_REACHABLE")
        step(Actions.forward)
        east+=1
    step(Actions.left)
    guard(int(obs["direction"])==3 and steps<=32,
          "PUBLIC_FORK_ORIENTATION_OR_BUDGET_INVALID")
    fork_raw=image(obs)
    return cue_raw,fork_raw,steps
def source_episode(seed_value,chooser):
    from minigrid.envs.memory import MemoryEnv
    from minigrid.core.actions import Actions
    env=MemoryEnv(size=13,random_length=False,agent_view_size=7,render_mode=None)
    try:
        o,info=env.reset(seed=seed_value)
        guard(isinstance(info,dict),"ORIGINAL_SOURCE_RESET_INFO")
        cue,fork,n=navigate(env,o)
        # Full raw encoded images are inputs; no manually extracted cue type.
        action=chooser(cue,fork)
        guard(type(action) is int and action in (0,1),"INVALID_PUBLIC_FORK_ACTION")
        if action:
            for _ in range(2):
                o,r,t,trunc,info=env.step(Actions.left)
                n+=1
                guard(not t and not trunc and float(r)==0.,
                      "UNEXPECTED_LOWER_TURN_TERMINAL")
        o,r,t,trunc,info=env.step(Actions.forward)
        n+=1
        guard(t and not trunc and isinstance(info,dict),"SOURCE_FORK_NOT_TERMINAL")
        return {"seed":seed_value,"cue_image":cue,"fork_image":fork,
                "chosen_lower":action,"terminal_success":int(float(r)>0),
                "source_reward":float(r),"legal_steps":n}
    finally:
        env.close()
class RankOneEncoder:
    """FIT-only unlabeled raw-image SVD rank-one; no cue categories or labels."""
    def __init__(self):
        self.mean=None;self.direction=None;self.scale=None
        self.explained=None
    def fit(self,images):
        import numpy as np
        x=np.asarray(images,dtype=np.float64)
        guard(x.shape[0]>=32 and x.shape[1]==147,"ENCODER_PUBLIC_TRAIN_SHAPE")
        mu=x.mean(axis=0)
        centered=x-mu
        _,sigma,vt=np.linalg.svd(centered,full_matrices=False)
        guard(sigma[0]>1e-8,"ORIGINAL_SOURCE_RAW_IMAGE_NO_VARIANCE")
        direction=vt[0]
        j=int(np.argmax(np.abs(direction)))
        if direction[j]<0:
            direction=-direction
        projections=centered@direction
        scale=float(np.max(np.abs(projections)))
        guard(scale>1e-10,"FIT_ENCODER_COLLAPSE")
        total=float((sigma*sigma).sum())
        self.mean=mu.tolist()
        self.direction=direction.tolist()
        self.scale=scale
        self.explained=float(sigma[0]**2/total)
    def project(self,image_values):
        import numpy as np
        guard(self.mean is not None,"ENCODER_UNFITTED")
        inp=np.asarray(image_values,dtype=np.float64)
        guard(inp.shape==(147,),"SCORE_RAW_IMAGE_INVALID")
        return float(np.dot(inp-np.asarray(self.mean),
                            np.asarray(self.direction))/self.scale)
    def state(self):
        return {"algorithm":"unsupervised_FIT_only_rank1_PCA","mean":self.mean,
                "direction":self.direction,"scale":self.scale,
                "explained_FIT_variance":self.explained}
class PcaReward:
    def __init__(self):
        self.cue=RankOneEncoder()
        self.fork=RankOneEncoder()
        self.w=[0.0]*8
        self.updates=0
    @staticmethod
    def vec(c,f,a):
        return (1,c,f,a,c*f,c*a,f*a,c*f*a)
    def probability(self,c,f,a):
        z=sum(w*v for w,v in zip(self.w,self.vec(c,f,a)))
        return 1/(1+math.exp(-max(-30.,min(30.,z))))
    def fit(self,rows):
        self.cue.fit([r["cue_image"] for r in rows])
        self.fork.fit([r["fork_image"] for r in rows])
        tuples=[(self.cue.project(r["cue_image"]),
                 self.fork.project(r["fork_image"]),
                 r["chosen_lower"],r["terminal_success"]) for r in rows]
        for _ in range(PASSES):
            for c,f,a,y in tuples:
                x=self.vec(c,f,a)
                p=self.probability(c,f,a)
                for i,entry in enumerate(x):
                    self.w[i]+=ETA*((y-p)*entry-L2*self.w[i])
                self.updates+=1
        guard(self.updates==len(rows)*PASSES,"REWARD_LEARNING_BUDGET")
        guard(any(abs(q)>1e-8 for q in self.w),"REWARD_WEIGHTS_UNTRAINED")
    def choose(self,cue,fork,erase=False):
        c=0.0 if erase else self.cue.project(cue)
        f=self.fork.project(fork)
        return int(self.probability(c,f,1)>self.probability(c,f,0))
    def state(self):
        return {"cue_encoder":self.cue.state(),"fork_encoder":self.fork.state(),
                "weights":self.w,"reward_updates":self.updates,
                "epochs":PASSES,"eta":ETA,"l2":L2}
class RawEpisodic:
    def __init__(self,frame_only=False):
        self.frame_only=frame_only
        self.cells=defaultdict(lambda:[1,1])
        self.updates=0
    def key(self,cue,fork,action):
        # True exact raw encoded-image bytes; no key/ball type encoder.
        return (bytes(fork) if self.frame_only else bytes(cue)+bytes(fork))+bytes([action])
    def fit(self,rows):
        for r in rows:
            self.cells[self.key(r["cue_image"],r["fork_image"],r["chosen_lower"])][r["terminal_success"]]+=1
            self.updates+=1
        guard(self.updates==len(rows),"RAW_EPISODIC_NOT_FITTED")
    def choose(self,cue,fork):
        q=lambda a:self.cells[self.key(cue,fork,a)][1]/sum(self.cells[self.key(cue,fork,a)])
        return int(q(1)>q(0))
    def state(self):
        return {"method":"trained_current_image_raw_table" if self.frame_only else "trained_raw_cue_and_fork_episodic_table",
                "rows":[[key.hex(),v] for key,v in sorted(self.cells.items())],
                "updates":self.updates}
class PcaErased:
    def __init__(self,parent):
        self.parent=parent
    def choose(self,cue,fork):
        return self.parent.choose(cue,fork,erase=True)
    def state(self):
        return {"method":"inference_cue_projection_erased_to_zero","parent":self.parent.state()}
class Fixed:
    def choose(self,cue,fork):return 0
    def state(self):return {"method":"fixed_upper","updates":0}
def train(rows):
    parent=PcaReward()
    raw=RawEpisodic()
    frame=RawEpisodic(frame_only=True)
    models={CANDIDATE:parent,EPISODIC:raw,FRAME:frame}
    train_receipts={}
    for name,m in models.items():
        start=time.process_time_ns()
        m.fit(rows)
        train_receipts[name]={"updates":m.updates,
                              "fit_cpu_ns":time.process_time_ns()-start,
                              "serialized_state_bytes":len(canonical(m.state()).encode()),
                              "trained_model_sha256":digest(m.state())}
    models[ERASED]=PcaErased(parent)
    models[FIXED]=Fixed()
    for name in (ERASED,FIXED):
        train_receipts[name]={"updates":0,"fit_cpu_ns":0,
                              "serialized_state_bytes":len(canonical(models[name].state()).encode()),
                              "trained_model_sha256":digest(models[name].state())}
    return models,train_receipts
def scored(role,r,models):
    size=ROLE_COUNTS[role]
    frozen={name:digest(m.state()) for name,m in models.items()}
    output={}
    for name in ARMS:
        successes=0;steps=0;rewards=0.;cpu=0
        trace=hashlib.sha256()
        for i in range(size):
            start=time.process_time_ns()
            row=source_episode(seed(role,r,i),models[name].choose)
            cpu+=time.process_time_ns()-start
            successes+=row["terminal_success"]
            rewards+=row["source_reward"]
            steps+=row["legal_steps"]
            # hashed complete original raw image trace, without retaining all scored roles
            trace.update((canonical(row)+"\n").encode())
        output[name]={"episodes":size,"successes":successes,
                       "success_rate":successes/size,
                       "legal_source_steps":steps,
                       "source_shaped_reward_sum":rewards,
                       "evaluation_cpu_ns_with_original_environment":cpu,
                       "public_trace_sha256":trace.hexdigest()}
    guard(frozen=={name:digest(m.state()) for name,m in models.items()},
          "VALID_DEV_MODEL_FIT_MUTATION")
    return output
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    root=Path(args.upstream).resolve()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs05.public_minigrid_raw_encoded_visual_memory.v1",
        "first_prereg_sha":FIRST,"original_git_source":PIN,
        "source_role":"PUBLIC_DEVELOPMENT_ONLY",
        "raw_observation_is_original_categorical_7x7x3_not_RGB":True,
        "preprocessing_is_fixed_public_navigation_not_learned":True,
        "semantic_cue_type_labels_available_to_trained_models":False,
        "latent_memory_is_one_fit_learned_PCA_scalar":True,
        "encoder_training_is_unlabeled_not_reward_end_to_end":True,
        "native_yggdrasil_or_wingless_cognitive_learner_executed":False,
        "independent_sealed_unfamiliar_first_use":False,
        "protected_test_consumed":False,
        "controller_science_admission_observed":False,
        "model_resource_parity_qualified":False,
        "disposition":"PUBLIC_CS05_INVALID_SOURCE_OR_TRAINING",
        "replicas":[]}
    raw={"schema":"mass.cs05.frozen_shared_public_FIT.v1","replicas":[]}
    try:
        receipt["upstream_original_source_verified"]=original_identity(root)
        from minigrid.envs.memory import MemoryEnv
        import inspect
        guard(Path(inspect.getfile(MemoryEnv)).resolve()==root/"minigrid"/"envs"/"memory.py",
              "NOT_ORIGINAL_MINIGRID_CLASS")
        seen=set()
        for r in REPS:
            fit=[]
            for i in range(ROLE_COUNTS["FIT"]):
                s=seed("FIT",r,i)
                guard(s not in seen,"SEED_ROLE_OVERLAP")
                seen.add(s)
                action=i%2
                row=source_episode(s,lambda cue,fork,a=action:a)
                guard(row["chosen_lower"]==action,"PUBLIC_FIT_EXPLORATION_DRIFT")
                fit.append(row)
            # Group purely by exact ORIGINAL PUBLIC IMAGE bytes. No semantic label.
            groups=defaultdict(int)
            cues=set();forks=set()
            for x in fit:
                c=bytes(x["cue_image"]);f=bytes(x["fork_image"])
                cues.add(c);forks.add(f)
                groups[(c,f,x["chosen_lower"])]+=1
            guard(len(cues)==2 and len(forks)==2 and len(groups)==8 and
                  min(groups.values())>=3,"FROZEN_RAW_PUBLIC_FIT_SUPPORT_NO_GO")
            raw["replicas"].append({"replica":r,"original_public_fit_rows":fit})
            models,fit_receipt=train(fit)
            guard(models[CANDIDATE].cue.explained>.5 and models[CANDIDATE].fork.explained>.5,
                  "UNLABELED_ENCODER_DID_NOT_EXTRACT_SOURCE_VARIANCE")
            original_state={name:digest(m.state()) for name,m in models.items()}
            valid=scored("VALID",r,models)
            dev=scored("DEV",r,models)
            guard(original_state=={name:digest(m.state()) for name,m in models.items()},
                  "MODEL_UPDATED_AFTER_FIT")
            for role in ("VALID","DEV"):
                for i in range(ROLE_COUNTS[role]):
                    ss=seed(role,r,i)
                    guard(ss not in seen,"VALID_DEV_SOURCE_SEED_OVERLAP")
                    seen.add(ss)
            srate=lambda name:dev[name]["success_rate"]
            decision=(srate(CANDIDATE)>=.9 and srate(EPISODIC)>=.9
                      and srate(CANDIDATE)-srate(FRAME)>=.2
                      and srate(CANDIDATE)-srate(ERASED)>=.2)
            receipt["replicas"].append({
                "replica":r,"public_fit_original_episodes":len(fit),
                "public_fit_original_steps":sum(x["legal_steps"] for x in fit),
                "public_FIT_original_raw_image_sha256":digest(fit),
                "distinct_original_public_cue_encoded_images":len(cues),
                "distinct_original_public_fork_encoded_images":len(forks),
                "eight_raw_context_action_group_counts":sorted(groups.values()),
                "model_fit_training":fit_receipt,
                "unlabeled_original_PCA_cue_variance_explained":models[CANDIDATE].cue.explained,
                "unlabeled_original_PCA_fork_variance_explained":models[CANDIDATE].fork.explained,
                "valid":valid,"dev":dev,
                "candidate_minus_current_frame_pp":100*(srate(CANDIDATE)-srate(FRAME)),
                "candidate_minus_cue_latent_erased_pp":100*(srate(CANDIDATE)-srate(ERASED)),
                "candidate_minus_conventional_raw_episodic_pp":100*(srate(CANDIDATE)-srate(EPISODIC)),
                "predeclared_memory_use_criterion_passed":decision,
                "process_inclusive_peak_rss_kib_not_isolated_models":
                   resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
            print("CS05_REPLICA="+str(r)+" DEV_CORRECT="+canonical({
                name:dev[name]["successes"] for name in ARMS}),flush=True)
        guard(len(seen)==3*(192+64+128),"TOTAL_ROLE_SEEDS_DRIFT")
        receipt["source_original_public_episodes"]=3*(192+5*(64+128))
        receipt["source_original_public_legal_steps"]=sum(
           sum(x["legal_steps"] for x in rr["original_public_fit_rows"])
           for rr in raw["replicas"])+sum(
               sum(v["legal_source_steps"] for v in rep[role].values())
               for rep in receipt["replicas"] for role in ("valid","dev"))
        receipt["full_original_public_FIT_sha256"]=digest(raw)
        receipt["disposition"]=(
            "PUBLIC_CS05_LEARNED_ENCODED_VISUAL_CUE_USE" if all(
                r["predeclared_memory_use_criterion_passed"] for r in receipt["replicas"])
            else "PUBLIC_CS05_NO_REPRODUCIBLE_VISUAL_MEMORY_GAIN")
        receipt["novel_architecture_advantage"]="NOT_ESTABLISHED_NO_NATIVE_MODEL"
        receipt["cross_family_unfamiliar_transfer"]="NOT_TESTED"
    except Exception as exc:
        receipt["failure"]=type(exc).__name__+":"+str(exc)[:700]
    finally:
        (out/"cs05-original-public-fit.json").write_text(canonical(raw)+"\n")
        (out/"cs05-source-native-receipt.json").write_text(
            json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("CS05_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS05_INVALID_SOURCE_OR_TRAINING" else 0

if __name__=="__main__":
    import sys
    raise SystemExit(main())

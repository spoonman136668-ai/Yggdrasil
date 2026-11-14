"""DG1-MG19: external MiniGrid action-consequence research, NOT a native model.
Frozen preregistration precedes this file. Registered seeds are first-use only.
"""
import hashlib
import json
import math
import platform
import random
import statistics
import sys
import time
import zlib

FREEZE = "f9c531011f36d3a9150397f462a681f094657b28"
PARENT = "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9"
MANIFEST_HASH = "e8b825254d1b7e90fe9c4eb6f12643f87066d50e1ee04970ca14a1fbd0400184"
SCHEMA = "yggdrasil.dg1-mg19-original.v1"
ARMS = ("episodic_history","shuffled_history","memoryless_sgd","recurrent_sgd","persistence")
TRAIN_SEEDS = tuple(range(630001,630013))
INTERFERENCE_SEEDS = tuple(range(640001,640013))
COLD_SEEDS = tuple(range(650001,650013))
TRANSFER_SEEDS = tuple(range(660001,660013))
LARGER_SEEDS = tuple(range(670001,670013))
TRAIN_ENVS = ("MiniGrid-DoorKey-5x5-v0","MiniGrid-DoorKey-6x6-v0")
INTERFERENCE_ENV = "MiniGrid-Dynamic-Obstacles-6x6-v0"
COLD_ENV = "MiniGrid-DoorKey-6x6-v0"
TRANSFER_ENV = "MiniGrid-UnlockPickup-v0"
LARGER_ENV = "MiniGrid-DoorKey-8x8-v0"
HORIZON = 12
MAX_STEPS = 128
HISTORY = 8
CAPACITY = 256
DIMS = 12
OUT = 8


def canon(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)


def digest(obj):
    return hashlib.sha256(canon(obj).encode()).hexdigest()


def manifest():
    return {
        "schema":"yggdrasil.dg1-mg19-episode-plan.v1",
        "horizon":HORIZON,"max_steps":MAX_STEPS,
        "train_seeds":list(TRAIN_SEEDS),
        "interference_seeds":list(INTERFERENCE_SEEDS),
        "cold_seeds":list(COLD_SEEDS),
        "transfer_seeds":list(TRANSFER_SEEDS),
        "larger_seeds":list(LARGER_SEEDS),
        "train_envs":list(TRAIN_ENVS),
        "interference_env":INTERFERENCE_ENV,
        "cold_env":COLD_ENV,
        "transfer_env":TRANSFER_ENV,
        "larger_env":LARGER_ENV,
        "arms":list(ARMS)
    }


def require_manifest():
    if digest(manifest())!=MANIFEST_HASH:
        raise AssertionError("MG19_FROZEN_MANIFEST_DRIFT")


def clamp(v,lo=0.,hi=1.):
    return max(lo,min(hi,v))


def image_features(obs):
    """Only public partial image pixels, not env.unwrapped state or mission text."""
    from minigrid.core.constants import OBJECT_TO_IDX
    image=obs["image"]
    obj=image[:,:,0]
    st=image[:,:,2]
    n=float(obj.size)
    fields=("wall","door","key","goal","empty","box")
    counts={k:int((obj==OBJECT_TO_IDX[k]).sum()) for k in fields}
    open_doors=int(((obj==OBJECT_TO_IDX["door"]) & (st==0)).sum())
    return tuple(round(counts[k]/n,8) for k in ("wall","door","key","goal","empty")) + (
        round(open_doors/n,8),round(counts["box"]/n,8))


def encoded(obs,prev_action):
    direction=int(obs["direction"])
    if direction not in range(4) or type(prev_action) is not int or prev_action not in range(7):
        raise ValueError("MG19_INVALID_PUBLIC_OBSERVATION")
    im=image_features(obs)
    return im+tuple(float(int(direction==i)) for i in range(4))+(round(prev_action/6,8),)


def policy(obs,step,rng,n):
    """Fixed policy reads only supplied partial view and its own seeded RNG."""
    from minigrid.core.constants import OBJECT_TO_IDX
    if n < 3:
        raise ValueError("MG19_BAD_ACTION_SPACE")
    front=int(obs["image"][3,5,0])
    if n>3 and front in (OBJECT_TO_IDX["key"],OBJECT_TO_IDX["box"]):
        return 3
    if n>5 and front==OBJECT_TO_IDX["door"] and step%5==0:
        return 5
    if front in (OBJECT_TO_IDX["wall"],OBJECT_TO_IDX["unseen"]):
        return rng.choice((0,1))
    r=rng.random()
    return 2 if r<.58 else (0 if r<.79 else 1)


def collect(env_name,seed):
    """Actually pay every Gymnasium env.step, once for a shared five-arm trace."""
    import gymnasium as gym
    import minigrid  # noqa: F401 - registers MiniGrid environments
    env=gym.make(env_name)
    try:
        obs,_=env.reset(seed=seed)
        rng=random.Random(seed^0x7B19)
        observations=[obs]
        actions=[]
        rewards=[]
        h=hashlib.sha256()
        h.update(env_name.encode())
        h.update(str(seed).encode())
        for t in range(MAX_STEPS):
            action=policy(obs,t,rng,env.action_space.n)
            next_obs,reward,terminated,truncated,_=env.step(action)
            actions.append(int(action))
            rewards.append(float(reward))
            observations.append(next_obs)
            pixels=next_obs["image"].tobytes()
            h.update(bytes([action,int(next_obs["direction"])]))
            h.update(len(pixels).to_bytes(4,"little"))
            h.update(pixels)
            h.update(f"{reward:.8f}".encode())
            obs=next_obs
            if terminated or truncated:
                break
    finally:
        env.close()
    rows=[]
    for t in range(max(0,len(actions)-HORIZON+1)):
        vectors=[encoded(observations[i],actions[i-1] if i>0 else 6)
                 for i in range(max(0,t-HISTORY+1),t+1)]
        target=tuple(image_features(observations[t+HORIZON]))+(
            float(any(r>0 for r in rewards[t:t+HORIZON])),)
        base=image_features(observations[t])
        changed=any(base[i]!=target[i] for i in range(7))
        rows.append((vectors,target,changed))
    return {"env":env_name,"seed":seed,"steps":len(actions),
            "trajectory_sha256":h.hexdigest(),
            "rewarded_steps":sum(r>0 for r in rewards),
            "rows":rows}


def context(seq,shuffled=False):
    if not seq or len(seq[-1])!=DIMS:
        raise ValueError("MG19_INVALID_SEQUENCE")
    cur=seq[-1]
    older=seq[-HISTORY:-1]
    mean=tuple(round(sum(x[j] for x in older)/len(older),6)
               if older else cur[j] for j in range(DIMS))
    if shuffled:
        # Independently synthesized junk context derived only from present image.
        seed=int(hashlib.sha256(canon(cur).encode()).hexdigest()[:12],16)
        r=random.Random(seed)
        mean=tuple(round(r.random(),6) for _ in range(DIMS))
    return tuple(cur)+mean


def mse(pred,target):
    return sum((a-b)**2 for a,b in zip(pred,target))/OUT


class Episodic:
    def __init__(self,kind):
        self.kind=kind
        self.slots=[]
        self.seen=0
        self.rng=random.Random(31911)
        self.first_sample_count=0

    def predict(self,seq):
        if not self.slots:
            return persistence(seq)
        x=context(seq,self.kind=="shuffled_history")
        distances=[]
        for i,(v,y,stage) in enumerate(self.slots):
            distance=sum(abs(a-b) for a,b in zip(v,x))
            distances.append((distance,i))
        matches=sorted(distances)[:8]
        coeff=[1/(.05+d) for d,_ in matches]
        denom=sum(coeff)
        return tuple(clamp(round(sum(c*self.slots[idx][1][j]
                    for c,(_,idx) in zip(coeff,matches))/denom,8))
                    for j in range(OUT))

    def learn(self,seq,target,stage):
        key=context(seq,self.kind=="shuffled_history")
        y=tuple(round(float(v),8) for v in target)
        item=(key,y,stage)
        self.seen+=1
        if len(self.slots)<CAPACITY:
            self.slots.append(item)
        else:
            index=self.rng.randrange(self.seen)
            if index<CAPACITY:
                self.slots[index]=item

    def dump(self):
        return {"kind":self.kind,"seen":self.seen,"slots":self.slots,
                "first_sample_count":self.first_sample_count,
                "rng":list(self.rng.getstate()[1])}

    def load(self,data):
        self.seen=data["seen"]
        self.first_sample_count=data["first_sample_count"]
        self.slots=[(tuple(x),tuple(y),stage) for x,y,stage in data["slots"]]
        self.rng.setstate((3,tuple(data["rng"]),None))

    def retained(self):
        return sum(stage=="train" for _,_,stage in self.slots)


class SGD:
    def __init__(self):
        self.kind="memoryless_sgd"
        r=random.Random(99211)
        self.w=[[round(r.uniform(-.01,.01),8) for _ in range(DIMS)]
                for _ in range(OUT)]
        self.b=[0.]*OUT
        self.count=0

    def predict(self,seq):
        x=seq[-1]
        return tuple(clamp(round(sum(a*b for a,b in zip(w,x))+self.b[j],8))
                     for j,w in enumerate(self.w))

    def learn(self,seq,target,stage):
        x=seq[-1]
        pred=self.predict(seq)
        rate=.05
        for j in range(OUT):
            err=pred[j]-target[j]
            for i in range(DIMS):
                self.w[j][i]=round(clamp(self.w[j][i]-rate*err*x[i],-2,2),8)
            self.b[j]=round(clamp(self.b[j]-rate*err,-2,2),8)
        self.count+=1

    def dump(self):
        return {"kind":self.kind,"w":self.w,"b":self.b,"count":self.count}

    def load(self,data):
        self.w=data["w"];self.b=data["b"];self.count=data["count"]


class Recurrent:
    """8-cell fully trained conventional clipped-linear RNN; eight-step BPTT."""
    def __init__(self):
        self.kind="recurrent_sgd"
        r=random.Random(74211)
        self.wx=[[round(r.uniform(-.06,.06),8) for _ in range(DIMS)]
                 for _ in range(8)]
        self.wh=[[round(r.uniform(-.04,.04),8) for _ in range(8)]
                 for _ in range(8)]
        self.v=[[round(r.uniform(-.06,.06),8) for _ in range(8)]
                for _ in range(OUT)]
        self.b=[0.]*8
        self.c=[0.]*OUT
        self.count=0

    def forward(self,seq):
        seq=[seq[0]]*max(0,HISTORY-len(seq))+list(seq[-HISTORY:])
        h=[0.]*8
        tapes=[]
        for x in seq:
            prev=h[:]
            z=[sum(a*b for a,b in zip(self.wx[i],x))+
               sum(a*b for a,b in zip(self.wh[i],prev))+self.b[i]
               for i in range(8)]
            h=[clamp(v,-1,1) for v in z]
            tapes.append((x,prev,z,h[:]))
        y=[sum(a*b for a,b in zip(self.v[j],h))+self.c[j]
           for j in range(OUT)]
        return y,tapes

    def predict(self,seq):
        raw,_=self.forward(seq)
        return tuple(round(clamp(v),8) for v in raw)

    def learn(self,seq,target,stage):
        raw,tapes=self.forward(seq)
        y=[clamp(v) for v in raw]
        # All weights train: output, input, recurrent, hidden and output biases.
        e=[(y[j]-target[j])/OUT for j in range(OUT)]
        dh=[sum(self.v[j][i]*e[j] for j in range(OUT)) for i in range(8)]
        gx=[[0.]*DIMS for _ in range(8)]
        gh=[[0.]*8 for _ in range(8)]
        gb=[0.]*8
        for x,prev,z,h in reversed(tapes):
            dz=[dh[i] if -1<z[i]<1 else 0. for i in range(8)]
            for i in range(8):
                gb[i]+=dz[i]
                for k in range(DIMS): gx[i][k]+=dz[i]*x[k]
                for k in range(8): gh[i][k]+=dz[i]*prev[k]
            dh=[sum(self.wh[i][k]*dz[i] for i in range(8))
                for k in range(8)]
        last_h=tapes[-1][3]
        rate=.05
        for j in range(OUT):
            for i in range(8):
                self.v[j][i]=round(clamp(self.v[j][i]-rate*e[j]*last_h[i],-2,2),8)
            self.c[j]=round(clamp(self.c[j]-rate*e[j],-2,2),8)
        for i in range(8):
            for k in range(DIMS):
                self.wx[i][k]=round(clamp(self.wx[i][k]-rate*gx[i][k],-2,2),8)
            for k in range(8):
                self.wh[i][k]=round(clamp(self.wh[i][k]-rate*gh[i][k],-2,2),8)
            self.b[i]=round(clamp(self.b[i]-rate*gb[i],-2,2),8)
        self.count+=1

    def dump(self):
        return {"kind":self.kind,"wx":self.wx,"wh":self.wh,"v":self.v,
                "b":self.b,"c":self.c,"count":self.count}

    def load(self,data):
        for k in ("wx","wh","v","b","c","count"):
            setattr(self,k,data[k])


class Persistence:
    kind="persistence"
    def predict(self,seq):
        return persistence(seq)
    def learn(self,seq,target,stage):
        pass
    def dump(self):
        return {"kind":self.kind}
    def load(self,data):
        if data!={"kind":self.kind}:
            raise AssertionError("MG19_PERSISTENCE_CHECKPOINT_DRIFT")


def persistence(seq):
    return tuple(seq[-1][:7])+(0.,)


def make_model(kind):
    if kind in ("episodic_history","shuffled_history"): return Episodic(kind)
    if kind=="memoryless_sgd": return SGD()
    if kind=="recurrent_sgd": return Recurrent()
    if kind=="persistence": return Persistence()
    raise ValueError("MG19_UNKNOWN_ARM")


def snapshot(model):
    payload=zlib.compress(canon(model.dump()).encode(),level=9)
    if len(payload)>65536:
        raise AssertionError("MG19_CHECKPOINT_TOO_LARGE")
    return payload


def restore(raw):
    d=json.loads(zlib.decompress(raw).decode())
    obj=make_model(d["kind"])
    obj.load(d)
    if snapshot(obj)!=raw:
        raise AssertionError("MG19_NONCANONICAL_CHECKPOINT")
    return obj


def train(arms,episode,stage,clock):
    for seq,target,_ in episode["rows"]:
        for name,model in arms.items():
            t=time.perf_counter_ns()
            model.learn(seq,target,stage)
            clock[name]+=time.perf_counter_ns()-t


def evaluate(arms,episodes,clock):
    raw={k:snapshot(m) for k,m in arms.items()}
    series={k:[] for k in arms}
    briers={k:[] for k in arms}
    per_seed={k:{} for k in arms}
    changed=0
    forecast_count=0
    for ep in episodes:
        forecast_count+=len(ep["rows"])
        changed+=sum(int(r[2]) for r in ep["rows"])
        for name,m in arms.items():
            losses=[]
            for seq,target,_ in ep["rows"]:
                t=time.perf_counter_ns()
                pred=m.predict(seq)
                clock[name]+=time.perf_counter_ns()-t
                loss=round(mse(pred,target),12)
                event_loss=round((pred[-1]-target[-1])**2,12)
                losses.append(loss)
                series[name].append(loss)
                briers[name].append(event_loss)
            per_seed[name][str(ep["seed"])]=round(statistics.mean(losses),12) if losses else None
    for name,model in arms.items():
        if snapshot(model)!=raw[name]:
            raise AssertionError("MG19_EVALUATOR_TRAINING_LEAKAGE")
    return {"metrics":{
        k:{"mse":round(statistics.mean(series[k]),12) if series[k] else None,
           "event_brier":round(statistics.mean(briers[k]),12) if briers[k] else None}
        for k in arms},
        "per_seed":per_seed,"forecast_count":forecast_count,
        "changed_visual_windows":changed,
        "meaningful_change_fraction":round(changed/max(1,forecast_count),8),
        "episode_count":len(episodes)}


def stage_collect(env_id,seeds,steps):
    episodes=[]
    for seed in seeds:
        ep=collect(env_id,seed)
        steps.append({"env":ep["env"],"seed":ep["seed"],"steps":ep["steps"],
                      "trajectory_sha256":ep["trajectory_sha256"],
                      "rewarded_steps":ep["rewarded_steps"],
                      "forecast_windows":len(ep["rows"])})
        episodes.append(ep)
    return episodes


def run():
    require_manifest()
    import minigrid
    import gymnasium
    import numpy
    if (minigrid.__version__!="3.2.0" or gymnasium.__version__!="1.4.0"
            or numpy.__version__!="2.3.4"):
        raise AssertionError("MG19_DEPENDENCY_VERSION_DRIFT")
    arms={kind:make_model(kind) for kind in ARMS}
    clock={kind:0 for kind in ARMS}
    steps=[]
    for env_id in TRAIN_ENVS:
        for ep in stage_collect(env_id,TRAIN_SEEDS,steps):
            train(arms,ep,"train",clock)
    snapshots={k:snapshot(m) for k,m in arms.items()}
    probe=[[0.1]*DIMS,[0.3]*DIMS,[0.4]*DIMS]
    for name,m in arms.items():
        twin=restore(snapshots[name])
        if twin.predict(probe)!=m.predict(probe):
            raise AssertionError("MG19_COLD_CHECKPOINT_INFERENCE_DRIFT")
    cold_before_eps=stage_collect(COLD_ENV,COLD_SEEDS,steps)
    before=evaluate(arms,cold_before_eps,clock)
    interference_eps=stage_collect(INTERFERENCE_ENV,INTERFERENCE_SEEDS,steps)
    for ep in interference_eps:
        train(arms,ep,"interference",clock)
    retain={k:(m.retained() if isinstance(m,Episodic) else None)
            for k,m in arms.items()}
    retained_arms={k:restore(snapshot(m)) for k,m in arms.items()}
    cold_after_eps=stage_collect(COLD_ENV,COLD_SEEDS,steps)
    cold_after=evaluate(retained_arms,cold_after_eps,clock)
    unseen_size_eps=stage_collect(LARGER_ENV,LARGER_SEEDS,steps)
    size=evaluate(retained_arms,unseen_size_eps,clock)
    unseen_family_eps=stage_collect(TRANSFER_ENV,TRANSFER_SEEDS,steps)
    transfer=evaluate(retained_arms,unseen_family_eps,clock)
    paid=sum(s["steps"] for s in steps)
    if len(steps)!=84 or paid>10752 or any(s["steps"]>128 for s in steps):
        raise AssertionError("MG19_REAL_PHYSICAL_ACTION_CUSTODY_DRIFT")
    assert len({(x["env"],x["seed"]) for x in steps})==72
    # The deliberate second cold evaluation repeats an identical env/seed, and is charged.
    cold_trace={s["trajectory_sha256"] for s in steps
        if s["env"]==COLD_ENV and s["seed"] in COLD_SEEDS}
    if len(cold_trace)!=12:
        raise AssertionError("MG19_COLD_TRAJECTORY_NONDETERMINISM")
    old=before["metrics"]["episodic_history"]["mse"]
    new=cold_after["metrics"]["episodic_history"]["mse"]
    cold_ratio=round(new/max(1e-12,old),8)
    wins={}
    for split_name,split in (("unseen_size",size),("unseen_family",transfer)):
        count=0
        for seed in (LARGER_SEEDS if split_name=="unseen_size" else TRANSFER_SEEDS):
            val=split["per_seed"]["episodic_history"][str(seed)]
            best=min(split["per_seed"][name][str(seed)]
                     for name in ("memoryless_sgd","recurrent_sgd"))
            count+=int(val<best)
        wins[split_name]=count
    gates={}
    for split_name,split in (("unseen_size",size),("unseen_family",transfer)):
        candidate=split["metrics"]["episodic_history"]["mse"]
        strongest=min(split["metrics"][name]["mse"]
                     for name in ("memoryless_sgd","recurrent_sgd","persistence","shuffled_history"))
        gates[split_name+"_all_control_margin"]=candidate<=strongest-.0001
        gates[split_name+"_seed_wins"]=wins[split_name]>=9
    gates["cold_mse_retained"]=cold_ratio<=1.10
    gates["cold_vs_conventional"]=(
        cold_after["metrics"]["episodic_history"]["mse"]<=
        min(cold_after["metrics"][name]["mse"] for name in
            ("memoryless_sgd","recurrent_sgd"))-.0001)
    gates["reward_brier_nondegradation"]=all(
        split["metrics"]["episodic_history"]["event_brier"]<=
        min(split["metrics"][name]["event_brier"] for name in
            ("memoryless_sgd","recurrent_sgd"))+.001
        for split in (size,transfer))
    gates["coverage"]=size["forecast_count"]+transfer["forecast_count"]>=500 and all(
        split["meaningful_change_fraction"]>=.05
        for split in (size,transfer))
    ratios={a:round(clock["episodic_history"]/max(1,clock[a]),6)
            for a in ("recurrent_sgd","memoryless_sgd")}
    gates["cpu_vs_recurrent"]=ratios["recurrent_sgd"]<=3
    gates["checkpoint_bounded"]=all(
        len(snapshot(m))<=65536 for m in retained_arms.values())
    primary=all(gates.values())
    partial=(any(
        split["metrics"]["episodic_history"]["mse"]<
        split["metrics"][a]["mse"]
        for split in (size,transfer,cold_after)
        for a in ("shuffled_history","memoryless_sgd","recurrent_sgd","persistence"))
        or (retain["episodic_history"]>0 and cold_ratio<=1))
    return {"schema":SCHEMA,"freeze_sha":FREEZE,"parent_sha":PARENT,
            "manifest_sha256":MANIFEST_HASH,"classification":(
                "INVALID_TASK_COVERAGE" if not gates["coverage"] else
                "DEVELOPMENT_SIGNAL_ONLY" if primary else
                "MIXED_DEV" if partial else "NEGATIVE_DEV"),
            "primary_pass":primary,"scientific_acceptance":"UNVERIFIED",
            "package_versions":{"minigrid":minigrid.__version__,
                                "gymnasium":gymnasium.__version__,
                                "numpy":numpy.__version__},
            "python_version":platform.python_version(),
            "charged_env_steps":paid,
            "total_episodes":len(steps),"recorded_episodes":steps,
            "first_training_sample_retention":retain,
            "cross_os_traces_required":True,
            "cold_before":before,"cold_after":cold_after,
            "unseen_size":size,"unseen_family":transfer,
            "cold_ratio":cold_ratio,"per_seed_wins":wins,"gates":gates,
            "CPU_ratio":ratios,"raw_cpu_ns":clock,
            "checkpoint_sha256":{k:hashlib.sha256(snapshot(m)).hexdigest()
                                  for k,m in retained_arms.items()},
            "checkpoint_bytes":{k:len(snapshot(m))
                                for k,m in retained_arms.items()},
            "model_training_counts":{k:m.dump().get("count",m.dump().get("seen",0))
                                     for k,m in retained_arms.items()},
            "native_model_changed":False}


if __name__=="__main__":
    print(canon(run()))

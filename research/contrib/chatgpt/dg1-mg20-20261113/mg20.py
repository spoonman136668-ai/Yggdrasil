"""DG1-MG20: prospective official-reward MiniGrid policy experiment.
Non-token external research. Never use registered seeds before original draft-PR opening.
"""
import hashlib
import json
import math
import platform
import random
import statistics
import time
import zlib
from collections import deque

FREEZE="029bd7e8da15e0512c2a11bba90a9fb322bb751f"
PARENT="5e74f8db85b2f5839c42148c0dfba69a88b1a2c9"
MANIFEST_SHA="c51855a9ab42e2bd5da848cd7eaa0db342fcf167dffa4d3237802d12d1096cff"
SCHEMA="yggdrasil.dg1-mg20-original.v1"
TRAIN_SEEDS=tuple(range(730001,730025))
INTERFERENCE_SEEDS=tuple(range(740001,740013))
COLD_SEEDS=tuple(range(750001,750013))
SIZE_SEEDS=tuple(range(760001,760013))
FAMILY_SEEDS=tuple(range(770001,770013))
TRAIN_ENVS=("MiniGrid-Empty-5x5-v0","MiniGrid-Empty-6x6-v0")
INTERFERENCE_ENV="MiniGrid-DoorKey-6x6-v0"
COLD_ENV="MiniGrid-Empty-6x6-v0"
SIZE_ENV="MiniGrid-Empty-8x8-v0"
FAMILY_ENV="MiniGrid-Dynamic-Obstacles-6x6-v0"
ARMS=("causal_map","sham_map","reactive","tabular_q","recurrent_imitation")
MAX_STEPS=128
FEATURES=18
HIDDEN=12
HISTORY=8
ACTIONS=(0,1,2,3,5)
LIMIT=256


def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)


def digest(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()


def manifest():
    return {"schema":"yggdrasil.dg1-mg20-action-plan.v1",
            "train_seeds":list(TRAIN_SEEDS),
            "interference_seeds":list(INTERFERENCE_SEEDS),
            "cold_seeds":list(COLD_SEEDS),
            "unseen_size_seeds":list(SIZE_SEEDS),
            "unseen_family_seeds":list(FAMILY_SEEDS),
            "train_envs":list(TRAIN_ENVS),
            "interference_env":INTERFERENCE_ENV,
            "cold_env":COLD_ENV,
            "unseen_size_env":SIZE_ENV,
            "unseen_family_env":FAMILY_ENV,
            "max_steps":MAX_STEPS,
            "arms":list(ARMS)}


def verify_manifest():
    if digest(manifest())!=MANIFEST_SHA:
        raise AssertionError("MG20_REGISTERED_MANIFEST_DRIFT")


def objects(obs):
    return obs["image"][:,:,0]


def front_type(obs):
    return int(objects(obs)[3,5])


def goal_position(obs):
    from minigrid.core.constants import OBJECT_TO_IDX
    import numpy as np
    pos=np.argwhere(objects(obs)==OBJECT_TO_IDX["goal"])
    if len(pos)==0: return None
    xy=pos[0]
    return (int(xy[0])-3,6-int(xy[1]))


def public_features(obs,prev_action,t):
    from minigrid.core.constants import OBJECT_TO_IDX
    o=objects(obs)
    n=float(o.size)
    types=("wall","door","key","goal","empty","box","ball")
    counts=[round(float((o==OBJECT_TO_IDX[k]).sum())/n,8) for k in types]
    goal=goal_position(obs)
    visible=1. if goal is not None else 0.
    dx=0. if goal is None else goal[0]/6.
    forward=0. if goal is None else goal[1]/6.
    ft=front_type(obs)
    wall=float(ft in (OBJECT_TO_IDX["wall"],OBJECT_TO_IDX["door"]))
    hazard=float(ft in (OBJECT_TO_IDX["lava"],OBJECT_TO_IDX["ball"]))
    direction=int(obs["direction"])
    if direction not in range(4) or prev_action not in range(7) or not isinstance(t,int):
        raise ValueError("MG20_BAD_PUBLIC_STATE")
    vec=tuple(counts)+(visible,round(dx,8),round(forward,8),wall,hazard)+tuple(
        float(direction==d) for d in range(4))+(round(prev_action/6,8),round(t/MAX_STEPS,8))
    if len(vec)!=FEATURES:
        raise AssertionError("MG20_FEATURE_DIM_MISMATCH")
    return vec


def reactive_action(obs,t,rng):
    from minigrid.core.constants import OBJECT_TO_IDX
    front=front_type(obs)
    g=goal_position(obs)
    if front==OBJECT_TO_IDX["key"]: return 3
    if front==OBJECT_TO_IDX["door"] and t%3==0: return 5
    blocked=front in (OBJECT_TO_IDX["wall"],OBJECT_TO_IDX["door"],
                      OBJECT_TO_IDX["lava"],OBJECT_TO_IDX["ball"])
    if g is not None:
        dx,dy=g
        if dx>0: return 1
        if dx<0: return 0
        if dy<0: return 1
        if not blocked: return 2
        return rng.choice((0,1))
    if blocked:
        return rng.choice((0,1))
    v=rng.random()
    return 2 if v<.73 else 0 if v<.86 else 1


class Reactive:
    kind="reactive"
    def start(self,seed):
        self.rng=random.Random(seed^0x20A1)
    def act(self,obs,t):
        return reactive_action(obs,t,self.rng)
    def feedback(self,obs,action,after,reward,training=False):
        return None
    def dump(self): return {"kind":self.kind}
    def load(self,d):
        if d!={"kind":self.kind}:raise AssertionError("MG20_REACTIVE_DRIFT")


class MapPolicy:
    """Online topological causal memory: public image, direction and charged actions only."""
    def __init__(self,kind):
        self.kind=kind
        self.passability={}
        self.train_calls=0
        self.start(11)

    def start(self,seed):
        self.pose=(0,0)
        self.tiles={}
        self.visits={}
        self.last_obs=None
        self.last_action=None
        self.clock=0
        self.rng=random.Random(seed^0x200C)
        self.training_seed=seed
        self.ephemeral_step_count=0

    @staticmethod
    def vectors(direction):
        forward=((1,0),(0,1),(-1,0),(0,-1))[direction]
        right=((-forward[1],forward[0]))
        return forward,right

    @staticmethod
    def motion_signal(before,after):
        """Image overlap infers consequence of forward motion; no hidden pose."""
        import numpy as np
        a=objects(before)
        b=objects(after)
        # After moving forward, prior near objects shift one pixel toward image bottom.
        shifted=a[:,0:6]
        now=b[:,1:7]
        visible=(shifted!=0)&(now!=0)
        aligned=int(((shifted==now)&visible).sum())
        held=int(((a==b)&(a!=0)&(b!=0)).sum())
        total=int(visible.sum())
        if total>=7 and aligned>held*.91:
            return True
        return None

    def move_estimate(self,before,after):
        from minigrid.core.constants import OBJECT_TO_IDX
        ft=front_type(before)
        score=self.motion_signal(before,after)
        if score is not None: return score
        old=self.passability.get(str(ft),[0,0])
        if old[1]>=3:
            return old[0]*2>=old[1]
        return ft in (OBJECT_TO_IDX["empty"],OBJECT_TO_IDX["goal"])

    def feedback(self,before,action,after,reward,training=False):
        if training and action==2:
            ft=str(front_type(before))
            data=self.passability.setdefault(ft,[0,0])
            move=self.move_estimate(before,after)
            data[0]+=int(move)
            data[1]+=1
            self.train_calls+=1
        if action==2:
            if self.move_estimate(before,after):
                forward,_=self.vectors(int(before["direction"]))
                self.pose=(self.pose[0]+forward[0],self.pose[1]+forward[1])

    def ingest(self,obs):
        from minigrid.core.constants import OBJECT_TO_IDX
        img=objects(obs)
        fx,rx=self.vectors(int(obs["direction"]))
        ax,ay=self.pose
        for dx in range(7):
            for dy in range(7):
                object_id=int(img[dx,dy])
                if object_id==OBJECT_TO_IDX["unseen"]:
                    continue
                xx=ax+(6-dy)*fx[0]+(dx-3)*rx[0]
                yy=ay+(6-dy)*fx[1]+(dx-3)*rx[1]
                if self.kind=="sham_map":
                    # Same state capacity/observation but break spatial coherence.
                    xx+=((self.ephemeral_step_count*17)%11)-5
                    yy+=((self.ephemeral_step_count*13)%11)-5
                key=(xx,yy)
                self.tiles[key]=object_id
                if len(self.tiles)>LIMIT:
                    self.tiles.pop(next(iter(self.tiles)))
        self.visits[self.pose]=self.visits.get(self.pose,0)+1
        self.ephemeral_step_count+=1

    def navigable(self,obj):
        from minigrid.core.constants import OBJECT_TO_IDX
        blocked=(OBJECT_TO_IDX["wall"],OBJECT_TO_IDX["lava"],
                 OBJECT_TO_IDX["ball"],OBJECT_TO_IDX["door"])
        if obj in blocked: return False
        value=self.passability.get(str(obj))
        return value[0]*2>=value[1] if value and value[1]>=3 else True

    def path(self):
        from minigrid.core.constants import OBJECT_TO_IDX
        start=self.pose
        queue=deque([(start,[])])
        seen={start}
        goals=[]
        frontiers=[]
        directions=((1,0),(0,1),(-1,0),(0,-1))
        while queue:
            position,path=queue.popleft()
            if len(path)>30: continue
            if self.tiles.get(position)==OBJECT_TO_IDX["goal"]:
                goals.append(path)
            for index,(vx,vy) in enumerate(directions):
                nxt=(position[0]+vx,position[1]+vy)
                if nxt in seen:continue
                seen.add(nxt)
                newpath=path+[index]
                obj=self.tiles.get(nxt)
                if obj is None:
                    frontiers.append((len(newpath)+4*self.visits.get(nxt,0),
                                      len(newpath),nxt,newpath))
                elif self.navigable(obj):
                    queue.append((nxt,newpath))
        if goals:
            return min(goals,key=lambda q:(len(q),q))
        if frontiers:
            return min(frontiers,key=lambda q:(q[0],q[1],q[2]))[3]
        return []

    def act(self,obs,t):
        self.ingest(obs)
        plan=self.path()
        if not plan:
            return reactive_action(obs,t,self.rng)
        wanted=plan[0]
        current=int(obs["direction"])
        delta=(wanted-current)%4
        if delta==0:
            return 2
        if delta==1:return 1
        if delta==3:return 0
        return 1

    def dump(self):
        return {"kind":self.kind,"passability":self.passability,
                "train_calls":self.train_calls}
    def load(self,d):
        self.passability=d["passability"]
        self.train_calls=d["train_calls"]


class TabularQ:
    kind="tabular_q"
    def __init__(self):
        self.q={}
        self.count=0
    def start(self,seed):
        self.rng=random.Random(seed^0x20B7)
    def state(self,obs):
        ft=front_type(obs)
        g=goal_position(obs)
        sign=lambda v: 0 if v==0 else -1 if v<0 else 1
        return canon((int(obs["direction"]),ft,int(g is not None),
                      sign(g[0]) if g else 0,sign(g[1]) if g else 0))
    def value(self,state):
        if state not in self.q:self.q[state]=[0.]*len(ACTIONS)
        return self.q[state]
    def feedback(self,obs,action,after,reward,training=False,terminal=False):
        if not training:return
        state=self.state(obs)
        nxt=self.state(after)
        old=self.value(state)
        slot=ACTIONS.index(action)
        best=0 if terminal else max(self.value(nxt))
        old[slot]=round(old[slot]+.2*(reward+.95*best-old[slot]),8)
        self.count+=1
    def act(self,obs,t):
        state=self.state(obs)
        values=self.q.get(state)
        if not values or max(values)<=0:
            return reactive_action(obs,t,self.rng)
        best=max(range(len(values)),key=lambda i:(values[i],-i))
        return ACTIONS[best]
    def dump(self): return {"kind":self.kind,"q":self.q,"count":self.count}
    def load(self,d):self.q=d["q"];self.count=d["count"]


class RecurrentImitation:
    """Conventional fully trained 12-cell recurrent policy with 8-step BPTT."""
    kind="recurrent_imitation"
    def __init__(self):
        r=random.Random(29555)
        self.wx=[[round(r.uniform(-.045,.045),8) for _ in range(FEATURES)]for _ in range(HIDDEN)]
        self.wh=[[round(r.uniform(-.035,.035),8) for _ in range(HIDDEN)]for _ in range(HIDDEN)]
        self.v=[[round(r.uniform(-.035,.035),8) for _ in range(HIDDEN)]for _ in ACTIONS]
        self.b=[0.]*HIDDEN
        self.c=[0.]*len(ACTIONS)
        self.count=0
        self.start(11)

    def start(self,seed):
        self.history=[]

    def forward(self,seq):
        if not seq:raise ValueError("MG20_EMPTY_RECURRENT_CONTEXT")
        seq=[seq[0]]*max(0,HISTORY-len(seq))+list(seq[-HISTORY:])
        h=[0.]*HIDDEN
        trace=[]
        for x in seq:
            prev=h[:]
            z=[sum(a*b for a,b in zip(self.wx[i],x))+
               sum(a*b for a,b in zip(self.wh[i],prev))+self.b[i]
               for i in range(HIDDEN)]
            h=[max(-1.,min(1.,z[i])) for i in range(HIDDEN)]
            trace.append((x,prev,z,h[:]))
        out=[sum(a*b for a,b in zip(self.v[j],h))+self.c[j]
             for j in range(len(ACTIONS))]
        return out,trace

    def learn(self,seq,action,weight=1.):
        logits,trace=self.forward(seq)
        goal=ACTIONS.index(action)
        e=[(logits[j]-int(j==goal))*weight/len(ACTIONS)
           for j in range(len(ACTIONS))]
        dh=[sum(self.v[j][i]*e[j] for j in range(len(ACTIONS)))
            for i in range(HIDDEN)]
        dx=[[0.]*FEATURES for _ in range(HIDDEN)]
        dw=[[0.]*HIDDEN for _ in range(HIDDEN)]
        db=[0.]*HIDDEN
        for x,prev,z,h in reversed(trace):
            dz=[dh[i] if -1<z[i]<1 else 0. for i in range(HIDDEN)]
            for i in range(HIDDEN):
                db[i]+=dz[i]
                for k in range(FEATURES):
                    dx[i][k]+=dz[i]*x[k]
                for k in range(HIDDEN):
                    dw[i][k]+=dz[i]*prev[k]
            dh=[sum(self.wh[i][k]*dz[i] for i in range(HIDDEN))
                for k in range(HIDDEN)]
        last=trace[-1][3]
        rate=.025
        def weight_update(x):
            return round(max(-2.,min(2.,x)),8)
        for j in range(len(ACTIONS)):
            for i in range(HIDDEN):
                self.v[j][i]=weight_update(self.v[j][i]-rate*e[j]*last[i])
            self.c[j]=weight_update(self.c[j]-rate*e[j])
        for i in range(HIDDEN):
            for k in range(FEATURES):
                self.wx[i][k]=weight_update(self.wx[i][k]-rate*dx[i][k])
            for k in range(HIDDEN):
                self.wh[i][k]=weight_update(self.wh[i][k]-rate*dw[i][k])
            self.b[i]=weight_update(self.b[i]-rate*db[i])
        self.count+=1

    def act(self,obs,t):
        prev=getattr(self,"prev_action",6)
        self.history.append(public_features(obs,prev,t))
        self.history=self.history[-HISTORY:]
        logits,_=self.forward(self.history)
        best=max(range(len(ACTIONS)),key=lambda i:(logits[i],-i))
        self.prev_action=ACTIONS[best]
        return self.prev_action

    def feedback(self,obs,action,after,reward,training=False):
        return None

    def dump(self):
        return {"kind":self.kind,"wx":self.wx,"wh":self.wh,"v":self.v,
                "b":self.b,"c":self.c,"count":self.count}
    def load(self,d):
        for key in ("wx","wh","v","b","c","count"):
            setattr(self,key,d[key])


def make_agent(name):
    if name in ("causal_map","sham_map"):return MapPolicy(name)
    if name=="reactive":return Reactive()
    if name=="tabular_q":return TabularQ()
    if name=="recurrent_imitation":return RecurrentImitation()
    raise ValueError("MG20_UNKNOWN_ARM")


def save(model):
    data=zlib.compress(canon(model.dump()).encode(),9)
    if len(data)>65536:raise AssertionError("MG20_OVER_CAPACITY")
    return data


def load(data):
    d=json.loads(zlib.decompress(data))
    agent=make_agent(d["kind"])
    agent.load(d)
    if save(agent)!=data:
        raise AssertionError("MG20_NONCANONICAL_CHECKPOINT")
    return agent


def recorded_state(obs):
    return [int(obs["direction"]),objects(obs).tobytes()]


def make_trace(env_id,seed,policy_model=None):
    """Return one physical trajectory. Never call env.step extra for controls."""
    import gymnasium as gym
    import minigrid
    env=gym.make(env_id)
    if policy_model is None: policy_model=Reactive()
    try:
        obs,_=env.reset(seed=seed)
        policy_model.start(seed)
        transitions=[]
        state_hash=hashlib.sha256((env_id+":"+str(seed)).encode())
        completed=False
        discount=0.
        clock=0
        for t in range(MAX_STEPS):
            before=obs
            start=time.perf_counter_ns()
            a=policy_model.act(before,t)
            clock+=time.perf_counter_ns()-start
            if a not in ACTIONS:raise AssertionError("MG20_INVALID_ACTION")
            obs,reward,terminated,truncated,_=env.step(a)
            policy_model.feedback(before,a,obs,reward,training=False)
            state_hash.update(bytes((a,int(obs["direction"]))))
            state_hash.update(objects(obs).tobytes())
            state_hash.update(f"{float(reward):.8f}".encode())
            transitions.append((before,a,float(reward),obs,bool(terminated or truncated)))
            discount+=float(reward)*(.99**t)
            completed=completed or reward>0
            if terminated or truncated:break
    finally:
        env.close()
    return {"env":env_id,"seed":seed,"steps":len(transitions),
            "success":int(completed),"discounted_reward":round(discount,8),
            "sha256":state_hash.hexdigest(),"transitions":transitions,
            "cpu_ns":clock}


def train_on_shared(agents,episode,stage):
    transitions=episode["transitions"]
    seq=[]
    last=6
    success=bool(episode["success"])
    for i,(before,a,reward,after,terminal) in enumerate(transitions):
        agents["causal_map"].feedback(before,a,after,reward,training=True)
        agents["sham_map"].feedback(before,a,after,reward,training=True)
        agents["tabular_q"].feedback(before,a,after,reward,training=True,terminal=terminal)
        seq.append(public_features(before,last,i))
        seq=seq[-HISTORY:]
        agents["recurrent_imitation"].learn(seq,a,2. if success else 1.)
        last=a


def episode_receipt(ep,model):
    if model is None:return {k:v for k,v in ep.items() if k not in ("transitions","cpu_ns")}
    return {**{k:v for k,v in ep.items() if k not in ("transitions","cpu_ns")},
            "arm":model.kind,"decision_cpu_ns":ep["cpu_ns"]}


def score(agents,env_id,seeds):
    checkpoint={k:save(v) for k,v in agents.items()}
    outcome={k:[] for k in agents}
    for arm,model in agents.items():
        for seed in seeds:
            ep=make_trace(env_id,seed,model)
            outcome[arm].append(episode_receipt(ep,model))
    for k,model in agents.items():
        if save(model)!=checkpoint[k]:
            raise AssertionError("MG20_HOLDOUT_LEARNING_LEAKAGE")
    metrics={}
    for arm,recs in outcome.items():
        success=sum(x["success"] for x in recs)
        metrics[arm]={"success_count":success,"success_fraction":round(success/len(recs),8),
                      "mean_official_return":round(statistics.mean(x["discounted_reward"]for x in recs),8),
                      "mean_charged_steps":round(statistics.mean(x["steps"] for x in recs),8),
                      "decision_cpu_ns":sum(x["decision_cpu_ns"] for x in recs),
                      "positive_episode_seeds":[x["seed"] for x in recs if x["success"]],
                      "trace_hashes":{str(x["seed"]):x["sha256"] for x in recs},
                      "charged_steps":sum(x["steps"] for x in recs)}
    return {"environment":env_id,"seeds":list(seeds),
            "metrics":metrics,
            "counted_env_steps":sum(x["steps"] for recs in outcome.values() for x in recs),
            "episodes":{k:[{z:v for z,v in x.items() if z!="decision_cpu_ns"}
                            for x in recs] for k,recs in outcome.items()}}


def run():
    verify_manifest()
    import minigrid,gymnasium,numpy
    if (minigrid.__version__!="3.2.0" or gymnasium.__version__!="1.4.0"
            or numpy.__version__!="2.3.4"):
        raise AssertionError("MG20_PACKAGE_DRIFT")
    agents={name:make_agent(name) for name in ARMS}
    receipts=[]
    successes=0
    training_steps=0
    for env_id in TRAIN_ENVS:
        for seed in TRAIN_SEEDS:
            ep=make_trace(env_id,seed)
            training_steps+=ep["steps"]
            successes+=ep["success"]
            receipts.append(episode_receipt(ep,None))
            train_on_shared(agents,ep,"train")
    pre={k:save(v) for k,v in agents.items()}
    snapshots_ok=all(save(load(v))==v for v in pre.values())
    if not snapshots_ok:raise AssertionError("MG20_COLD_RESTORE_FAIL")
    cold_before=score(agents,COLD_ENV,COLD_SEEDS)
    interference_successes=0
    interference_steps=0
    for seed in INTERFERENCE_SEEDS:
        ep=make_trace(INTERFERENCE_ENV,seed)
        receipts.append(episode_receipt(ep,None))
        interference_steps+=ep["steps"]
        interference_successes+=ep["success"]
        train_on_shared(agents,ep,"interference")
    for k,v in agents.items():
        if save(load(save(v)))!=save(v):
            raise AssertionError("MG20_INTERFERENCE_SNAPSHOT_FAIL")
    cold_after=score(agents,COLD_ENV,COLD_SEEDS)
    unseen_size=score(agents,SIZE_ENV,SIZE_SEEDS)
    unseen_family=score(agents,FAMILY_ENV,FAMILY_SEEDS)
    total_steps=training_steps+interference_steps+sum(x["counted_env_steps"]
        for x in (cold_before,cold_after,unseen_size,unseen_family))
    if total_steps>38400 or len(receipts)!=60:
        raise AssertionError("MG20_PHYSICAL_BUDGET_FAIL")
    per_seed_wins={}
    gates={}
    for name,part in (("unseen_size",unseen_size),("unseen_family",unseen_family)):
        candidate=part["metrics"]["causal_map"]["success_count"]
        best=max(part["metrics"][c]["success_count"] for c in ARMS if c!="causal_map")
        gates[name+"_goal_margin"]=candidate>=best+2
        own=set(part["metrics"]["causal_map"]["positive_episode_seeds"])
        best_control=max((x for x in ARMS if x!="causal_map"),key=lambda x:
                         part["metrics"][x]["success_count"])
        rival=set(part["metrics"][best_control]["positive_episode_seeds"])
        count=len(own-rival)
        per_seed_wins[name]=count
        gates[name+"_per_seed_wins"]=count>=5
    orig=cold_before["metrics"]["causal_map"]["success_count"]
    after=cold_after["metrics"]["causal_map"]["success_count"]
    gates["cold_retention"]=after>=orig-1
    gates["cold_vs_reactive"]=after>=cold_after["metrics"]["reactive"]["success_count"]
    ratio=round((unseen_size["metrics"]["causal_map"]["decision_cpu_ns"]+
                 unseen_family["metrics"]["causal_map"]["decision_cpu_ns"])/
                max(1,unseen_size["metrics"]["recurrent_imitation"]["decision_cpu_ns"]+
                      unseen_family["metrics"]["recurrent_imitation"]["decision_cpu_ns"]),6)
    gates["cpu_vs_recurrent"]=ratio<=3
    gates["bounded_checkpoint"]=all(len(save(m))<=65536 for m in agents.values())
    training_model_counts={
        k:(v.dump().get("count") if hasattr(v,"count") else
           v.dump().get("train_calls",0)) for k,v in agents.items()}
    gates["trained_conventional"]=(
        training_model_counts["tabular_q"]>0 and
        training_model_counts["recurrent_imitation"]>0)
    heldout_coverage={name:sum(part["metrics"][arm]["success_count"] for arm in ARMS)
            for name,part in (("unseen_size",unseen_size),("unseen_family",unseen_family))}
    sufficient_coverage=successes>=8 and all(v>=3 for v in heldout_coverage.values())
    primary=all(gates.values()) and sufficient_coverage
    partial=(any(
        part["metrics"]["causal_map"]["success_count"]>=
        part["metrics"][c]["success_count"]+2
        for part in (unseen_size,unseen_family) for c in ARMS if c!="causal_map") or
        (after>=orig-1 and after>0))
    classification=("INVALID_TASK_COVERAGE" if not sufficient_coverage else
                    "DEVELOPMENT_SIGNAL_ONLY" if primary else
                    "MIXED_DEV" if partial else "NEGATIVE_DEV")
    return {"schema":SCHEMA,"freeze_sha":FREEZE,"parent_sha":PARENT,
            "manifest_sha256":MANIFEST_SHA,"classification":classification,
            "primary_pass":primary,"scientific_acceptance":"UNVERIFIED",
            "packages":{"minigrid":minigrid.__version__,"gymnasium":gymnasium.__version__,
                        "numpy":numpy.__version__},
            "training_episode_count":48,"interference_episode_count":12,
            "heldout_episode_count":240,"total_episodes":300,
            "charged_training_steps":training_steps,
            "charged_interference_steps":interference_steps,
            "charged_total_steps":total_steps,
            "training_official_successes":successes,
            "interference_official_successes":interference_successes,
            "heldout_success_coverage":heldout_coverage,
            "per_seed_goal_wins":per_seed_wins,
            "gates":gates,"cpu_ratio":ratio,
            "model_training_counts":training_model_counts,
            "checkpoint_sha256":{k:hashlib.sha256(save(v)).hexdigest()
                                 for k,v in agents.items()},
            "checkpoint_bytes":{k:len(save(v)) for k,v in agents.items()},
            "train_and_interference_trace":receipts,
            "cold_before":cold_before,"cold_after":cold_after,
            "unseen_size":unseen_size,"unseen_family":unseen_family,
            "native_model_changed":False}


if __name__=="__main__":
    print(canon(run()))

"""DG1-T17: prospective synthetic continuous causal repair, DEV only.

No native Yggdrasil model, official research loop or accepted reference is modified.
Do not invoke run() on registered seeds before the frozen source is committed.
"""
import hashlib
import json
import math
import random
import statistics
import time

FREEZE = "a4c0ee310f12f55535f8b5dea6ab2f0b190a6fe9"
PARENT = "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9"
SEEDS = tuple(range(410001, 410017))
AUDITS = (128, 160)
ARMS = ("causal_modules", "no_archive", "random_route",
        "forgetting_rls", "integer_recurrent")
MANIFEST = "eb975980ff8fae294128cd651e1d04f3b373f2263cdecce21b4fdffc7c21a8c4"
SCHEMA = "yggdrasil.dg1-t17-original.v1"


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


Q=4096


def divr(n,d):
    if d<=0:
        raise ValueError("T17_INVALID_DIVISOR")
    sign=-1 if n<0 else 1
    return sign*((abs(int(n))+d//2)//d)


def features(x, action):
    if (len(x)!=3 or any(type(v) is not int or abs(v)>8*Q for v in x)
            or type(action) is not int or action not in range(6)):
        raise ValueError("T17_INVALID_OBSERVATION_OR_ACTION")
    return [v/Q for v in x]+[float(k==action) for k in range(6)]+[1.0]


def dist(a,b):
    return sum((u-v)**2 for u,v in zip(a,b))/Q**2


class World:
    """Integer causal dynamics with hidden row lineage; learners never receive labels."""
    def __init__(self,seed):
        rng=random.Random(seed)
        pa=[]
        for j in range(3):
            row=[0]*3
            row[j]=2300
            row[(j+1+(seed%2))%3]=rng.choice((-1350,-950,950,1350))
            pa.append(row)
        b=[r[:] for r in pa]
        self.lesion=seed%3
        j=self.lesion
        old=next(k for k in range(3) if k!=j and pa[j][k]!=0)
        new=next(k for k in range(3) if k!=j and k!=old)
        b[j]=[0]*3
        b[j][j]=2300
        b[j][new]=-1350 if pa[j][old]>0 else 1350
        c=[r[:] for r in pa]
        c[j]=b[j][:]
        novel=(j+2)%3
        c[novel]=[0]*3
        c[novel][novel]=2300
        c[novel][(novel+2)%3]=1350 if seed%2 else -1350
        self.matrices=(pa,b,pa,c)
        self.charged=0

    @staticmethod
    def phase(t):
        if t<64: return 0
        if t<128: return 1
        if t<160: return 2
        return 3

    def next(self,x,action,phase):
        features(x,action)
        if type(phase) is not int or phase not in range(4):
            raise ValueError("T17_INVALID_PHASE")
        mat=self.matrices[phase]
        axis,sgn=divmod(action,2)
        motor=Q//3 if sgn==0 else -(Q//3)
        return [divr(sum(mat[j][k]*x[k] for k in range(3)),Q)
                +(motor if j==axis else 0) for j in range(3)]

    def step(self,x,action,phase):
        y=self.next(x,action,phase)
        self.charged+=1
        return y

class RLS:
    def __init__(self, forgetting=1.0, birth=0):
        self.w=[0.0]*10
        self.p=[[16.0 if i==j else 0.0 for j in range(10)] for i in range(10)]
        self.forgetting=forgetting
        self.birth=birth
        self.n=0

    def predict(self,f):
        return sum(a*b for a,b in zip(self.w,f))

    def fit(self,f,y):
        z=[sum(pij*f[j] for j,pij in enumerate(row)) for row in self.p]
        den=self.forgetting+sum(a*b for a,b in zip(f,z))
        if not math.isfinite(den) or den<=0:
            raise AssertionError("T17_BAD_RLS_CURVATURE")
        residual=y-self.predict(f)
        for i in range(10):
            self.w[i]+=z[i]*residual/den
        for i in range(10):
            for j in range(10):
                self.p[i][j]=(self.p[i][j]-z[i]*z[j]/den)/self.forgetting
        self.n+=1


class Repair:
    def __init__(self,kind):
        self.kind=kind
        self.rows=[{"active":0,"slots":[RLS(birth=0)],"witness":[]} for _ in range(3)]
        self.count=0
        self.switches=[]
        self.rng=random.Random(714113)

    def predict(self,x,a):
        f=features(x,a)
        return [r["slots"][r["active"]].predict(f) for r in self.rows]

    def observe(self,x,a,y):
        f=features(x,a)
        if len(y)!=3 or any(type(v) is not int for v in y):
            raise ValueError("T17_INVALID_REAL_CONSEQUENCE")
        for j,r in enumerate(self.rows):
            old=r["slots"][r["active"]]
            error=abs(old.predict(f)-y[j]/Q)
            witness=r["witness"]
            witness.append([f[:],float(y[j]/Q),error])
            del witness[:-4]
            if (old.n>=12 and len(witness)==4
                    and sum(ev[2]>.065 for ev in witness)>=3):
                viable=[]
                for k,m in enumerate(r["slots"]):
                    if k==r["active"] or m.n<12: continue
                    loss=sum(abs(m.predict(ev[0])-ev[1]) for ev in witness)/4
                    viable.append((loss,k))
                viable.sort()
                old_loss=sum(ev[2] for ev in witness)/4
                choice=None
                if viable and viable[0][0]<min(.055,old_loss*.55):
                    choice=(self.rng.choice([v[1] for v in viable])
                            if self.kind=="random_route" else viable[0][1])
                elif self.kind!="no_archive" and len(r["slots"])<3:
                    choice=len(r["slots"])
                    r["slots"].append(RLS(birth=self.count))
                elif self.kind=="no_archive":
                    choice=0
                    r["slots"][0]=RLS(birth=self.count)
                if choice is not None:
                    prior=r["active"]
                    r["active"]=choice
                    self.switches.append([self.count,j,prior,choice])
                    r["witness"]=[]
            r["slots"][r["active"]].fit(f,y[j]/Q)
        self.count+=1

    def dump(self):
        return {"kind":self.kind,"count":self.count,"switches":self.switches,
                "rng":list(self.rng.getstate()[1]),
                "rows":[{"active":r["active"],"witness":r["witness"],
                         "slots":[vars(m) for m in r["slots"]]} for r in self.rows]}


class Regression:
    def __init__(self):
        self.kind="forgetting_rls"
        self.rows=[RLS(forgetting=.97) for _ in range(3)]
        self.count=0

    def predict(self,x,a):
        f=features(x,a)
        return [m.predict(f) for m in self.rows]

    def observe(self,x,a,y):
        f=features(x,a)
        for i in range(3): self.rows[i].fit(f,y[i]/Q)
        self.count+=1

    def dump(self):
        return {"kind":self.kind,"count":self.count,
                "rows":[vars(m) for m in self.rows]}


class IntegerRecurrent:
    """Fully trainable 8-hidden-cell recurrent control with integer fixed-point arithmetic."""
    def __init__(self):
        self.kind="integer_recurrent"
        rng=random.Random(90129)
        self.wx=[[rng.randint(-Q//16,Q//16) for _ in range(10)] for _ in range(8)]
        self.wh=[[rng.randint(-Q//32,Q//32) for _ in range(8)] for _ in range(8)]
        self.v=[[rng.randint(-Q//16,Q//16) for _ in range(8)] for _ in range(3)]
        self.b=[0]*8
        self.c=[0]*3
        self.h=[0]*8
        self.count=0

    @staticmethod
    def input(x,a):
        features(x,a)
        return list(x)+[Q*int(k==a) for k in range(6)]+[Q]

    def forward(self,fx):
        z=[divr(sum(self.wx[i][k]*fx[k] for k in range(10))+
                sum(self.wh[i][k]*self.h[k] for k in range(8)),Q)+self.b[i]
           for i in range(8)]
        h=[max(-Q,min(Q,v)) for v in z]
        y=[divr(sum(self.v[j][k]*h[k] for k in range(8)),Q)+self.c[j]
           for j in range(3)]
        return h,y,z

    def predict(self,x,a):
        _,y,_=self.forward(self.input(x,a))
        return [v/Q for v in y]

    def observe(self,x,a,y):
        fx=self.input(x,a)
        old_h=self.h[:]
        h,p,z=self.forward(fx)
        e=[max(-2*Q,min(2*Q,p[j]-y[j])) for j in range(3)]
        dh=[divr(sum(self.v[j][i]*e[j] for j in range(3)),Q)
            if abs(z[i])<Q else 0 for i in range(8)]
        # Fixed learning rate 1/16, integer arithmetic throughout; all weights train.
        for j in range(3):
            for i in range(8):
                self.v[j][i]-=divr(e[j]*h[i],16*Q)
            self.c[j]-=divr(e[j],16)
        for i in range(8):
            for k in range(10):
                self.wx[i][k]-=divr(dh[i]*fx[k],16*Q)
            for k in range(8):
                self.wh[i][k]-=divr(dh[i]*old_h[k],16*Q)
            self.b[i]-=divr(dh[i],16)
        self.h=h
        self.count+=1

    def dump(self):
        return {k:v for k,v in vars(self).items()}

def learner(arm):
    if arm in ("causal_modules","no_archive","random_route"): return Repair(arm)
    if arm=="forgetting_rls": return Regression()
    if arm=="integer_recurrent": return IntegerRecurrent()
    raise ValueError("T17_UNKNOWN_ARM")


def snapshot(model):
    payload=canonical(model.dump()).encode()
    if len(payload)>65536: raise AssertionError("T17_CHECKPOINT_TOO_LARGE")
    return payload


def restore(payload):
    data=json.loads(payload)
    kind=data["kind"]
    model=learner(kind)
    if isinstance(model,Repair):
        model.count=data["count"]
        model.switches=data["switches"]
        model.rows=[]
        for row in data["rows"]:
            slots=[]
            for val in row["slots"]:
                m=RLS()
                m.__dict__.update(val)
                slots.append(m)
            model.rows.append({"active":row["active"],
                               "slots":slots,"witness":row["witness"]})
        model.rng.setstate((3,tuple(data["rng"]),None))
    elif isinstance(model,Regression):
        model.count=data["count"]
        model.rows=[]
        for val in data["rows"]:
            m=RLS()
            m.__dict__.update(val)
            model.rows.append(m)
    else:
        model.__dict__.update(data)
    if snapshot(model)!=payload:
        raise AssertionError("T17_NONCANONICAL_CHECKPOINT")
    return model


def probe_routes(model,x,probe_action,probe_y,seed,mark,episode):
    if not isinstance(model,Repair):
        return None
    f=features(x,probe_action)
    chosen=[]
    for j,row in enumerate(model.rows):
        slots=row["slots"]
        if model.kind=="no_archive":
            ix=0
        elif model.kind=="random_route":
            ix=random.Random(seed*100000+mark*31+episode*7+j).randrange(len(slots))
        else:
            scored=sorted((abs(slot.predict(f)-probe_y[j]/Q),k)
                          for k,slot in enumerate(slots) if slot.n>=12)
            ix=scored[0][1] if scored else row["active"]
            # Abstain when no archived relationship accounts for this consequence.
            if scored and scored[0][0]>.12:
                ix=None
        chosen.append(ix)
    return chosen


def conditioned_predict(model,x,a,routes):
    if routes is None or not isinstance(model,Repair):
        return model.predict(x,a)
    f=features(x,a)
    return [row["slots"][row["active"] if routes[j] is None else routes[j]].predict(f)
            for j,row in enumerate(model.rows)]


def audit(model,world,seed,mark):
    rng=random.Random((seed*141067)^mark)
    phase=2 if mark==128 else 3
    regrets=[]
    mses=[]
    choices=[]
    routes=[]
    for episode in range(16):
        x=[rng.randint(-Q,Q) for _ in range(3)]
        target=[rng.randint(-Q,Q) for _ in range(3)]
        probe_action=(episode+seed)%6
        probe_y=world.step(x,probe_action,phase)
        routing=probe_routes(model,x,probe_action,probe_y,seed,mark,episode)
        predicted=[[divr(round(v*Q),1) for v in conditioned_predict(model,probe_y,a,routing)]
                   for a in range(6)]
        action=min(range(6),key=lambda a:(dist(predicted[a],target),a))
        y=world.step(probe_y,action,phase)
        oracle=min(dist(world.next(probe_y,a,phase),target) for a in range(6))
        regret=dist(y,target)-oracle
        regrets.append(regret)
        mses.append(dist(predicted[action],y)/3)
        choices.append([probe_action,action,round(regret,12),round(mses[-1],12)])
        if isinstance(model,Repair):
            routes.append([None if ix is None else model.rows[j]["slots"][ix].birth
                           for j,ix in enumerate(routing)])
    return {"regret":round(statistics.mean(regrets),12),
            "mse":round(statistics.mean(mses),12),
            "choices":choices,"route_births":routes}


def one_arm(seed,arm):
    world=World(seed)
    model=learner(arm)
    rng=random.Random(seed^0xF12D)
    trace=[]
    metrics={}
    cold=[]
    state=[0]*3
    cpu_ns=0
    for t in range(160):
        if t%8==0:
            state=[rng.randint(-Q,Q) for _ in range(3)]
        before=state[:]
        action=t%6
        y=world.step(before,action,World.phase(t))
        start=time.perf_counter_ns()
        model.observe(before,action,y)
        cpu_ns+=time.perf_counter_ns()-start
        trace.append([t,before,action,y])
        state=y
        if t in (63,127,159):
            raw=snapshot(model)
            twin=restore(raw)
            probe=[Q//4,-Q//6,Q//3]
            if snapshot(twin)!=raw or any(
                twin.predict(probe,a)!=model.predict(probe,a) for a in range(6)):
                raise AssertionError("T17_COLD_RESTORE_MISMATCH")
            model=twin
            cold.append(len(raw))
        mark=t+1
        if mark in AUDITS:
            start=time.perf_counter_ns()
            metrics[str(mark)]=audit(model,world,seed,mark)
            cpu_ns+=time.perf_counter_ns()-start
    if world.charged!=224 or model.count!=160:
        raise AssertionError("T17_PAID_EVENT_BUDGET_MISMATCH")
    return {"arm":arm,"seed":seed,"paid_steps":world.charged,
            "charged_observations":160,"audits":metrics,
            "train_trace_sha256":digest(trace),"cold_bytes":cold,
            "final_checkpoint_sha256":hashlib.sha256(snapshot(model)).hexdigest(),
            "switches":getattr(model,"switches",[]),"cpu_ns":cpu_ns}

def run():
    manifest={"schema":"yggdrasil.dg1-t17-seeds.v1",
              "world_seeds":list(SEEDS),"phase_steps":[64,64,32],
              "audit_episodes_per_mark":16,"audit_marks":list(AUDITS),
              "probe_actions_per_audit":1,"goal_actions_per_audit":1,
              "arms":list(ARMS)}
    if digest(manifest)!=MANIFEST:
        raise AssertionError("T17_SEED_MANIFEST_DRIFT")
    worlds=[]
    for seed in SEEDS:
        arms={a:one_arm(seed,a) for a in ARMS}
        if len({v["train_trace_sha256"] for v in arms.values()})!=1:
            raise AssertionError("T17_DIFFERENT_PHYSICAL_INFORMATION")
        worlds.append({"seed":seed,"lesion":seed%3,"arms":arms})
    paid=sum(v["paid_steps"] for w in worlds for v in w["arms"].values())
    if paid!=17920:
        raise AssertionError("T17_TOTAL_ACTION_CUSTODY_DRIFT")
    mean=lambda arm,mark,key:round(statistics.mean(
        w["arms"][arm]["audits"][str(mark)][key] for w in worlds),12)
    aggregate={arm:{str(mark):{k:mean(arm,mark,k) for k in ("regret","mse")}
                    for mark in AUDITS} for arm in ARMS}
    correctA=0
    correctC=0
    falseC=0
    per_world_wins={128:0,160:0}
    jnames=("forgetting_rls","integer_recurrent")
    for w in worlds:
        j=w["lesion"]
        ar=w["arms"]["causal_modules"]["audits"]["128"]["route_births"]
        cr=w["arms"]["causal_modules"]["audits"]["160"]["route_births"]
        correctA+=int(any(r[j] is not None and r[j]<64 for r in ar))
        # C requires module reuse of B's changed row plus A's intact row.
        intact=(j+1)%3
        correctC+=int(any(r[j] is not None and 64<=r[j]<128 and
                          r[intact] is not None and r[intact]<64 for r in cr))
        novel=(j+2)%3
        falseC+=int(any(r[novel] is not None for r in cr))
        for mark in AUDITS:
            candid=w["arms"]["causal_modules"]["audits"][str(mark)]["regret"]
            best=min(w["arms"][v]["audits"][str(mark)]["regret"] for v in jnames)
            per_world_wins[mark]+=int(candid<best)
    ratios={a:statistics.median(
        w["arms"]["causal_modules"]["cpu_ns"]/
        max(1,w["arms"][a]["cpu_ns"]) for w in worlds)
        for a in ("forgetting_rls","no_archive")}
    gates={}
    for phase,mark in (("return_A",128),("unseen_C",160)):
        cand=mean("causal_modules",mark,"regret")
        strong=min(mean(a,mark,"regret") for a in jnames)
        gates[phase+"_vs_strong"]=cand<=strong-.005
        for arm in ("no_archive","random_route"):
            gates[phase+"_vs_"+arm]=cand<=mean(arm,mark,"regret")-.005
        gates[phase+"_world_wins"]=per_world_wins[mark]>=12
    gates["return_A_reuse"]=correctA>=12
    gates["C_factorized_reuse"]=correctC>=12
    gates["C_false_reuse"]=falseC<=2
    gates["cpu_rls"]=ratios["forgetting_rls"]<=2.5
    gates["cpu_no_archive"]=ratios["no_archive"]<=2.0
    primary=all(gates.values())
    partial=(correctA>0 or correctC>0 or any(
        mean("causal_modules",m,"regret")<mean(a,m,"regret")
        for m in AUDITS for a in ("no_archive","random_route")+jnames))
    return {"schema":SCHEMA,"freeze_sha":FREEZE,"parent_sha":PARENT,
            "world_count":len(worlds),"paid_steps":paid,
            "paid_training_steps":12800,"paid_audit_steps":5120,
            "controls":list(ARMS),"primary_gates":gates,
            "primary_pass":primary,
            "classification":("DEVELOPMENT_SIGNAL_ONLY" if primary else
                             "MIXED_DEV" if partial else "NEGATIVE_DEV"),
            "scientific_acceptance":"UNVERIFIED","native_model_changed":False,
            "return_A_reactivation_count":correctA,
            "unfamiliar_C_composition_count":correctC,
            "unfamiliar_C_false_route_count":falseC,
            "world_win_counts":{str(k):v for k,v in per_world_wins.items()},
            "cpu_median_ratio":{k:round(v,6) for k,v in ratios.items()},
            "aggregate":aggregate,"worlds":worlds}

if __name__=="__main__":
    print(canonical(run()))

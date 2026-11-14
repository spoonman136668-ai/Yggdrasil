"""DG1-IV18: preregistered two-probe causal veto and two-step paid decision transfer, DEV only.

No native Yggdrasil model, official research loop or accepted reference is modified.
Do not invoke run() on registered seeds before the frozen source is committed.
"""
import hashlib
import json
import math
import random
import statistics
import time

FREEZE = "20b0af804ffbd04d7e3d22cdf39b3c82a14d7093"
PARENT = "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9"
SEEDS = tuple(range(520001, 520017))
AUDITS = (128, 160)
ARMS = ("certified_gate", "ungated_route", "sham_route",
        "no_archive", "forgetting_rls", "integer_recurrent")
MANIFEST = "37b70a87720bfbc26a7fe05f6460cbf6c1607a7f07cdb2b04eb85c452f2a10fb"
SCHEMA = "yggdrasil.dg1-iv18-original.v1"


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


Q=4096


def divr(n,d):
    if d<=0:
        raise ValueError("IV18_INVALID_DIVISOR")
    sign=-1 if n<0 else 1
    return sign*((abs(int(n))+d//2)//d)


def features(x, action):
    if (len(x)!=3 or any(type(v) is not int or abs(v)>8*Q for v in x)
            or type(action) is not int or action not in range(6)):
        raise ValueError("IV18_INVALID_OBSERVATION_OR_ACTION")
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
            raise ValueError("IV18_INVALID_PHASE")
        mat=self.matrices[phase]
        axis,sgn=divmod(action,2)
        motor=Q//3 if sgn==0 else -(Q//3)
        out=[divr(sum(mat[j][k]*x[k] for k in range(3)),Q)
             +(motor if j==axis else 0) for j in range(3)]
        if phase==3:
            novel=(self.lesion+2)%3
            out[novel]+=divr(x[(novel+1)%3]*x[(novel+2)%3],3*Q)
        return out

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
            raise AssertionError("IV18_BAD_RLS_CURVATURE")
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
            raise ValueError("IV18_INVALID_REAL_CONSEQUENCE")
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
                            if self.kind=="_never_active_random_learning_" else viable[0][1])
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
    if arm in ("certified_gate","ungated_route","sham_route","no_archive"): return Repair(arm)
    if arm=="forgetting_rls": return Regression()
    if arm=="integer_recurrent": return IntegerRecurrent()
    raise ValueError("IV18_UNKNOWN_ARM")


def snapshot(model):
    payload=canonical(model.dump()).encode()
    if len(payload)>65536: raise AssertionError("IV18_CHECKPOINT_TOO_LARGE")
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
        raise AssertionError("IV18_NONCANONICAL_CHECKPOINT")
    return model


def probe_routes(model,probes,seed,mark,episode):
    """Two charged action-consequence probes, no hidden regime or audit training."""
    if not isinstance(model,Repair):
        return None
    chosen=[]
    for j,row in enumerate(model.rows):
        slots=row["slots"]
        if model.kind=="no_archive":
            ix=0
        else:
            viable=[(statistics.mean(
                    (slot.predict(features(x,a))-y[j]/Q)**2
                    for x,a,y in probes), k)
                    for k,slot in enumerate(slots) if slot.n>=12]
            viable.sort()
            if model.kind=="sham_route":
                mature=[k for _,k in viable]
                ix=(random.Random(seed*200000+mark*23+episode*11+j).choice(mature)
                    if mature else None)
            elif model.kind=="ungated_route":
                ix=viable[0][1] if viable else None
            else:
                ix=viable[0][1] if viable and viable[0][0]<=.0049 else None
        chosen.append(ix)
    return chosen


def conditioned_predict(model,x,a,routes):
    if routes is None or not isinstance(model,Repair):
        return model.predict(x,a)
    f=features(x,a)
    out=[]
    for j,row in enumerate(model.rows):
        ix=routes[j]
        if ix is None:
            mature=[slot.predict(f) for slot in row["slots"] if slot.n>=12]
            out.append(statistics.median(mature) if mature else
                       row["slots"][row["active"]].predict(f))
        else:
            out.append(row["slots"][ix].predict(f))
    return out


def audit(model,world,seed,mark):
    """Each episode: two real probes and two sequential selected real goal actions."""
    rng=random.Random((seed*141067)^mark)
    phase=2 if mark==128 else 3
    regrets=[]
    mses=[]
    choices=[]
    routes=[]
    for ep in range(12):
        x=[rng.randint(-Q,Q) for _ in range(3)]
        x2=[rng.randint(-Q,Q) for _ in range(3)]
        target=[rng.randint(-Q,Q) for _ in range(3)]
        probe0=(seed+ep)%6
        probe1=(probe0+3)%6
        y0=world.step(x,probe0,phase)
        y1=world.step(x2,probe1,phase)
        probes=((x,probe0,y0),(x2,probe1,y1))
        routing=probe_routes(model,probes,seed,mark,ep)
        bias=[statistics.mean(
            y[j]/Q-conditioned_predict(model,px,pa,routing)[j]
            for px,pa,y in probes) for j in range(3)]
        def predicted(px,pa):
            v=conditioned_predict(model,px,pa,routing)
            return [round(Q*(v[j]+bias[j])) for j in range(3)]
        scored=[]
        for a in range(6):
            xa=predicted(x,a)
            for b in range(6):
                xb=predicted(xa,b)
                scored.append((dist(xb,target),a,b))
        _,a,b=min(scored)
        real1=world.step(x,a,phase)
        real2=world.step(real1,b,phase)
        oracle=min(dist(world.next(world.next(x,aa,phase),bb,phase),target)
                   for aa in range(6) for bb in range(6))
        regret=dist(real2,target)-oracle
        regrets.append(regret)
        estimate=predicted(predicted(x,a),b)
        mses.append(dist(estimate,real2)/3)
        choices.append([probe0,probe1,a,b,round(regret,12),round(mses[-1],12)])
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
                raise AssertionError("IV18_COLD_RESTORE_MISMATCH")
            model=twin
            cold.append(len(raw))
        mark=t+1
        if mark in AUDITS:
            start=time.perf_counter_ns()
            metrics[str(mark)]=audit(model,world,seed,mark)
            cpu_ns+=time.perf_counter_ns()-start
    if world.charged!=256 or model.count!=160:
        raise AssertionError("IV18_PAID_EVENT_BUDGET_MISMATCH")
    return {"arm":arm,"seed":seed,"paid_steps":world.charged,
            "charged_observations":160,"audits":metrics,
            "train_trace_sha256":digest(trace),"cold_bytes":cold,
            "final_checkpoint_sha256":hashlib.sha256(snapshot(model)).hexdigest(),
            "switches":getattr(model,"switches",[]),"cpu_ns":cpu_ns}

def run():
    manifest={"schema":"yggdrasil.dg1-iv18-seeds.v1",
              "world_seeds":list(SEEDS),"phase_steps":[64,64,32],
              "audit_episodes_per_mark":12,"audit_marks":list(AUDITS),
              "probe_actions_per_audit":2,"goal_actions_per_audit":2,
              "arms":list(ARMS)}
    if digest(manifest)!=MANIFEST:
        raise AssertionError("IV18_SEED_MANIFEST_DRIFT")
    worlds=[]
    for seed in SEEDS:
        arms={a:one_arm(seed,a) for a in ARMS}
        if len({v["train_trace_sha256"] for v in arms.values()})!=1:
            raise AssertionError("IV18_DIFFERENT_PHYSICAL_INFORMATION")
        worlds.append({"seed":seed,"lesion":seed%3,"arms":arms})
    total=sum(v["paid_steps"] for w in worlds for v in w["arms"].values())
    if total!=24576:
        raise AssertionError("IV18_TOTAL_ACTION_CUSTODY_DRIFT")
    mean=lambda arm,mark,key:round(statistics.mean(
        w["arms"][arm]["audits"][str(mark)][key] for w in worlds),12)
    aggregate={arm:{str(mark):{k:mean(arm,mark,k) for k in ("regret","mse")}
                    for mark in AUDITS} for arm in ARMS}
    recall=0
    composition=0
    false_route=0
    wins={128:0,160:0}
    conventional=("forgetting_rls","integer_recurrent")
    for w in worlds:
        lesion=w["lesion"]
        ca=w["arms"]["certified_gate"]["audits"]["128"]["route_births"]
        cc=w["arms"]["certified_gate"]["audits"]["160"]["route_births"]
        recall+=int(any(r[lesion] is not None and r[lesion]<64 for r in ca))
        intact=(lesion+1)%3
        composition+=int(any(
            r[lesion] is not None and 64<=r[lesion]<128
            and r[intact] is not None and r[intact]<64 for r in cc))
        novel=(lesion+2)%3
        false_route+=int(any(r[novel] is not None for r in cc))
        for mark in AUDITS:
            value=w["arms"]["certified_gate"]["audits"][str(mark)]["regret"]
            best=min(w["arms"][c]["audits"][str(mark)]["regret"]
                     for c in conventional)
            wins[mark]+=int(value<best)
    ratios={arm:statistics.median(
        w["arms"]["certified_gate"]["cpu_ns"]/max(1,w["arms"][arm]["cpu_ns"])
        for w in worlds)
        for arm in ("forgetting_rls","ungated_route")}
    gates={}
    for phase,mark in (("return_A",128),("unseen_C",160)):
        candidate=mean("certified_gate",mark,"regret")
        best=min(mean(c,mark,"regret") for c in conventional)
        gates[phase+"_vs_strong"]=candidate<=best-.01
        for control in ("ungated_route","sham_route","no_archive"):
            gates[phase+"_vs_"+control]=(
                candidate<=mean(control,mark,"regret")-.01)
        gates[phase+"_world_wins"]=wins[mark]>=12
    gates["return_A_memory_recovery"]=recall>=12
    gates["C_factorized_known_reuse"]=composition>=12
    gates["C_false_novel_routes"]=false_route<=2
    gates["cpu_vs_rls"]=ratios["forgetting_rls"]<=3
    gates["cpu_vs_ungated"]=ratios["ungated_route"]<=2.5
    primary=all(gates.values())
    partial=(recall>0 or composition>0 or any(
        mean("certified_gate",mark,"regret")<mean(c,mark,"regret")
        for mark in AUDITS for c in ("ungated_route","sham_route","no_archive")+conventional))
    return {"schema":SCHEMA,"freeze_sha":FREEZE,"parent_sha":PARENT,
            "world_count":len(worlds),"paid_steps":total,
            "paid_training_steps":15360,"paid_audit_steps":9216,
            "controls":list(ARMS),"primary_gates":gates,"primary_pass":primary,
            "classification":("DEVELOPMENT_SIGNAL_ONLY" if primary else
                             "MIXED_DEV" if partial else "NEGATIVE_DEV"),
            "scientific_acceptance":"UNVERIFIED","native_model_changed":False,
            "return_A_reactivation_count":recall,
            "unfamiliar_C_composition_count":composition,
            "unfamiliar_C_false_route_count":false_route,
            "world_win_counts":{str(k):v for k,v in wins.items()},
            "cpu_median_ratio":{k:round(v,6) for k,v in ratios.items()},
            "aggregate":aggregate,"worlds":worlds}

if __name__=="__main__":
    print(canonical(run()))

"""DG1-CR16: prospective synthetic continuous causal repair, DEV only.

No native Yggdrasil model, official research loop or accepted reference is modified.
Do not invoke run() before the registered preregistration commit.
"""
import hashlib
import json
import math
import random
import statistics
import time

FREEZE = "cd2823483a9d984915e887cd6a076a15c0a59b68"
PARENT = "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9"
SEEDS = tuple(range(310001, 310017))
AUDITS = (72, 144, 168, 192)
ARMS = ("selective", "no_archive", "random_repair",
        "forgetting_rls", "trained_recurrent")
MANIFEST = "24ad8baaca087042d75f04ac1bc64ab745de3dfbfbc2135a0733718b1d7e94d0"
SCHEMA = "yggdrasil.dg1-cr16-original.v1"


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


def features(x, action):
    if (len(x) != 3 or any(not math.isfinite(float(v)) for v in x)
            or type(action) is not int or action not in range(6)):
        raise ValueError("CR16_INVALID_OBSERVATION_OR_ACTION")
    return list(x) + [float(k == action) for k in range(6)] + [1.0]


def dist(a, b):
    return sum((u-v)**2 for u, v in zip(a,b))


class World:
    """Three-channel continuous physical state; private causal edges never reach a learner."""
    def __init__(self, seed):
        r = random.Random(seed)
        pa = []
        for j in range(3):
            row = [0.0] * 3
            row[j] = .58
            row[(j+1+(seed%2))%3] = r.choice((-.32,-.24,.24,.32))
            pa.append(row)
        b = [x[:] for x in pa]
        self.lesion = seed%3
        j = self.lesion
        b[j] = [0.0]*3
        b[j][j] = .58
        old = next(k for k in range(3) if k != j and pa[j][k] != 0)
        other = next(k for k in range(3) if k != j and k != old)
        b[j][other] = (-1 if pa[j][old]>0 else 1)*.32
        c = [x[:] for x in pa]
        c[j] = b[j][:]
        novel = (j+2)%3
        c[novel] = [0.0]*3
        c[novel][novel] = .58
        c[novel][(novel+2)%3] = -.35 if pa[novel][(novel+1)%3]>=0 else .35
        self.matrices = (pa,b,pa,c)
        self.charged = 0

    @staticmethod
    def phase(step):
        if step<72: return 0
        if step<144: return 1
        if step<168: return 2
        return 3

    def next(self,x,action,phase):
        if type(phase) is not int or phase not in range(4):
            raise ValueError("CR16_INVALID_PHASE")
        features(x,action)
        mat = self.matrices[phase]
        axis,sign = divmod(action,2)
        motor = .35*(1 if sign==0 else -1)
        return [sum(mat[j][k]*x[k] for k in range(3))+
                (motor if j==axis else 0.0) for j in range(3)]

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
            raise AssertionError("CR16_BAD_RLS_CURVATURE")
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
        if len(y)!=3 or any(not math.isfinite(v) for v in y):
            raise ValueError("CR16_INVALID_REAL_CONSEQUENCE")
        for j,r in enumerate(self.rows):
            old=r["slots"][r["active"]]
            error=abs(old.predict(f)-y[j])
            witness=r["witness"]
            witness.append([f[:],float(y[j]),error])
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
                            if self.kind=="random_repair" else viable[0][1])
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
            r["slots"][r["active"]].fit(f,y[j])
        self.count+=1

    def dump(self):
        return {"kind":self.kind,"count":self.count,"switches":self.switches,
                "rng":self.rng.getstate()[1][:5],  # record-only, never used to restore PRNG
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
        for i in range(3): self.rows[i].fit(f,y[i])
        self.count+=1

    def dump(self):
        return {"kind":self.kind,"count":self.count,
                "rows":[vars(m) for m in self.rows]}


class Recurrent:
    """All trainable RNN matrices, biases, and readout updated on every transition."""
    def __init__(self):
        self.kind="trained_recurrent"
        r=random.Random(90129)
        self.wx=[[r.uniform(-.08,.08) for _ in range(10)] for _ in range(8)]
        self.wh=[[r.uniform(-.04,.04) for _ in range(8)] for _ in range(8)]
        self.v=[[r.uniform(-.08,.08) for _ in range(8)] for _ in range(3)]
        self.b=[0.0]*8
        self.c=[0.0]*3
        self.h=[0.0]*8
        self.count=0

    def forward(self,f):
        nh=[math.tanh(sum(wi*xi for wi,xi in zip(self.wx[i],f))+
                      sum(wi*hi for wi,hi in zip(self.wh[i],self.h))+
                      self.b[i]) for i in range(8)]
        pred=[sum(wi*hi for wi,hi in zip(self.v[j],nh))+self.c[j]
              for j in range(3)]
        return nh,pred

    def predict(self,x,a):
        return self.forward(features(x,a))[1]

    def observe(self,x,a,y):
        f=features(x,a)
        prev=self.h[:]
        nh,pred=self.forward(f)
        # Online one-step truncated recurrent backprop; all weights trainable.
        residual=[max(-2,min(2,pred[j]-y[j])) for j in range(3)]
        dh=[(1-nh[i]**2)*sum(self.v[j][i]*residual[j] for j in range(3))
            for i in range(8)]
        rate=.035
        for j in range(3):
            for i in range(8): self.v[j][i]-=rate*residual[j]*nh[i]
            self.c[j]-=rate*residual[j]
        for i in range(8):
            for k in range(10): self.wx[i][k]-=rate*dh[i]*f[k]
            for k in range(8): self.wh[i][k]-=rate*dh[i]*prev[k]
            self.b[i]-=rate*dh[i]
        self.h=nh
        self.count+=1

    def dump(self):
        return {k:v for k,v in vars(self).items()}


def learner(arm):
    if arm in ("selective","no_archive","random_repair"): return Repair(arm)
    if arm=="forgetting_rls": return Regression()
    if arm=="trained_recurrent": return Recurrent()
    raise ValueError("CR16_UNKNOWN_ARM")


def snapshot(model):
    payload=canonical(model.dump()).encode()
    if len(payload)>65536: raise AssertionError("CR16_CHECKPOINT_TOO_LARGE")
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
        # deterministic generator consumed only if randomized archived selection.
        # Reconstruct via exact replay count would be unsafe; persist full RNG state below.
        if kind=="random_repair":
            raise AssertionError("CR16_RANDOM_REPAIR_CHECKPOINT_REQUIRES_RNG_STATE")
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
        raise AssertionError("CR16_NONCANONICAL_CHECKPOINT")
    return model


def audit(model,world,seed,mark):
    r=random.Random((seed*141067)^mark)
    phase={72:0,144:1,168:2,192:3}[mark]
    regrets=[]
    mses=[]
    choices=[]
    for _ in range(12):
        x=[r.uniform(-.8,.8) for _ in range(3)]
        target=[r.uniform(-.8,.8) for _ in range(3)]
        predictions=[model.predict(x,a) for a in range(6)]
        action=min(range(6),key=lambda a:(dist(predictions[a],target),a))
        y=world.step(x,action,phase)
        counterfactual=min(dist(world.next(x,a,phase),target) for a in range(6))
        regrets.append(dist(y,target)-counterfactual)
        mses.append(dist(predictions[action],y)/3)
        choices.append([action,round(regrets[-1],12),round(mses[-1],12)])
    return {"regret":round(statistics.mean(regrets),12),
            "mse":round(statistics.mean(mses),12),"choices":choices}


def one_arm(seed,arm):
    world=World(seed)
    model=learner(arm)
    rng=random.Random(seed^0xF12D)
    trace=[]
    metrics={}
    cold=[]
    state=[0.0]*3
    cpu_ns=0
    for t in range(192):
        if t%8==0:
            state=[rng.uniform(-.8,.8) for _ in range(3)]
        before=state[:]
        action=t%6
        y=world.step(before,action,World.phase(t))
        start=time.perf_counter_ns()
        model.observe(before,action,y)
        cpu_ns+=time.perf_counter_ns()-start
        trace.append([t,[round(v,12) for v in before],action,
                      [round(v,12) for v in y]])
        state=y
        if t in (70,142,166):
            raw=snapshot(model)
            twin=restore(raw)
            probe=[.13,-.24,.31]
            if (snapshot(twin)!=raw or
                    any(twin.predict(probe,a)!=model.predict(probe,a)
                        for a in range(6))):
                raise AssertionError("CR16_COLD_RESTORE_MISMATCH")
            model=twin
            cold.append(len(raw))
        mark=t+1
        if mark in AUDITS:
            start=time.perf_counter_ns()
            metrics[str(mark)]=audit(model,world,seed,mark)
            cpu_ns+=time.perf_counter_ns()-start
    if world.charged!=240 or model.count!=192:
        raise AssertionError("CR16_PAID_EVENT_BUDGET_MISMATCH")
    birth_info=None
    if isinstance(model,Repair):
        birth_info=[r["slots"][r["active"]].birth for r in model.rows]
    return {"arm":arm,"seed":seed,"paid_steps":world.charged,
            "charged_observations":192,"audits":metrics,
            "train_trace_sha256":digest(trace),"cold_bytes":cold,
            "final_checkpoint_sha256":hashlib.sha256(snapshot(model)).hexdigest(),
            "active_slot_births":birth_info,"switches":getattr(model,"switches",[]),
            "cpu_ns":cpu_ns}


def run():
    manifest={"schema":"yggdrasil.dg1-cr16-seeds.v1","world_seeds":list(SEEDS),
              "training_steps_per_world":192,
              "audit_cases_per_checkpoint":12,
              "checkpoints":list(AUDITS)}
    if digest(manifest)!=MANIFEST: raise AssertionError("CR16_SEED_MANIFEST_DRIFT")
    worlds=[]
    for seed in SEEDS:
        arms={a:one_arm(seed,a) for a in ARMS}
        if len({a["train_trace_sha256"] for a in arms.values()})!=1:
            raise AssertionError("CR16_DIFFERENT_PHYSICAL_INFORMATION")
        worlds.append({"seed":seed,"lesion":seed%3,"arms":arms})
    paid=sum(arm["paid_steps"] for w in worlds for arm in w["arms"].values())
    if paid!=19200:
        raise AssertionError("CR16_TOTAL_ACTION_CUSTODY_DRIFT")
    mean=lambda arm,mark,key:round(statistics.mean(
        w["arms"][arm]["audits"][str(mark)][key] for w in worlds),12)
    aggregate={arm:{str(mark):{k:mean(arm,mark,k) for k in ("regret","mse")}
                     for mark in AUDITS} for arm in ARMS}
    recall=sum(w["arms"]["selective"]["active_slot_births"][w["lesion"]]<72
               for w in worlds)
    composed=sum(
        72<=w["arms"]["selective"]["active_slot_births"][w["lesion"]]<144
        and w["arms"]["selective"]["active_slot_births"][(w["lesion"]+1)%3]<72
        and w["arms"]["selective"]["active_slot_births"][(w["lesion"]+2)%3]>=168
        for w in worlds
    )
    ratios={
        arm:statistics.median(
            w["arms"]["selective"]["cpu_ns"]/
            max(1,w["arms"][arm]["cpu_ns"]) for w in worlds)
        for arm in ("forgetting_rls","no_archive")
    }
    gates={}
    for phase,mark in (("return_A",168),("unseen_C",192)):
        cand=mean("selective",mark,"regret")
        best=min(mean("forgetting_rls",mark,"regret"),
                 mean("trained_recurrent",mark,"regret"))
        gates[phase+"_strong_control"]=cand<=best-.01
        for arm in ("no_archive","random_repair"):
            gates[phase+"_vs_"+arm]=cand<=mean(arm,mark,"regret")-.01
        gates[phase+"_predictive_mse"]=(
            mean("selective",mark,"mse")<=mean("forgetting_rls",mark,"mse"))
    gates["genuine_return_A_reuse"]=recall>=8
    gates["genuine_unfamiliar_C_composition"]=composed>=8
    gates["cpu_vs_rls"]=ratios["forgetting_rls"]<=2.5
    gates["cpu_vs_no_archive"]=ratios["no_archive"]<=2.0
    signal=all(gates.values())
    partial=(recall>0 or composed>0 or any(
        mean("selective",m,"regret")<mean(a,m,"regret")
        for m in (168,192)
        for a in ("no_archive","random_repair","forgetting_rls","trained_recurrent")
    ))
    return {"schema":SCHEMA,"freeze_sha":FREEZE,"parent_sha":PARENT,
            "world_count":16,"paid_steps":paid,"paid_training_steps":15360,
            "paid_audit_steps":3840,"controls":list(ARMS),
            "primary_gates":gates,"primary_pass":signal,
            "classification":("DEVELOPMENT_SIGNAL_ONLY" if signal else
                              "MIXED_DEV" if partial else "NEGATIVE_DEV"),
            "scientific_acceptance":"UNVERIFIED","native_model_changed":False,
            "return_A_reactivation_count":recall,
            "unfamiliar_C_composition_count":composed,
            "cpu_median_ratio":{k:round(v,6) for k,v in ratios.items()},
            "aggregate":aggregate,"worlds":worlds}


if __name__=="__main__":
    print(canonical(run()))

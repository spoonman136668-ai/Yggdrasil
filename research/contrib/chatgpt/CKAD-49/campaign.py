"""CKAD49 research-only source-trained causal feature/operator discovery.

Not accepted binary NativeEpisodeExperience. Hidden physical features are
simulator/evaluator data only. Two genuine transitions and one reward train
each separate learner from the same public episode; no evaluator truth enters.
"""
from __future__ import annotations
import argparse, hashlib, json, math, random, time

SCHEMA="yggdrasil.ckad49.learned_exception_operator.v1"
PREREG="63d9ff3b5cabbe932f70ad5452c86d24cfb74c7f"
DEV=(49111,49112)
PILOT=(49211,49212)
PRIMARY=(49311,49312,49313)
OLD=80
NOVEL_END=192
TOTAL=256
ALPHA=.25
PROB=.9
WRONG=.1/3
OPERATORS=("xor","add")
STRUCTURES=tuple((op,mask) for op in OPERATORS for mask in range(8))
RESTRICTED=tuple(("xor",mask) for mask in (0,3,5,6))
ARMS=("discovered_feature_native","exact_full_BMA","unrestricted_tabular","old_XOR_restricted","uniform_negative")
PROBES=(80,96,112,128,144,160,176,192,208,224,240)
PHASES={"early_novel":(80,96),"late_novel":(144,160,176),"cold_return":(192,208,224,240),
        "pooled_late_and_cold":(144,160,176,192,208,224,240)}

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)

def sha(x):
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

def four(x):
    if type(x) is not int or x not in (0,1,2,3):raise ValueError("CKAD49_FOUR_STATE_OR_ACTION")
    return x

def group(mask,state):
    four(state)
    return int(bool(mask&(1<<state))) if mask else 0

def effect(op,state,delta):
    four(state);four(delta)
    if op=="xor":return state^delta
    if op=="add":return (state+delta)%4
    raise ValueError("CKAD49_OPERATOR")

def inverse(op,state,target):
    four(target)
    if op=="xor":return state^target
    if op=="add":return (target-state)%4
    raise ValueError("CKAD49_OPERATOR")

def private_world(seed,world):
    if seed not in DEV and seed!=0:raise ValueError("CKAD49_ONLY_REGISTERED_DEV")
    if world not in (0,1):raise ValueError("CKAD49_WORLD")
    rng=random.Random(int(sha(f"ckad49-source|{seed}|{world}"),16))
    m=list(range(4));rng.shuffle(m)
    return rng,{"world":world,"operator":"add" if world==0 else "xor",
                "mask":1 if world==0 else 7,
                "maps":(tuple(m),tuple(m[(i+1)%4] for i in range(4)))}

def physical_distribution(secret,s,action):
    mask=secret["mask"]
    d=secret["maps"][group(mask,s)][action]
    correct=effect(secret["operator"],s,d)
    return tuple(PROB if x==correct else WRONG for x in range(4))

def private_reward(world,state):
    truth=(state in (0,3)) if world==0 else (state in (1,2))
    return .9 if truth else .1

def private_query(secret,s,a,b):
    return sum(p1*p2*private_reward(secret["world"],t)
               for mid,p1 in enumerate(physical_distribution(secret,s,a))
               for t,p2 in enumerate(physical_distribution(secret,mid,b)))

def source(seed,world):
    rng,secret=private_world(seed,world)
    episodes=[]
    for t in range(TOTAL):
        s=rng.randrange(4)
        available=(0,1) if t<OLD or t>=NOVEL_END else (2,3)
        a,b=rng.choice(available),rng.choice(available)
        p=physical_distribution(secret,s,a)
        intended=p.index(PROB)
        u=rng.random();wrong=rng.randrange(3)
        mid=intended if u<PROB else [j for j in range(4) if j!=intended][wrong]
        p=physical_distribution(secret,mid,b)
        intended=p.index(PROB)
        u=rng.random();wrong=rng.randrange(3)
        terminal=intended if u<PROB else [j for j in range(4) if j!=intended][wrong]
        y=int(rng.random()<private_reward(world,terminal))
        episodes.append((sha(f"ckad49-genuine-source|{seed}|{world}|{t}"),
                         {"s0":s,"a1":a,"s1":mid,"a2":b,"s2":terminal,"y":y}))
    return episodes,secret

def validate(ident,row):
    if type(ident) is not str or len(ident)!=64 or any(c not in "0123456789abcdef" for c in ident):
        raise ValueError("CKAD49_ID")
    if type(row) is not dict or set(row)!={"s0","a1","s1","a2","s2","y"}:
        raise ValueError("CKAD49_ROW")
    for k in ("s0","a1","s1","a2","s2"):four(row[k])
    if type(row["y"]) is not int or row["y"] not in (0,1):raise ValueError("CKAD49_REWARD")

class Structural:
    def __init__(self,arm):
        if arm not in ("discovered_feature_native","exact_full_BMA","old_XOR_restricted"):
            raise ValueError("CKAD49_ARM")
        self.arm=arm
        self.structures=STRUCTURES if arm!="old_XOR_restricted" else RESTRICTED
        self.counts=[[[[0]*4 for _ in range(2)] for _ in range(4)] for _ in self.structures]
        prior=[2 if mask==0 else 1 for _,mask in self.structures]
        self.weights=[p/sum(prior) for p in prior]
        self.reward=[[0,0] for _ in range(4)]
        self.receipts={};self.ledger=[];self.n=0;self.initial=None

    def transition(self,i,s,a):
        op,mask=self.structures[i]
        counts=self.counts[i][a][group(mask,s)]
        den=sum(counts)+4*ALPHA
        return tuple((counts[inverse(op,s,target)]+ALPHA)/den for target in range(4))

    def selected(self):
        ix=max(range(len(self.weights)),key=lambda i:self.weights[i])
        return self.structures[ix],self.weights[ix]

    def read_weights(self):
        if self.arm=="discovered_feature_native":
            ix=max(range(len(self.weights)),key=lambda i:self.weights[i])
            if self.weights[ix]>=.80:
                return tuple(float(j==ix) for j in range(len(self.weights)))
        return tuple(self.weights)

    def forecast(self,s,a,b):
        four(s);four(a);four(b)
        r=[(yes+1)/(no+yes+2) for no,yes in self.reward]
        value=0.0
        for i,w in enumerate(self.read_weights()):
            if w==0:continue
            for mid,p1 in enumerate(self.transition(i,s,a)):
                for fin,p2 in enumerate(self.transition(i,mid,b)):
                    value+=w*p1*p2*r[fin]
        return value

    def observe(self,ident,row):
        validate(ident,row)
        receipt=sha(canonical(row))
        if ident in self.receipts:
            if self.receipts[ident]!=receipt:raise ValueError("CKAD49_SOURCE_ID_CONFLICT")
            return self
        if self.n>=TOTAL:raise ValueError("CKAD49_BUDGET")
        for s,a,next_state in ((row["s0"],row["a1"],row["s1"]),(row["s1"],row["a2"],row["s2"])):
            scores=[w*self.transition(i,s,a)[next_state] for i,w in enumerate(self.weights)]
            z=sum(scores)
            if not z>0 or not math.isfinite(z):raise AssertionError("CKAD49_BAYES_INVALID")
            self.weights=[x/z for x in scores]
            for i,(op,mask) in enumerate(self.structures):
                self.counts[i][a][group(mask,s)][inverse(op,s,next_state)]+=1
        self.reward[row["s2"]][row["y"]]+=1
        self.receipts[ident]=receipt;self.ledger.append([ident,receipt]);self.n+=1
        if self.n==OLD:self.initial=sha(canonical(self.ledger))
        return self

    def checkpoint(self):
        return canonical({"schema":SCHEMA,"arm":self.arm,"structures":self.structures,
            "counts":self.counts,"weights":self.weights,"reward":self.reward,
            "receipts":self.receipts,"ledger":self.ledger,"n":self.n,"initial":self.initial})

    @classmethod
    def restore(cls,raw,expected):
        if sha(raw)!=expected:raise ValueError("CKAD49_COLD_SHA")
        x=json.loads(raw)
        if x["schema"]!=SCHEMA:raise ValueError("CKAD49_COLD_SCHEMA")
        model=cls(x["arm"])
        if [list(v) for v in model.structures]!=x["structures"]:
            raise ValueError("CKAD49_COLD_STRUCTURES")
        for k in ("counts","weights","reward","receipts","ledger","n"):setattr(model,k,x[k])
        model.initial=x["initial"]
        if model.n!=len(model.receipts) or model.n!=len(model.ledger) or model.n>TOTAL:
            raise ValueError("CKAD49_COLD_LEDGER")
        if model.n>=OLD and sha(canonical(model.ledger[:OLD]))!=model.initial:
            raise ValueError("CKAD49_COLD_PRIOR_SOURCE")
        if abs(sum(model.weights)-1)>1e-12:raise ValueError("CKAD49_COLD_WEIGHTS")
        if sum(sum(v) for v in model.reward)!=model.n:raise ValueError("CKAD49_COLD_REWARDS")
        if any(sum(sum(sum(c) for c in action) for action in structure)!=2*model.n
               for structure in model.counts):raise ValueError("CKAD49_COLD_EFFECTS")
        if model.checkpoint()!=raw:raise ValueError("CKAD49_COLD_BYTES")
        return model

class Tabular:
    def __init__(self):
        self.arm="unrestricted_tabular"
        self.counts=[[[0]*4 for _ in range(4)] for _ in range(4)]
        self.reward=[[0,0] for _ in range(4)]
        self.receipts={};self.ledger=[];self.n=0;self.initial=None

    def transition(self,s,a):
        counts=self.counts[s][a];den=sum(counts)+4*ALPHA
        return [(v+ALPHA)/den for v in counts]

    def forecast(self,s,a,b):
        four(s);four(a);four(b)
        r=[(yes+1)/(no+yes+2) for no,yes in self.reward]
        return sum(p1*p2*r[fin] for mid,p1 in enumerate(self.transition(s,a))
                   for fin,p2 in enumerate(self.transition(mid,b)))

    def observe(self,ident,row):
        validate(ident,row);receipt=sha(canonical(row))
        if ident in self.receipts:
            if self.receipts[ident]!=receipt:raise ValueError("CKAD49_SOURCE_ID_CONFLICT")
            return self
        if self.n>=TOTAL:raise ValueError("CKAD49_BUDGET")
        self.counts[row["s0"]][row["a1"]][row["s1"]]+=1
        self.counts[row["s1"]][row["a2"]][row["s2"]]+=1
        self.reward[row["s2"]][row["y"]]+=1
        self.receipts[ident]=receipt;self.ledger.append([ident,receipt]);self.n+=1
        if self.n==OLD:self.initial=sha(canonical(self.ledger))
        return self

    def checkpoint(self):
        return canonical({"schema":SCHEMA+".tabular","arm":self.arm,"counts":self.counts,
          "reward":self.reward,"receipts":self.receipts,"ledger":self.ledger,
          "initial":self.initial,"n":self.n})

    @classmethod
    def restore(cls,raw,expected):
        if sha(raw)!=expected:raise ValueError("CKAD49_COLD_SHA")
        x=json.loads(raw)
        if x["schema"]!=SCHEMA+".tabular":raise ValueError("CKAD49_COLD_SCHEMA")
        obj=cls()
        for key in ("counts","reward","receipts","ledger","initial","n"):setattr(obj,key,x[key])
        if obj.n!=len(obj.ledger) or obj.n!=len(obj.receipts):raise ValueError("CKAD49_COLD_LEDGER")
        if obj.n>=OLD and sha(canonical(obj.ledger[:OLD]))!=obj.initial:
            raise ValueError("CKAD49_COLD_PRIOR_SOURCE")
        if sum(sum(sum(c) for c in act) for act in obj.counts)!=2*obj.n:
            raise ValueError("CKAD49_COLD_EFFECTS")
        if sum(sum(v) for v in obj.reward)!=obj.n:raise ValueError("CKAD49_COLD_REWARDS")
        if obj.checkpoint()!=raw:raise ValueError("CKAD49_COLD_BYTES")
        return obj

def custody(model,last,actual_actions):
    raw=model.checkpoint()
    if type(model).restore(raw,sha(raw)).checkpoint()!=raw:
        raise AssertionError("CKAD49_COLD_INVALID")
    if model.n!=TOTAL or sha(canonical(model.ledger[:OLD]))!=model.initial:
        raise AssertionError("CKAD49_OLD_SOURCE_CHANGED")
    if model.observe(*last) is not model or model.checkpoint()!=raw:
        raise AssertionError("CKAD49_DUPLICATE_CHANGED")
    ident,row=last
    try:model.observe(ident,dict(row,y=1-row["y"]))
    except ValueError:pass
    else:raise AssertionError("CKAD49_CONFLICT_ACCEPTED")
    if model.checkpoint()!=raw:raise AssertionError("CKAD49_CONFLICT_MUTATED")
    return {"arm":model.arm,"checkpoint_sha256":sha(raw),"source_sha256":sha(canonical(model.ledger)),
      "old80_sha256":model.initial,"checkpoint_bytes":len(raw),"source_episodes":model.n,
      "four_public_actions_witnessed":len(actual_actions)==4,
      "cold_exact":True,"old_source_exact":True,"duplicate_idempotent":True,"conflict_atomic":True}

def expected_brier(p,q):
    if not(0<=p<=1 and 0<=q<=1):raise ValueError("CKAD49_BRIER_DOMAIN")
    return (p-q)**2+q*(1-q)

def run(seed):
    if seed not in DEV:raise ValueError("CKAD49_ONLY_REGISTERED_DEV")
    wall=time.perf_counter();cpu=time.process_time()
    probes=[];receipts=[]
    for world in (0,1):
        events,truth=source(seed,world)
        models={"discovered_feature_native":Structural("discovered_feature_native"),
                "exact_full_BMA":Structural("exact_full_BMA"),
                "unrestricted_tabular":Tabular(),
                "old_XOR_restricted":Structural("old_XOR_restricted")}
        seen=set();last_scored_structure=None
        for t,event in enumerate(events):
            ident,row=event
            if t in PROBES:
                if t==PROBES[-1]:last_scored_structure=models["discovered_feature_native"].selected()
                before={arm:m.checkpoint() for arm,m in models.items()}
                for arm in ARMS:
                    total=0
                    for s in range(4):
                        for a in range(4):
                            for b in range(4):
                                actual=private_query(truth,s,a,b)
                                predicted=.5 if arm=="uniform_negative" else models[arm].forecast(s,a,b)
                                total+=expected_brier(predicted,actual)
                    probes.append({"world":world,"t":t,"arm":arm,"brier":total/64})
                if any(model.checkpoint()!=before[arm] for arm,model in models.items()):
                    raise AssertionError("CKAD49_READ_CHANGED_SOURCE")
            seen.update((row["a1"],row["a2"]))
            for obj in models.values():obj.observe(ident,row)
        for arm,obj in models.items():
            receipt=custody(obj,events[-1],seen)
            receipt["world"]=world
            if isinstance(obj,Structural):
                selected,prob=obj.selected()
                receipt["selected_operator"]=selected[0]
                receipt["selected_partition_mask"]=selected[1]
                receipt["selected_posterior"]=prob
                receipt["true_operator_evaluator_only"]=truth["operator"]
                receipt["true_partition_evaluator_only"]=truth["mask"]
                if arm=="discovered_feature_native":
                    receipt["last_probe_selected_structure"]=last_scored_structure[0]
                    receipt["last_probe_posterior"]=last_scored_structure[1]
                    receipt["correct_feature_operator_by_last_probe"]=(
                        last_scored_structure[0]==(truth["operator"],truth["mask"]))
            receipts.append(receipt)
    groups={}
    for phase,indices in PHASES.items():
        subset=[x for x in probes if x["t"] in indices]
        if len(subset)!=len(indices)*2*len(ARMS):raise AssertionError("CKAD49_PROBE_COVERAGE")
        groups[phase]={"probe_world_model_records":len(subset),
           "expected_brier":{arm:sum(x["brier"] for x in subset if x["arm"]==arm)/(len(indices)*2)
                             for arm in ARMS}}
    return {"seed":seed,"groups":groups,"model_receipts":receipts,
      "genuine_source_episodes":TOTAL*2,"genuine_observed_consequences":TOTAL*6,
      "common_probe_records":len(probes),"inputs_per_probe":64,
      "cpu_seconds":round(time.process_time()-cpu,6),
      "wall_seconds":round(time.perf_counter()-wall,6)}

def classify(cases):
    if tuple(c["seed"] for c in cases)!=DEV:raise AssertionError("CKAD49_DEV_ORDER")
    for case in cases:
        receipts=case["model_receipts"]
        if len(receipts)!=8 or any(not all(w[k] for k in
                 ("four_public_actions_witnessed","cold_exact","old_source_exact",
                  "duplicate_idempotent","conflict_atomic")) for w in receipts):
            return "SOURCE_INVALID"
        if any(not w["correct_feature_operator_by_last_probe"] for w in receipts
               if w["arm"]=="discovered_feature_native"):
            return "DEV_NO_GO"
        g=case["groups"]
        late=g["pooled_late_and_cold"]["expected_brier"]
        early=g["early_novel"]["expected_brier"]
        cold=g["cold_return"]["expected_brier"]
        c=late["discovered_feature_native"]
        if (c>.19 or c>late["unrestricted_tabular"]-.010
            or c>late["old_XOR_restricted"]-.025
            or c>late["exact_full_BMA"]+.004
            or early["discovered_feature_native"]>early["exact_full_BMA"]+.015
            or cold["discovered_feature_native"]>cold["exact_full_BMA"]+.008):
            return "DEV_NO_GO"
    return "DEV_FEASIBLE_NOT_SCIENTIFIC"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("preflight","dev"),required=True)
    p.add_argument("--seed",type=int)
    args=p.parse_args()
    if args.mode=="preflight":
        if args.seed is not None:raise ValueError("CKAD49_PREFLIGHT_SEED_FORBIDDEN")
        print(canonical({"schema":SCHEMA,"prereg":PREREG,"dev":DEV,
           "pilots_untouched":PILOT,"primaries_untouched":PRIMARY,
           "accepted_Yggdrasil_model_modified":False,"first_use":False}))
        return
    if args.seed not in DEV:raise ValueError("CKAD49_ONLY_REGISTERED_DEV")
    print("CKAD49_CASE="+canonical(run(args.seed)))

if __name__=="__main__":main()

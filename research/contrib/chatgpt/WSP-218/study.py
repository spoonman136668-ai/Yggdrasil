"""WSP218 — fixed-cohort balanced unmarked causal-lag credit and context shift.

Independent SOURCE-FREE contributor; no native model/data or historical cohort.
Frozen prereg (before implementation): a37bced024ff959325f42d5259982dbd2197cb8f.
Hidden causal lag is accessed only by the simulator and postfit diagnostics.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import time

SCHEMA = "wsp218.balanced-contextual-credit.v1"
PREREG = "a37bced024ff959325f42d5259982dbd2197cb8f"
SEEDS = (21801, 21802, 21803, 21804)
TRUTH_BY_WORLD = {21801: 0, 21802: 0, 21803: 1, 21804: 1}
STAGES = 4
ROWS_PER_STAGE = 50
HELD_ROWS = 100
OUTPUTS = 3
FULL_FEATURES = 16
RIDGE = 0.01
SWEEPS = 60
MODES = ("local", "full_context", "first_only", "last_only", "lag_blind",
         "context_omitted", "shuffled")
SOURCE_SHA = hashlib.sha256((SCHEMA+"|"+PREREG).encode("ascii")).hexdigest()


def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),
                      allow_nan=False).encode("utf-8")


def shash(seed,*parts):
    if seed not in SEEDS:
        raise ValueError("source outside frozen WSP218 cohort")
    return hashlib.sha256("|".join(map(str,("WSP218",seed,*parts))).encode("utf-8")).digest()


def descriptor(seed,stage):
    """Exact 25x2 action grid; only public input metadata, no hidden law."""
    if seed not in SEEDS or stage not in range(STAGES):
        raise ValueError("invalid source/stage")
    out=[]
    for i in range(ROWS_PER_STAGE):
        a0=i%5
        a1=(i//5)%5
        context=shash(seed,"context",stage,i,a0,a1)[0]%8
        out.append((f"WSP218/{seed}/FIT/{stage*ROWS_PER_STAGE+i:04d}",
                    (a0,a1),context))
    return tuple(out)


def feature(actions,context,mode="full_context"):
    if (len(actions)!=2 or
            any(type(x) is not int or x not in range(5) for x in actions) or
            type(context) is not int or context not in range(16)):
        raise ValueError("ordered actions/context outside frozen domain")
    a0,a1=actions
    if mode in ("local","full_context","shuffled"):
        x=[0.0]*FULL_FEATURES
        if context<8:
            x[context]=1.0
        if a0:x[7+a0]=1.0
        if a1:x[11+a1]=1.0
    elif mode in ("first_only","last_only"):
        x=[0.0]*12
        if context<8:x[context]=1.0
        a=a0 if mode=="first_only" else a1
        if a:x[7+a]=1.0
    elif mode=="lag_blind":
        x=[0.0]*12
        if context<8:x[context]=1.0
        if a0:x[7+a0]+=1.0
        if a1:x[7+a1]+=1.0
    elif mode=="context_omitted":
        x=[1.0]+[0.0]*8
        if a0:x[a0]=1.0
        if a1:x[4+a1]=1.0
    else:
        raise ValueError("unknown action-credit feature mode")
    return tuple(x)


def width(mode):
    return (16 if mode in ("local","full_context","shuffled")
            else 9 if mode=="context_omitted" else 12)


def rank_unregularized(rows,mode="full_context"):
    """Exact metadata-only design rank; never opens FIT/held outcomes."""
    matrix=[list(map(float,feature(actions,ctx,mode)))
            for _,actions,ctx in rows]
    cols=width(mode)
    pivots=0
    for j in range(cols):
        p=max(range(pivots,len(matrix)),key=lambda i:abs(matrix[i][j]))
        if abs(matrix[p][j])<1e-9:
            continue
        matrix[pivots],matrix[p]=matrix[p],matrix[pivots]
        scale=matrix[pivots][j]
        for k in range(j,cols):matrix[pivots][k]/=scale
        for r in range(pivots+1,len(matrix)):
            factor=matrix[r][j]
            if factor:
                for k in range(j,cols):
                    matrix[r][k]-=factor*matrix[pivots][k]
        pivots+=1
    return pivots


def hidden_lag(seed):
    """Privileged SOURCE generator / evaluator ONLY. Never used by learner."""
    return TRUTH_BY_WORLD[seed]


def causal_effect(seed,lag,action,output):
    if (lag not in (0,1) or action not in range(5) or
            output not in range(OUTPUTS)):
        raise ValueError("invalid privileged world coordinate")
    if not action or lag!=hidden_lag(seed):return 0.0
    h=shash(seed,"hidden-effect",lag,action,output)
    return (1.0 if h[0]%2 else -1.0)*(2+h[1]%4)/4.0


def simulate(seed,phase,index,context,actions,branch):
    if phase not in ("FIT","HELD"):
        raise ValueError("world phase must be scoped")
    return tuple(
        (shash(seed,"context-nuisance",context,k)[0]%7-3)/5.0 +
        (shash(seed,"measurement-noise",phase,index,branch,k)[0]%5-2)/32.0 +
        sum(causal_effect(seed,lag,a,k) for lag,a in enumerate(actions))
        for k in range(OUTPUTS)
    )


@dataclass(frozen=True)
class Observation:
    event_id:str
    actions:tuple[int,int]
    context:int
    outcome:tuple[float,float,float]


@dataclass(frozen=True)
class HeldPair:
    pair_id:str
    context:int
    before:tuple[int,int]
    after:tuple[int,int]
    before_y:tuple[float,float,float]
    after_y:tuple[float,float,float]

    def delta(self):
        return tuple(a-b for a,b in zip(self.after_y,self.before_y))


def fit_batch(seed,stage):
    return tuple(Observation(event_id,actions,ctx,
                   simulate(seed,"FIT",stage*ROWS_PER_STAGE+i,ctx,actions,"single"))
                 for i,(event_id,actions,ctx) in enumerate(descriptor(seed,stage)))


def held_pairs(seed,*,finished=False):
    if seed not in SEEDS or not finished:
        raise ValueError("HELD outcomes forbidden until all FIT stages cold restored")
    out=[]
    for i in range(HELD_ROWS):
        context=8+shash(seed,"HELD-context-policy-shift",i)[0]%8
        before=(0,0)
        after=(i%5,(i//5)%5)
        out.append(HeldPair(
            f"WSP218/{seed}/HELD/{i:04d}",context,before,after,
            simulate(seed,"HELD",i,context,before,"reference"),
            simulate(seed,"HELD",i,context,after,"treatment")))
    return tuple(out)


def source_digest(rows):
    return hashlib.sha256(canon([
        (r.event_id,r.actions,r.context,r.outcome) for r in rows])).hexdigest()


def empty(n,m):
    return [[0.0]*m for _ in range(n)]


def gram_from_rows(rows,mode,shuffled=False):
    d=width(mode)
    gram=empty(d,d)
    target=empty(d,OUTPUTS)
    for i,r in enumerate(rows):
        x=feature(r.actions,r.context,mode)
        y=rows[(i+1)%len(rows)].outcome if shuffled else r.outcome
        active=[(j,a) for j,a in enumerate(x) if a]
        for j,a in active:
            for k,b in active:gram[j][k]+=a*b
            for o in range(OUTPUTS):target[j][o]+=a*y[o]
    return gram,target


def exact_ridge(gram,target):
    """True complete conventional ridge normal-equation optimum, not Adam."""
    d=len(gram)
    aug=[[float(gram[i][j])+(RIDGE if i==j else 0.0)
         for j in range(d)]+list(target[i]) for i in range(d)]
    for j in range(d):
        pivot=max(range(j,d),key=lambda k:abs(aug[k][j]))
        if abs(aug[pivot][j])<1e-12:
            raise ArithmeticError("qualified full-conventional solve singular")
        aug[pivot],aug[j]=aug[j],aug[pivot]
        scale=aug[j][j]
        for k in range(j,d+OUTPUTS):aug[j][k]/=scale
        for i in range(d):
            if i==j:continue
            fac=aug[i][j]
            if fac:
                for k in range(j,d+OUTPUTS):
                    aug[i][k]-=fac*aug[j][k]
    weights=[row[d:d+OUTPUTS] for row in aug]
    for j in range(d):
        for o in range(OUTPUTS):
            residual=sum((gram[j][i]+(RIDGE if i==j else 0.0))*weights[i][o]
                         for i in range(d))-target[j][o]
            if not math.isfinite(residual) or abs(residual)>1e-7:
                raise ArithmeticError("strong exact regression failed residual")
    return weights


def predict(weights,actions,context,mode):
    x=feature(actions,context,mode)
    return tuple(sum(weights[j][k]*x[j] for j in range(len(x)))
                 for k in range(OUTPUTS))


def package(state):
    data=dict(state)
    data["integrity_sha256"]=hashlib.sha256(canon(data)).hexdigest()
    return canon(data)


def unpack(blob,seed,mode):
    if not isinstance(blob,bytes):
        raise ValueError("durable checkpoint bytes required")
    state=json.loads(blob)
    checksum=state.pop("integrity_sha256","")
    if (state.get("schema")!=SCHEMA or state.get("source")!=SOURCE_SHA or
            state.get("seed")!=seed or state.get("mode")!=mode or
            checksum!=hashlib.sha256(canon(state)).hexdigest() or
            package(state)!=blob):
        raise ValueError("wrong checkpoint source, policy, world or integrity")
    return state


def check_batch(seed,last,stage,rows):
    if stage!=last+1 or stage not in range(STAGES) or len(rows)!=ROWS_PER_STAGE:
        raise ValueError("stage mismatch/replay/partial source")
    if len({r.event_id for r in rows})!=ROWS_PER_STAGE:
        raise ValueError("duplicate FIT source")
    for r,(eid,acts,ctx) in zip(rows,descriptor(seed,stage)):
        if ((r.event_id,r.actions,r.context)!=(eid,acts,ctx) or
                len(r.outcome)!=OUTPUTS or
                any(not math.isfinite(v) for v in r.outcome)):
            raise ValueError("wrong FIT source/metadata or nonfinite outcome")


class LocalCredit:
    """Cumulative source-exact local coactivations; no FIT row history."""

    def __init__(self,seed):
        if seed not in SEEDS:raise ValueError("unknown world")
        self.seed=seed
        self.stage=-1
        self.gram=empty(FULL_FEATURES,FULL_FEATURES)
        self.target=empty(FULL_FEATURES,OUTPUTS)
        self.weights=empty(FULL_FEATURES,OUTPUTS)
        self.source_chain=SOURCE_SHA
        self.rows_seen=0
        self.accumulations=0
        self.coordinate_solves=0

    def predict(self,actions,context):
        return predict(self.weights,actions,context,"local")

    def checkpoint(self):
        return package(dict(schema=SCHEMA,source=SOURCE_SHA,mode="local",
            seed=self.seed,stage=self.stage,gram=self.gram,target=self.target,
            weights=self.weights,source_chain=self.source_chain,
            rows_seen=self.rows_seen,accumulations=self.accumulations,
            coordinate_solves=self.coordinate_solves))

    @classmethod
    def restore(cls,blob,seed):
        s=unpack(blob,seed,"local")
        m=cls(seed)
        m.stage=s["stage"];m.gram=s["gram"];m.target=s["target"]
        m.weights=s["weights"];m.source_chain=s["source_chain"]
        m.rows_seen=s["rows_seen"];m.accumulations=s["accumulations"]
        m.coordinate_solves=s["coordinate_solves"]
        d=FULL_FEATURES
        if (m.stage not in range(-1,STAGES) or
                m.rows_seen!=(m.stage+1)*ROWS_PER_STAGE or
                len(m.gram)!=d or any(len(row)!=d for row in m.gram) or
                len(m.target)!=d or len(m.weights)!=d or
                any(len(row)!=OUTPUTS for row in m.target+m.weights) or
                any(not math.isfinite(v) for row in m.gram+m.target+m.weights for v in row) or
                m.coordinate_solves!=(m.stage+1)*SWEEPS*d*OUTPUTS or
                m.checkpoint()!=blob):
            raise ValueError("invalid/corrupt cumulative checkpoint")
        return m

    def advance(self,stage,rows):
        check_batch(self.seed,self.stage,stage,rows)
        candidate=type(self).restore(self.checkpoint(),self.seed)
        candidate.source_chain=hashlib.sha256(
            (candidate.source_chain+"|"+source_digest(rows)).encode("ascii")).hexdigest()
        for r in rows:
            x=feature(r.actions,r.context,"local")
            active=[(j,a) for j,a in enumerate(x) if a]
            for j,a in active:
                for k,b in active:
                    candidate.gram[j][k]+=a*b
                    candidate.accumulations+=1
                for o in range(OUTPUTS):
                    candidate.target[j][o]+=a*r.outcome[o]
                    candidate.accumulations+=1
        for sweep in range(SWEEPS):
            for j in range(FULL_FEATURES):
                denom=candidate.gram[j][j]+RIDGE
                if denom<=0:raise ArithmeticError("nonpositive local diagonal")
                for o in range(OUTPUTS):
                    residual=candidate.target[j][o]-sum(
                        candidate.gram[j][i]*candidate.weights[i][o]
                        for i in range(FULL_FEATURES) if i!=j)
                    candidate.weights[j][o]=residual/denom
                    candidate.coordinate_solves+=1
        candidate.stage=stage
        candidate.rows_seen+=len(rows)
        self.__dict__.update(candidate.__dict__)
        return dict(source_chain=self.source_chain,rows_seen=self.rows_seen,
                    scalar_accumulations=self.accumulations,
                    coordinate_solves=self.coordinate_solves,
                    stored_numerical_scalars=FULL_FEATURES**2+2*FULL_FEATURES*OUTPUTS,
                    checkpoint_sha256=hashlib.sha256(self.checkpoint()).hexdigest())


class BatchControl:
    """Exact fully trained all-cumulative-data alternative for each control."""

    def __init__(self,seed,mode):
        if seed not in SEEDS or mode not in MODES or mode=="local":
            raise ValueError("unknown model/source")
        self.seed=seed;self.mode=mode;self.stage=-1
        self.rows=[]
        self.weights=empty(width(mode),OUTPUTS)
        self.source_chain=SOURCE_SHA
        self.cumulative_refit_rows=0
        self.solved_dimensions=0

    def predict(self,actions,context):
        return predict(self.weights,actions,context,self.mode)

    def checkpoint(self):
        return package(dict(schema=SCHEMA,source=SOURCE_SHA,mode=self.mode,
                seed=self.seed,stage=self.stage,history=self.rows,
                weights=self.weights,source_chain=self.source_chain,
                cumulative_refit_rows=self.cumulative_refit_rows,
                solved_dimensions=self.solved_dimensions))

    @classmethod
    def restore(cls,blob,seed,mode):
        s=unpack(blob,seed,mode)
        m=cls(seed,mode)
        m.stage=s["stage"];m.rows=s["history"];m.weights=s["weights"]
        m.source_chain=s["source_chain"]
        m.cumulative_refit_rows=s["cumulative_refit_rows"]
        m.solved_dimensions=s["solved_dimensions"]
        if (m.stage not in range(-1,STAGES) or
                len(m.rows)!=(m.stage+1)*ROWS_PER_STAGE or
                len(m.weights)!=width(mode) or
                any(len(row)!=OUTPUTS for row in m.weights) or
                any(not math.isfinite(v) for row in m.weights for v in row) or
                m.cumulative_refit_rows!=ROWS_PER_STAGE*(m.stage+1)*(m.stage+2)//2 or
                m.checkpoint()!=blob):
            raise ValueError("invalid/corrupt batch full-refit snapshot")
        return m

    def advance(self,stage,rows):
        check_batch(self.seed,self.stage,stage,rows)
        candidate=type(self).restore(self.checkpoint(),self.seed,self.mode)
        candidate.source_chain=hashlib.sha256(
            (candidate.source_chain+"|"+source_digest(rows)).encode("ascii")).hexdigest()
        candidate.rows.extend([[r.event_id,r.actions,r.context,r.outcome] for r in rows])
        fitted=[Observation(eid,tuple(acts),ctx,tuple(y))
                for eid,acts,ctx,y in candidate.rows]
        if self.mode=="shuffled":
            displaced=[]
            for st in range(stage+1):
                part=fitted[st*ROWS_PER_STAGE:(st+1)*ROWS_PER_STAGE]
                displaced.extend([Observation(r.event_id,r.actions,r.context,
                                  part[(j+1)%len(part)].outcome)
                                  for j,r in enumerate(part)])
            g,b=gram_from_rows(displaced,self.mode)
        else:
            g,b=gram_from_rows(fitted,self.mode)
        candidate.weights=exact_ridge(g,b)
        candidate.cumulative_refit_rows+=len(fitted)
        candidate.solved_dimensions+=len(candidate.weights)
        candidate.stage=stage
        self.__dict__.update(candidate.__dict__)
        return dict(source_chain=self.source_chain,rows_seen=len(self.rows),
                    cumulative_refit_rows=self.cumulative_refit_rows,
                    solved_dimensions=self.solved_dimensions,
                    checkpoint_sha256=hashlib.sha256(self.checkpoint()).hexdigest())


def outcome_rmse(rows,model):
    return math.sqrt(sum((v-y)**2 for r in rows
        for v,y in zip(r.outcome,model.predict(r.actions,r.context)))
        /(len(rows)*OUTPUTS))


def contrast_rmse(held,model):
    return math.sqrt(sum((v-y)**2 for r in held
        for v,y in zip(r.delta(),
                (a-b for a,b in zip(model.predict(r.after,r.context),
                                    model.predict(r.before,r.context)))))
        /(len(held)*OUTPUTS))


def zero_rmse(held):
    return math.sqrt(sum(v*v for r in held for v in r.delta())
        /(len(held)*OUTPUTS))


def evaluate_world(seed):
    if seed not in SEEDS:raise ValueError("unfrozen synthetic world")
    models={"local":LocalCredit(seed)}
    models.update({m:BatchControl(seed,m) for m in MODES if m!="local"})
    traces={m:[] for m in MODES}
    b0=None
    for stage in range(STAGES):
        # Source-only matrix custody revalidated before each new FIT read.
        if rank_unregularized(descriptor(seed,stage))!=FULL_FEATURES:
            raise ValueError("preregistered full-rank source constraint failed")
        batch=fit_batch(seed,stage)
        if b0 is None:b0=batch
        for mode in MODES:
            m=models[mode]
            begin=time.perf_counter_ns()
            rec=m.advance(stage,batch)
            ck=m.checkpoint()
            cold=(LocalCredit.restore(ck,seed) if mode=="local"
                  else BatchControl.restore(ck,seed,mode))
            if (ck!=cold.checkpoint() or
                    any(cold.predict(x.actions,x.context)!=m.predict(x.actions,x.context)
                        for x in b0)):
                raise ValueError("historical B0 function changed on cold restore")
            traces[mode].append(dict(
                stage=stage,fit_source_sha256=m.source_chain,
                rows_seen=m.rows_seen if mode=="local" else len(m.rows),
                b0_historical_rmse=outcome_rmse(b0,m),
                scalar_accumulations=m.accumulations if mode=="local" else 0,
                coordinate_solves=m.coordinate_solves if mode=="local" else 0,
                cumulative_refit_rows=m.cumulative_refit_rows if mode!="local" else 0,
                checkpoint_sha256=hashlib.sha256(ck).hexdigest(),
                wall_ns=time.perf_counter_ns()-begin))
        if len({m.source_chain for m in models.values()})!=1:
            raise ValueError("same FIT exposure violated")
    held=held_pairs(seed,finished=all(m.stage==STAGES-1 for m in models.values()))
    scores={}
    for mode in MODES:
        m=models[mode]
        scores[mode]=dict(
            held_rmse=contrast_rmse(held,m),
            b0_final_rmse=traces[mode][-1]["b0_historical_rmse"],
            resident_numeric_scalars=(FULL_FEATURES**2+2*FULL_FEATURES*OUTPUTS
                                      if mode=="local" else width(mode)*OUTPUTS),
            coordinate_solves=m.coordinate_solves if mode=="local" else 0,
            cumulative_refit_rows=m.cumulative_refit_rows if mode!="local" else 0)
    zero=zero_rmse(held)
    # Postfit ONLY: the true lag selects the *wrong* restricted control for scoring.
    active=hidden_lag(seed)
    wrong="last_only" if active==0 else "first_only"
    right="first_only" if active==0 else "last_only"
    coeff=models["local"].weights
    energy=[sum(coeff[8+4*lag+a-1][k]**2
                for a in range(1,5) for k in range(OUTPUTS))
            for lag in (0,1)]
    lag_found=energy[active]>1.5*energy[1-active]
    loc=scores["local"];strong=scores["full_context"]
    primary=bool(
        loc["held_rmse"]<=max(1.10*strong["held_rmse"],strong["held_rmse"]+0.02)
        and loc["held_rmse"]<=.75*scores[wrong]["held_rmse"]
        and loc["held_rmse"]<=.75*scores["lag_blind"]["held_rmse"]
        and loc["held_rmse"]<=.75*scores["shuffled"]["held_rmse"]
        and loc["held_rmse"]<=.60*zero
        and lag_found
        and loc["b0_final_rmse"]<=max(
            1.2*traces["local"][0]["b0_historical_rmse"],
            traces["local"][0]["b0_historical_rmse"]+.02))
    # These privileged quantities are computed ONLY after all fitted arms scored.
    oracle=math.sqrt(sum((v-y)**2 for r in held
         for v,y in zip(r.delta(),(
             sum(causal_effect(seed,j,r.after[j],k)-
                 causal_effect(seed,j,r.before[j],k) for j in (0,1))
             for k in range(OUTPUTS))))
         /(len(held)*OUTPUTS))
    return dict(world=seed,status="VALID",stage_count=4,fit_rows=200,
        held_pairs=len(held),fit_source_sha256=models["local"].source_chain,
        held_sha256=hashlib.sha256(canon([(r.pair_id,r.context,r.before,
              r.after,r.before_y,r.after_y) for r in held])).hexdigest(),
        traces=traces,scores=scores,zero_held_rmse=zero,oracle_held_rmse=oracle,
        active_lag_postfit=active,wrong_control_postfit=wrong,
        right_control_postfit=right,lag_energy=energy,lag_identified=lag_found,
        world_supported=primary,original_gfp_accessed=False,reserved_accessed=False)


def run_primary():
    worlds=[evaluate_world(seed) for seed in SEEDS]
    result=("INVALID" if any(w["status"]!="VALID" for w in worlds)
            else "BALANCED_CREDIT_SUPPORTED" if
                 sum(w["world_supported"] for w in worlds)>=3
            else "NO_GAIN")
    return dict(schema=SCHEMA,prereg=PREREG,classification=result,worlds=worlds,
        original_gfp_accessed=False,reserved_accessed=False,
        prior_cohorts_reused=False,native_amalgam_accessed=False,
        research_only=True)


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    cfg=ap.parse_args()
    receipt=run_primary()
    Path(cfg.output).write_text(
        json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+"\n",
        encoding="utf-8")
    print("WSP218_CLASSIFICATION="+receipt["classification"])
    for w in receipt["worlds"]:
        print(f"WSP218_WORLD={w['world']} STATUS={w['status']}"
              f" GAIN={w['world_supported']} LAG_IDENTIFIED={w['lag_identified']}"
              f" LOCAL_RMSE={w['scores']['local']['held_rmse']}"
              f" CONVENTIONAL_RMSE={w['scores']['full_context']['held_rmse']}"
              f" WRONG_LAG_RMSE={w['scores'][w['wrong_control_postfit']]['held_rmse']}")

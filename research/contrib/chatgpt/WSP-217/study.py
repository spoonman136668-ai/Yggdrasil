"""WSP-217 — unknown-lag credit from unmarked action/outcome sequences.

Synthetic independent research ONLY; no marker or paired intervention in FIT.
Prerecorded source prereg commit: 273f0c4671bb4a27dcbe29f24bb0ab16339361cc.
All four first-use worlds are inaccessible before source-only/G29 qualification.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import time

SCHEMA = "wsp217.unmarked-delayed-credit.v1"
PREREG = "273f0c4671bb4a27dcbe29f24bb0ab16339361cc"
SEEDS = (21701, 21702, 21703, 21704)
STAGES = 4
ROWS_PER_STAGE = 50
HELD_ROWS = 100
OUTPUTS = 3
FEATURES = 9
RIDGE = 0.001
SWEEPS = 24
MODES = ("local", "full_regression", "last_action",
         "pooled_action", "shuffled_consequence")
SOURCE_SHA = hashlib.sha256((SCHEMA+"|"+PREREG).encode("ascii")).hexdigest()


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _hash(seed, *parts):
    if seed not in SEEDS:
        raise ValueError("outside WSP217 frozen worlds")
    return hashlib.sha256("\0".join(map(str, ("WSP217", seed, *parts))).encode("utf-8")).digest()


def feature(actions, mode="full_regression"):
    if len(actions) != 2 or any(type(a) is not int or a not in range(5) for a in actions):
        raise ValueError("invalid ordered trace actions")
    t0,t1 = actions
    if mode in ("full_regression","local","shuffled_consequence"):
        x=[1.0]+[0.0]*8
        if t0: x[t0]=1.0
        if t1: x[4+t1]=1.0
        return tuple(x)
    if mode=="last_action":
        x=[1.0]+[0.0]*4
        if t1: x[t1]=1.0
        return tuple(x)
    if mode=="pooled_action":
        x=[1.0]+[0.0]*4
        if t0: x[t0]+=1.0
        if t1: x[t1]+=1.0
        return tuple(x)
    raise ValueError("unknown feature policy")


def fit_descriptor(seed, stage):
    """Source-only full-rank metadata, NEVER loads an outcome or causal law."""
    if seed not in SEEDS or stage not in range(STAGES):
        raise ValueError("frozen source or stage required")
    return tuple((
        f"WSP217/{seed}/FIT/{stage*ROWS_PER_STAGE+i:04d}",
        ((i % 25) % 5, (i % 25)//5),
        (3*i+5*stage+seed%8)%8
    ) for i in range(ROWS_PER_STAGE))


def _active_lag(seed):
    return _hash(seed,"hidden-active-lag")[0]%2


def _law(seed, lag, action, output):
    """Privileged world generator, never imported by learner update/readout."""
    if lag not in (0,1) or action not in range(5) or output not in range(OUTPUTS):
        raise ValueError("world law index invalid")
    if not action or lag != _active_lag(seed):
        return 0.0
    v=_hash(seed,"hidden-effect",lag,action,output)
    return (1.0 if v[0]%2 else -1.0)*(2+v[1]%4)/4.0


def _outcome(seed, phase, index, context, actions, branch):
    base=[(_hash(seed,"nuisance",context,k)[0]%7-3)/5.0
          for k in range(OUTPUTS)]
    noise=[(_hash(seed,"noise",phase,index,branch,k)[0]%5-2)/32.0
           for k in range(OUTPUTS)]
    return tuple(base[k]+noise[k]+sum(_law(seed,lag,action,k)
                    for lag,action in enumerate(actions)) for k in range(OUTPUTS))


@dataclass(frozen=True)
class Observation:
    event_id: str
    context: int
    actions: tuple[int,int]
    outcome: tuple[float,float,float]


@dataclass(frozen=True)
class HeldPair:
    pair_id: str
    context: int
    before: tuple[int,int]
    after: tuple[int,int]
    before_outcome: tuple[float,float,float]
    after_outcome: tuple[float,float,float]

    def actual_contrast(self):
        return tuple(a-b for a,b in zip(self.after_outcome,self.before_outcome))


def fit_batch(seed,stage):
    return tuple(Observation(event_id,context,actions,
                  _outcome(seed,"FIT",stage*ROWS_PER_STAGE+i,context,actions,"observed"))
                 for i,(event_id,actions,context) in enumerate(fit_descriptor(seed,stage)))


def held_pairs(seed, *, stages_completed=False):
    if seed not in SEEDS or not stages_completed:
        raise ValueError("sealed held first-use only after B3")
    pairs=[]
    for i in range(HELD_ROWS):
        context=8+(i*3+seed)%8
        before=(0,0)
        after=(i%5,(i//5)%5)
        before_y=_outcome(seed,"HELD",i,context,before,"reference")
        after_y=_outcome(seed,"HELD",i,context,after,"treatment")
        pairs.append(HeldPair(f"WSP217/{seed}/HELD/{i:04d}",context,before,
                              after,before_y,after_y))
    return tuple(pairs)


def _source_digest(rows):
    return hashlib.sha256(_canon([(r.event_id,r.context,r.actions,r.outcome)
                                  for r in rows])).hexdigest()


def _model_source_digest(previous,batch_digest):
    return hashlib.sha256((previous+"|"+batch_digest).encode("ascii")).hexdigest()


def _zeros(n,m):
    return [[0.0]*m for _ in range(n)]


def _gram(rows,mode,shuffle=False):
    d=FEATURES if mode in ("full_regression","local","shuffled_consequence") else 5
    gram=_zeros(d,d)
    target=_zeros(d,OUTPUTS)
    for n,row in enumerate(rows):
        x=feature(row.actions,mode)
        y=rows[(n+1)%len(rows)].outcome if shuffle else row.outcome
        for a,u in enumerate(x):
            if u==0.0: continue
            for b,v in enumerate(x):
                if v: gram[a][b]+=u*v
            for o in range(OUTPUTS):
                target[a][o]+=u*y[o]
    return gram,target


def _solve_exact(gram,target):
    """Fully converged ridge-OLS normal-equation solve, not gradient budget."""
    n=len(gram)
    a=[[float(gram[i][j])+(RIDGE if i==j else 0.0)
        for j in range(n)]+list(target[i]) for i in range(n)]
    for col in range(n):
        pivot=max(range(col,n),key=lambda r:abs(a[r][col]))
        if abs(a[pivot][col])<1e-12:
            raise ArithmeticError("full-rank exact control nonconvergence")
        a[col],a[pivot]=a[pivot],a[col]
        scale=a[col][col]
        for j in range(col,n+OUTPUTS):
            a[col][j]/=scale
        for i in range(n):
            if i==col: continue
            k=a[i][col]
            if not k: continue
            for j in range(col,n+OUTPUTS):
                a[i][j]-=k*a[col][j]
    weights=[row[n:n+OUTPUTS] for row in a]
    for i in range(n):
        for o in range(OUTPUTS):
            residual=sum((gram[i][j]+(RIDGE if i==j else 0.0))*weights[j][o]
                         for j in range(n))-target[i][o]
            if not math.isfinite(residual) or abs(residual)>1e-7:
                raise ArithmeticError("strong conventional normal equations not qualified")
    return weights


def _predict(weights,actions,mode):
    x=feature(actions,mode)
    return tuple(sum(weights[j][k]*x[j] for j in range(len(x)))
                 for k in range(OUTPUTS))


def _ckpt(data):
    snapshot=dict(data)
    snapshot["checksum"]=hashlib.sha256(_canon(snapshot)).hexdigest()
    return _canon(snapshot)


def _decode(blob,seed,mode):
    if not isinstance(blob,bytes):
        raise ValueError("snapshot bytes required")
    s=json.loads(blob)
    checksum=s.pop("checksum","")
    if (s.get("schema")!=SCHEMA or s.get("source")!=SOURCE_SHA or
            s.get("seed")!=seed or s.get("mode")!=mode or
            checksum!=hashlib.sha256(_canon(s)).hexdigest() or
            _ckpt(s)!=blob):
        raise ValueError("checkpoint provenance/checksum mismatch")
    return s


class LocalCredit:
    """Persistent native-style *local covariance* learner, raw rows discarded."""

    def __init__(self,seed):
        if seed not in SEEDS:
            raise ValueError("unfrozen seed")
        self.seed=seed
        self.stage=-1
        self.g=_zeros(FEATURES,FEATURES)
        self.b=_zeros(FEATURES,OUTPUTS)
        self.w=_zeros(FEATURES,OUTPUTS)
        self.source=SOURCE_SHA
        self.count=0
        self.accumulations=0
        self.coordinate_solves=0

    def predict(self,actions):
        return _predict(self.w,actions,"local")

    def checkpoint(self):
        return _ckpt(dict(schema=SCHEMA,source=SOURCE_SHA,seed=self.seed,
              mode="local",stage=self.stage,gram=self.g,target=self.b,
              weights=self.w,source_chain=self.source,count=self.count,
              accumulations=self.accumulations,coordinate_solves=self.coordinate_solves))

    @classmethod
    def restore(cls,blob,seed):
        s=_decode(blob,seed,"local")
        m=cls(seed)
        m.stage=s["stage"]
        m.g=s["gram"];m.b=s["target"];m.w=s["weights"]
        m.source=s["source_chain"];m.count=s["count"]
        m.accumulations=s["accumulations"]
        m.coordinate_solves=s["coordinate_solves"]
        if (m.stage not in range(-1,STAGES) or
                m.count != (m.stage+1)*ROWS_PER_STAGE or
                len(m.g)!=FEATURES or any(len(x)!=FEATURES for x in m.g) or
                len(m.b)!=FEATURES or len(m.w)!=FEATURES or
                any(len(x)!=OUTPUTS for x in m.b+m.w) or
                any(not math.isfinite(v) for row in m.g+m.b+m.w for v in row) or
                m.checkpoint()!=blob):
            raise ValueError("invalid cold local covariance state")
        return m

    def advance(self,stage,rows):
        _check_stage(self.seed,self.stage,stage,rows)
        candidate=type(self).restore(self.checkpoint(),self.seed)
        digest=_source_digest(rows)
        candidate.source=_model_source_digest(candidate.source,digest)
        for r in rows:
            x=feature(r.actions,"local")
            active=[i for i,v in enumerate(x) if v]
            for a in active:
                for b in active:
                    candidate.g[a][b]+=x[a]*x[b]
                    candidate.accumulations+=1
                for k in range(OUTPUTS):
                    candidate.b[a][k]+=x[a]*r.outcome[k]
                    candidate.accumulations+=1
        for sweep in range(SWEEPS):
            for j in range(FEATURES):
                scale=candidate.g[j][j]+RIDGE
                if scale<=0: raise ArithmeticError("bad local diagonal")
                for k in range(OUTPUTS):
                    numerator=candidate.b[j][k]-sum(candidate.g[j][i]*candidate.w[i][k]
                                                    for i in range(FEATURES) if i!=j)
                    candidate.w[j][k]=numerator/scale
                    candidate.coordinate_solves+=1
        candidate.stage=stage
        candidate.count+=len(rows)
        self.__dict__.update(candidate.__dict__)
        return dict(source_digest=self.source, stage=stage, rows=self.count,
                    accumulations=self.accumulations, coordinate_solves=self.coordinate_solves,
                    resident_scalars=FEATURES*FEATURES+2*FEATURES*OUTPUTS,
                    checkpoint_sha256=hashlib.sha256(self.checkpoint()).hexdigest())


class BatchRidge:
    def __init__(self,seed,mode):
        if seed not in SEEDS or mode not in MODES or mode=="local":
            raise ValueError("bad strong/negative baseline")
        self.seed=seed;self.mode=mode;self.stage=-1
        self.rows=[];self.source=SOURCE_SHA
        d=FEATURES if mode in ("full_regression","shuffled_consequence") else 5
        self.w=_zeros(d,OUTPUTS)
        self.total_rows_fit=0
        self.equation_solves=0

    def predict(self,actions):
        return _predict(self.w,actions,self.mode)

    def checkpoint(self):
        return _ckpt(dict(schema=SCHEMA,source=SOURCE_SHA,seed=self.seed,
                    mode=self.mode,stage=self.stage,
                    history=self.rows,weights=self.w,source_chain=self.source,
                    total_rows_fit=self.total_rows_fit,equation_solves=self.equation_solves))

    @classmethod
    def restore(cls,blob,seed,mode):
        s=_decode(blob,seed,mode)
        m=cls(seed,mode)
        m.stage=s["stage"];m.rows=s["history"];m.w=s["weights"]
        m.source=s["source_chain"];m.total_rows_fit=s["total_rows_fit"]
        m.equation_solves=s["equation_solves"]
        if (m.stage not in range(-1,STAGES) or
                len(m.rows)!=(m.stage+1)*ROWS_PER_STAGE or
                len(m.w)!=(FEATURES if mode in ("full_regression","shuffled_consequence") else 5) or
                any(len(x)!=OUTPUTS or not all(map(math.isfinite,x)) for x in m.w) or
                m.checkpoint()!=blob):
            raise ValueError("invalid conventional model checkpoint")
        return m

    def advance(self,stage,rows):
        _check_stage(self.seed,self.stage,stage,rows)
        candidate=type(self).restore(self.checkpoint(),self.seed,self.mode)
        digest=_source_digest(rows)
        candidate.source=_model_source_digest(candidate.source,digest)
        candidate.rows.extend([[r.event_id,r.actions,r.outcome] for r in rows])
        # Refit all observed raw events from scratch, not a partial batch baseline.
        dset=[Observation(i,0,tuple(a),tuple(y)) for i,a,y in candidate.rows]
        if self.mode=="shuffled_consequence":
            # Frozen cyclic permutation WITHIN each earlier stage independently.
            shuffled=[]
            for start in range(0,len(dset),ROWS_PER_STAGE):
                part=dset[start:start+ROWS_PER_STAGE]
                shuffled.extend([Observation(e.event_id,e.context,e.actions,
                                              part[(j+1)%ROWS_PER_STAGE].outcome)
                                 for j,e in enumerate(part)])
            gram,target=_gram(shuffled,self.mode)
        else:
            gram,target=_gram(dset,self.mode)
        candidate.w=_solve_exact(gram,target)
        candidate.stage=stage
        candidate.total_rows_fit+=len(dset)
        candidate.equation_solves+=(len(candidate.w))**3
        self.__dict__.update(candidate.__dict__)
        return dict(source_digest=self.source,stage=stage,rows=len(self.rows),
                    cumulative_batch_rows_replayed=self.total_rows_fit,
                    equation_solver_cubic_units=self.equation_solves,
                    checkpoint_sha256=hashlib.sha256(self.checkpoint()).hexdigest())


def _check_stage(seed,last,stage,rows):
    if stage!=last+1 or stage not in range(STAGES) or len(rows)!=ROWS_PER_STAGE:
        raise ValueError("out-of-order stage/replay/partial batch")
    desc=fit_descriptor(seed,stage)
    if len({r.event_id for r in rows})!=ROWS_PER_STAGE:
        raise ValueError("duplicate or invalid evidence IDs")
    for row,(event_id,actions,context) in zip(rows,desc):
        if (row.event_id,row.actions,row.context)!=(event_id,actions,context) or
                len(row.outcome)!=OUTPUTS or not all(map(math.isfinite,row.outcome))):
            raise ValueError("bad FIT evidence or wrong stage")


def _score_outcomes(rows,model):
    return math.sqrt(sum((y-z)**2 for r in rows
           for y,z in zip(r.outcome,model.predict(r.actions)))/(len(rows)*OUTPUTS))


def _held_rmse(rows,model):
    return math.sqrt(sum((v-u)**2 for r in rows
          for v,u in zip(r.actual_contrast(),
                         (a-b for a,b in zip(model.predict(r.after),
                                              model.predict(r.before)))))
            /(len(rows)*OUTPUTS))


def _zero_held_rmse(rows):
    return math.sqrt(sum(v*v for r in rows for v in r.actual_contrast())
                     /(len(rows)*OUTPUTS))


def evaluate_world(seed):
    if seed not in SEEDS:
        raise ValueError("unfrozen primary")
    trained={"local":LocalCredit(seed)}
    trained.update({mode:BatchRidge(seed,mode) for mode in MODES if mode!="local"})
    trajectories={mode:[] for mode in MODES}
    b0=None
    for stage in range(STAGES):
        rows=fit_batch(seed,stage)
        if b0 is None: b0=rows
        batch_digest=_source_digest(rows)
        for mode in MODES:
            model=trained[mode]
            start=time.perf_counter_ns()
            receipt=model.advance(stage,rows)
            if receipt["source_digest"]!=model.source:
                raise ValueError("mismatched evidence")
            ckpt=model.checkpoint()
            cold=(LocalCredit.restore(ckpt,seed) if mode=="local"
                  else BatchRidge.restore(ckpt,seed,mode))
            if (cold.checkpoint()!=ckpt or
                    any(cold.predict(r.actions)!=model.predict(r.actions) for r in b0)):
                raise ValueError("cold functional historical memory drift")
            b0_rmse=_score_outcomes(b0,model)
            trajectories[mode].append(dict(stage=stage,source_digest=model.source,
                            b0_rmse=b0_rmse,checkpoint_sha256=receipt["checkpoint_sha256"],
                            rows_cumulative=model.count if mode=="local" else len(model.rows),
                            scalar_accumulations=model.accumulations if mode=="local" else 0,
                            coordinate_solves=model.coordinate_solves if mode=="local" else 0,
                            conventional_refit_rows=model.total_rows_fit if mode!="local" else 0,
                            wall_ns=time.perf_counter_ns()-start))
        if len({trained[mode].source for mode in MODES})!=1:
            raise ValueError("different source evidence for arms")
    held=held_pairs(seed,stages_completed=all(m.stage==3 for m in trained.values()))
    if any(r.pair_id.startswith(f"WSP217/{seed}/FIT/") for r in held):
        raise ValueError("held/FIT overlap")
    metrics={mode:dict(held_effect_rmse=_held_rmse(held,trained[mode]),
                       b0_final_rmse=trajectories[mode][-1]["b0_rmse"],
                       stored_scalar_weights=(FEATURES*FEATURES+2*FEATURES*OUTPUTS
                                              if mode=="local" else len(trained[mode].w)*OUTPUTS),
                       total_coordinate_solves=(trained[mode].coordinate_solves if mode=="local" else 0),
                       cumulative_batch_rows_replayed=(trained[mode].total_rows_fit
                                                       if mode!="local" else 0))
             for mode in MODES}
    zero=_zero_held_rmse(held)
    # Never expose world lag to a fitted arm. This is a held-only causal diagnostic.
    real=_active_lag(seed)
    weights=trained["local"].w
    magnitudes=[sum(weights[1+4*lag+a-1][k]**2
                   for a in range(1,5) for k in range(OUTPUTS))
                for lag in range(2)]
    discovered=(magnitudes[real]>1.5*magnitudes[1-real])
    local=metrics["local"];full=metrics["full_regression"]
    supported=bool(
        local["held_effect_rmse"]<=max(1.10*full["held_effect_rmse"],
                                        full["held_effect_rmse"]+0.02) and
        local["held_effect_rmse"]<=.75*metrics["last_action"]["held_effect_rmse"] and
        local["held_effect_rmse"]<=.75*metrics["pooled_action"]["held_effect_rmse"] and
        local["held_effect_rmse"]<=.75*metrics["shuffled_consequence"]["held_effect_rmse"] and
        local["held_effect_rmse"]<=.60*zero and
        discovered and
        local["b0_final_rmse"]<=max(
            1.20*trajectories["local"][0]["b0_rmse"],
            trajectories["local"][0]["b0_rmse"]+0.02))
    # Privileged oracle can be used only AFTER every model is trained/scored.
    oracle=math.sqrt(sum((v-u)**2 for r in held
          for v,u in zip(r.actual_contrast(),
              (sum(_law(seed,j,r.after[j],k)-_law(seed,j,r.before[j],k)
                   for j in range(2)) for k in range(OUTPUTS))))
                    /(len(held)*OUTPUTS))
    return dict(world=seed,status="VALID",stages_completed=STAGES,
                fit_rows=STAGES*ROWS_PER_STAGE,held_pairs=len(held),
                fit_sha256=trained["local"].source,
                held_sha256=hashlib.sha256(_canon([(r.pair_id,r.context,r.before,r.after,
                              r.before_outcome,r.after_outcome) for r in held])).hexdigest(),
                trajectories=trajectories,metrics=metrics,
                zero_held_rmse=zero,oracle_held_rmse=oracle,
                hidden_lag_postfit=real,discovered_active_lag=discovered,
                active_lag_l2_squares=magnitudes,
                world_supported=supported,original_gfp_accessed=False,
                reserved_accessed=False)


def run_primary():
    worlds=[evaluate_world(seed) for seed in SEEDS]
    status=("INVALID" if any(w["status"]!="VALID" for w in worlds) else
            "UNMARKED_CREDIT_SUPPORTED" if sum(w["world_supported"] for w in worlds)>=3
            else "NO_GAIN")
    return dict(schema=SCHEMA,prereg=PREREG,status=status,worlds=worlds,
                original_gfp_accessed=False,reserved_accessed=False,
                prior_cohorts_reused=False,native_amalgam_accessed=False,
                research_only=True)


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    cfg=ap.parse_args()
    r=run_primary()
    Path(cfg.output).write_text(json.dumps(r,sort_keys=True,indent=2,
                                           allow_nan=False)+"\n",encoding="utf-8")
    print("WSP217_CLASSIFICATION="+r["status"])
    for w in r["worlds"]:
        print(f"WSP217_WORLD={w['world']} STATUS={w['status']}"
              f" SUPPORTED={w['world_supported']} LAG_IDENTIFIED={w['discovered_active_lag']}"
              f" LOCAL_RMSE={w['metrics']['local']['held_effect_rmse']}"
              f" CONVENTIONAL_RMSE={w['metrics']['full_regression']['held_effect_rmse']}")

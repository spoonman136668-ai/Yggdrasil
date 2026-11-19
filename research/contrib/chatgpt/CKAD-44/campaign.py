"""CKAD44: genuine-action causal evidence against a fitted changepoint control.

Research sidecar only. Neither native learner nor accepted Yggdrasil code is
changed. Source score precedes revelation of actual witnessed consequences.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
import sys
import time
from collections import deque
from decimal import Decimal
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE=Path(__file__).resolve().parent
EXACT=HERE.parent/"CKAD-42"/"campaign.py"
spec=importlib.util.spec_from_file_location("ckad42_exact_for_44",EXACT)
E=importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)
C=E.C

SCHEMA="yggdrasil.ckad44.source-change-evidence-dev.v1"
PREREG="0c613f55a2e5d68d5bbc9ce21a5b8fbc8a84e0a7"
DEV=(44111,44112)
PILOT=(44211,44212)
PRIMARY=(44311,44312,44313)
EXCLUDED=(43111,43112,42111,42112,41101,41102,40811,40812,38911,38912)
REFERENCE_EVENTS=64
EVIDENCE_WINDOW=12
CLIP=8.0
RUN_CAP=48
HAZARD=1.0/72.0
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")
LATE=("late_B","late_return_A")
CONVENTIONAL=(*C.CONVENTIONAL,"beta_hedge")
ARMS=("contrastive_recall","uniform_recall","frozen_reference",
      "causal_discount93","causal_full","causal_dual","causal_action_masked",
      "native_stream","beta_bocpd",*CONVENTIONAL,"sham")


def pair_loss(p,q,row):
    if not all(0.0<=v<=1.0 for v in (p,q)):
        raise AssertionError("CKAD44_OUT_OF_RANGE")
    e1=p-row["s2"]
    e2=q-row["y"]
    return (e1*e1+e2*e2)*.5


def _event_probability(p,q,row):
    # Two actually witnessed outcomes; read before source update.
    t=p if row["s2"] else 1.0-p
    y=q if row["y"] else 1.0-q
    return t*y


def _observed_log_ratio(a,b):
    if not (0.0<a<=1.0 and 0.0<b<=1.0):
        raise AssertionError("CKAD44_ZERO_EVENT_LIKELIHOOD")
    ctx=E._PORTABLE_DECIMAL_CONTEXT
    return float(ctx.subtract(ctx.ln(Decimal.from_float(a)),
                              ctx.ln(Decimal.from_float(b))))


class ContrastiveCausalMemory:
    """One frozen source-trained reference plus a continual causal expert."""
    def __init__(self):
        self.adaptive=E.NativeInterventionRelations()
        self.reference=None
        self.receipts={}
        self.history=deque(maxlen=EVIDENCE_WINDOW)
        self.n=0
        self.eligible_reads=0
        self.no_diversity_reads=0

    def _weight(self):
        if self.reference is None or len(self.history)<EVIDENCE_WINDOW:
            return 0.0
        if (len({a["x1"] for a in self.history})<2 or
                len({a["x2"] for a in self.history})<2):
            return 0.0
        evidence=sum(a["lr"] for a in self.history)
        evidence=max(-CLIP,min(CLIP,evidence))
        return 1.0/(1.0+E._portable_exp(-evidence))

    def read(self,mode,view,first,next_state=None,second=None):
        if mode not in ("contrastive_recall","uniform_recall","frozen_reference",
                        "causal_discount93","causal_full","causal_dual",
                        "causal_action_masked"):
            raise ValueError("CKAD44_UNREGISTERED_READOUT")
        if mode=="causal_action_masked":
            return self.adaptive.read("no_action",view,first,next_state,second)
        if mode in ("causal_discount93","causal_full","causal_dual"):
            m={"causal_discount93":"short","causal_full":"full",
               "causal_dual":"dual"}[mode]
            return self.adaptive.read(m,view,first,next_state,second)
        if self.reference is None:
            return self.adaptive.read("short",view,first,next_state,second)
        if mode=="frozen_reference":
            return self.reference.read("short",view,first,next_state,second)
        weight=(self._weight() if mode=="contrastive_recall" else .5)
        if weight==0:
            return self.adaptive.read("short",view,first,next_state,second)
        pa=self.reference.read("short",view,first)
        pb=self.adaptive.read("short",view,first)
        if next_state is None:
            return weight*pa+(1-weight)*pb
        if second is None or type(next_state) is not int or next_state not in (0,1):
            raise ValueError("CKAD44_STAGE_INPUT")
        # The transition has been observed. Condition expert mass on that
        # actual transition BEFORE reporting the terminal prediction.
        like_a=pa if next_state else 1-pa
        like_b=pb if next_state else 1-pb
        norm=weight*like_a+(1-weight)*like_b
        if norm<=0:
            raise AssertionError("CKAD44_INVALID_CONDITIONAL_MASS")
        conditioned=weight*like_a/norm
        qa=self.reference.read("short",view,first,next_state,second)
        qb=self.adaptive.read("short",view,first,next_state,second)
        return conditioned*qa+(1-conditioned)*qb

    def observe(self,identifier,views,row):
        if type(identifier) is not str or type(views) is not tuple or type(row) is not dict:
            raise ValueError("CKAD44_INVALID_PUBLIC_SOURCE")
        receipt=canonical([views,row]).decode("ascii")
        if identifier in self.receipts:
            if self.receipts[identifier]!=receipt:
                raise ValueError("CKAD44_CONFLICTING_SOURCE_ID")
            return self
        if self.n>=E.MAX_EVENTS:
            raise ValueError("CKAD44_SOURCE_CAP")
        if self.reference is not None:
            view=views[0]
            pa=self.reference.read("short",view,row["x1"])
            qa=self.reference.read("short",view,row["x1"],row["s2"],row["x2"])
            pb=self.adaptive.read("short",view,row["x1"])
            qb=self.adaptive.read("short",view,row["x1"],row["s2"],row["x2"])
            lr=_observed_log_ratio(_event_probability(pa,qa,row),
                                   _event_probability(pb,qb,row))
            self.history.append({"lr":lr,"x1":row["x1"],"x2":row["x2"]})
        self.adaptive.observe(identifier,views,row)
        self.receipts[identifier]=receipt
        self.n+=1
        if self.n==REFERENCE_EVENTS:
            raw=self.adaptive.checkpoint()
            self.reference=E.NativeInterventionRelations.restore(raw,digest(raw))
            self.history.clear()
        if self.adaptive.n!=self.n:
            raise AssertionError("CKAD44_SOURCE_UPDATE_PARITY")
        if self.reference is not None and self.reference.n!=REFERENCE_EVENTS:
            raise AssertionError("CKAD44_ARCHIVE_TRAINED_AFTER_FREEZE")
        return self

    def checkpoint(self):
        return canonical({"schema":SCHEMA,"adaptive":json.loads(self.adaptive.checkpoint()),
             "reference":None if self.reference is None else json.loads(self.reference.checkpoint()),
             "n":self.n,"receipts":self.receipts,"history":list(self.history)})

    @classmethod
    def restore(cls,raw,expected):
        if digest(raw)!=expected:raise ValueError("CKAD44_CHECKPOINT_SHA")
        j=json.loads(raw)
        if j["schema"]!=SCHEMA or j["n"]!=len(j["receipts"]):
            raise ValueError("CKAD44_CHECKPOINT_SCHEMA_OR_COUNT")
        obj=cls()
        a=canonical(j["adaptive"])
        obj.adaptive=E.NativeInterventionRelations.restore(a,digest(a))
        if j["reference"] is not None:
            b=canonical(j["reference"])
            obj.reference=E.NativeInterventionRelations.restore(b,digest(b))
        obj.n=j["n"]
        obj.receipts=dict(j["receipts"])
        obj.history=deque(j["history"],maxlen=EVIDENCE_WINDOW)
        if (obj.adaptive.n!=obj.n or
            (obj.reference is not None and
             (obj.reference.n!=REFERENCE_EVENTS or obj.n<REFERENCE_EVENTS)) or
            (obj.reference is None and obj.n>=REFERENCE_EVENTS)):
            raise ValueError("CKAD44_RESTORED_SOURCE_COUNT")
        if obj.checkpoint()!=raw:raise ValueError("CKAD44_CHECKPOINT_NONCANONICAL")
        return obj


def _cell_key(row,terminal=False):
    if not terminal:return str(row["s1"])+":"+str(row["x1"])
    return ":".join(str(row[k]) for k in ("s1","x1","s2","x2"))


def _beta(counts,key):
    z,o=counts.get(key,(0,0))
    return (1.0+o)/(2.0+z+o)


def _add(counts,key,outcome):
    new=dict(counts)
    a,b=new.get(key,(0,0))
    new[key]=(a+int(outcome==0),b+int(outcome==1))
    return new


class BayesianChangePoint:
    """Fully fitted truncated run-length Beta filter, same source and actions.

    Hazard creates reset paths on every observed event. Unlike a rule oracle
    the filter never receives an evaluator boundary label. Run length >=48
    is pruned rather than silently granted an indefinitely fitted memory.
    """
    def __init__(self):
        self.states=[{"w":1.0,"run":0,"trans":{},"terminal":{}}]
        self.receipts={}
        self.n=0

    def _predict_state(self,state,context,first,next_state=None,second=None):
        key=str(context)+":"+str(first)
        if next_state is None:return _beta(state["trans"],key)
        k=":".join(str(v) for v in (context,first,next_state,second))
        return _beta(state["terminal"],k)

    def predict(self,view,first,next_state=None,second=None):
        ctx=view[0]
        if type(first) is not int or first not in (0,1):
            raise ValueError("CKAD44_BETA_ACTION")
        if next_state is None:
            return sum(s["w"]*self._predict_state(s,ctx,first) for s in self.states)
        # Conditional on observed transition, not terminal reward; source
        # weights are not updated until BOTH actual outcomes are provided.
        mass=[]
        for s in self.states:
            p=self._predict_state(s,ctx,first)
            mass.append(s["w"]*(p if next_state else 1-p))
        denom=sum(mass)
        if denom<=0:raise AssertionError("CKAD44_BETA_CONDITION_ZERO")
        return sum(w*self._predict_state(s,ctx,first,next_state,second)
                   for w,s in zip(mass,self.states))/denom

    def observe(self,identifier,views,row):
        if type(identifier) is not str or type(views) is not tuple or type(row) is not dict:
            raise ValueError("CKAD44_INVALID_BETA_SOURCE")
        rec=canonical([views,row]).decode("ascii")
        if identifier in self.receipts:
            if self.receipts[identifier]!=rec:
                raise ValueError("CKAD44_BETA_CONFLICTING_SOURCE_ID")
            return self
        if self.n>=E.MAX_EVENTS:raise ValueError("CKAD44_BETA_SOURCE_CAP")
        tkey=_cell_key(row)
        ykey=_cell_key(row,terminal=True)
        reset={"w":HAZARD*.25,"run":1,
               "trans":_add({},tkey,row["s2"]),
               "terminal":_add({},ykey,row["y"])}
        new=[reset]
        for state in self.states:
            if state["run"]>=RUN_CAP:
                continue
            p=_beta(state["trans"],tkey)
            q=_beta(state["terminal"],ykey)
            joint=(p if row["s2"] else 1-p)*(q if row["y"] else 1-q)
            new.append({"w":state["w"]*(1-HAZARD)*joint,
                "run":state["run"]+1,
                "trans":_add(state["trans"],tkey,row["s2"]),
                "terminal":_add(state["terminal"],ykey,row["y"])})
        denom=sum(s["w"] for s in new)
        if denom<=0 or not math.isfinite(denom):
            raise AssertionError("CKAD44_BETA_POSTERIOR_INVALID")
        for s in new:s["w"]/=denom
        self.states=new
        self.receipts[identifier]=rec
        self.n+=1
        if not(1<=len(self.states)<=RUN_CAP+1):
            raise AssertionError("CKAD44_BETA_RUN_LENGTH_CAP")
        return self

    def checkpoint(self):
        return canonical({"schema":"yggdrasil.ckad44.bocpd.v1",
             "states":self.states,"receipts":self.receipts,"n":self.n})

    @classmethod
    def restore(cls,raw,expected):
        if digest(raw)!=expected:raise ValueError("CKAD44_BETA_SHA")
        j=json.loads(raw)
        if j["schema"]!="yggdrasil.ckad44.bocpd.v1":
            raise ValueError("CKAD44_BETA_SCHEMA")
        obj=cls()
        obj.states=j["states"]
        obj.n=j["n"]
        obj.receipts=j["receipts"]
        if len(obj.receipts)!=obj.n or len(obj.states)>RUN_CAP+1:
            raise ValueError("CKAD44_BETA_INVALID_STATE")
        if obj.checkpoint()!=raw:raise ValueError("CKAD44_BETA_COLD_CHANGED")
        return obj


def run(seed):
    if seed not in DEV:raise ValueError("CKAD44_ONLY_REGISTERED_DEV")
    start,cpustart=time.perf_counter(),time.process_time()
    allrows=[]
    worlds=[]
    for world in C.WORLDS:
        events,private=C.generator(seed,world)
        native=NativeEpisodeExperience(repair=True)
        witness=ContrastiveCausalMemory()
        online=BayesianChangePoint()
        fitted=C.Conventional()
        first64=None
        warm48=None
        source_ids=set()
        eligible_reads=0
        diverse_reads=0
        for t,(identifier,views,row,phase) in enumerate(events):
            if t==48:
                native=native.begin_stream()
                warm48=digest(canonical(native._ledger[:48]))
            before_native=native.checkpoint()
            before_witness=witness.checkpoint()
            before_online=online.checkpoint()
            view=views[0]
            n_fn=native.context_forecast if t>=48 else native.forecast
            probs={"native_stream":(
               float(n_fn(view,row["x1"])),
               float(n_fn(view,row["x1"],row["s2"],row["x2"]))),
               "sham":(.5,.5),
               "beta_bocpd":(online.predict(view,row["x1"]),
                             online.predict(view,row["x1"],row["s2"],row["x2"]))}
            for arm in ("contrastive_recall","uniform_recall","frozen_reference",
                        "causal_discount93","causal_full","causal_dual","causal_action_masked"):
                probs[arm]=(witness.read(arm,view,row["x1"]),
                            witness.read(arm,view,row["x1"],row["s2"],row["x2"]))
            for arm in CONVENTIONAL:
                probs[arm]=(fitted.p(arm,"transition",row["s1"],row["x1"]),
                            fitted.p(arm,"terminal",row["s1"],row["x1"],
                                     row["s2"],row["x2"]))
            losses={a:pair_loss(*p,row) for a,p in probs.items()}
            if (native.checkpoint()!=before_native or
                witness.checkpoint()!=before_witness or
                online.checkpoint()!=before_online):
                raise AssertionError("CKAD44_FORECAST_MUTATED_SOURCE")
            if phase in PHASES:
                eligibility=witness.reference is not None and len(witness.history)==EVIDENCE_WINDOW
                diversity=eligibility and len({e["x1"] for e in witness.history})==2 and len({e["x2"] for e in witness.history})==2
                eligible_reads+=int(eligibility)
                diverse_reads+=int(diversity)
                allrows.append({"seed":seed,"world":world,"index":t,
                   "phase":phase,"loss":losses,
                   "evidence_weight_A":witness._weight(),
                   "evidence_window_eligible":eligibility,
                   "intervention_diversity":diversity})
            # Genuine public action-consequence update of EVERY arm only
            # AFTER score; private regime and phase never passed to learners.
            native=native.observe(identifier,views,row)
            witness.observe(identifier,views,row)
            online.observe(identifier,views,row)
            fitted.observe(row,{a:losses[a] for a in C.CONVENTIONAL})
            if identifier in source_ids:raise AssertionError("CKAD44_DUP_SOURCE")
            source_ids.add(identifier)
            if t==REFERENCE_EVENTS-1:
                first64=witness.reference.checkpoint()
        if (len(source_ids)!=len(events) or len(native._ledger)!=len(events)
            or witness.n!=len(events) or online.n!=len(events)):
            raise AssertionError("CKAD44_GENUINE_SOURCE_PARITY")
        if digest(canonical(native._ledger[:48]))!=warm48:
            raise AssertionError("CKAD44_NATIVE_SOURCE_ERASED")
        if witness.reference.checkpoint()!=first64:
            raise AssertionError("CKAD44_STABLE_REFERENCE_MODIFIED")
        na=native.checkpoint()
        ca=witness.checkpoint()
        bc=online.checkpoint()
        if NativeEpisodeExperience.restore(na,digest(na)).checkpoint()!=na:
            raise AssertionError("CKAD44_NATIVE_COLD")
        if ContrastiveCausalMemory.restore(ca,digest(ca)).checkpoint()!=ca:
            raise AssertionError("CKAD44_SOURCE_COLD")
        if BayesianChangePoint.restore(bc,digest(bc)).checkpoint()!=bc:
            raise AssertionError("CKAD44_BETA_COLD")
        last=events[-1]
        if any(obj.observe(last[0],last[1],last[2]) is not obj
               for obj in (native,witness,online)):
            raise AssertionError("CKAD44_DUPLICATE_NOT_IDEMPOTENT")
        altered=dict(last[2]);altered["y"]^=1
        for obj in (native,witness,online):
            try:obj.observe(last[0],last[1],altered)
            except ValueError:pass
            else:raise AssertionError("CKAD44_CONFLICT_ACCEPTED")
        if native.checkpoint()!=na or witness.checkpoint()!=ca or online.checkpoint()!=bc:
            raise AssertionError("CKAD44_CONFLICT_CHANGED_WEIGHTS")
        worlds.append({"world":world,"episodes":len(events),
          "authentic_observed_consequences":2*len(events),
          "native_sha256":digest(na),
          "frozen_reference_sha256":digest(first64),
          "candidate_sha256":digest(ca),"bocpd_sha256":digest(bc),
          "candidate_checkpoint_bytes":len(ca),"bocpd_checkpoint_bytes":len(bc),
          "source_complete":True,"source_original48_exact":True,
          "frozen64_exact":True,"cold_exact":True,"read_only":True,
          "duplicate_idempotent":True,"conflict_atomic":True,
          "bocpd_run_states":len(online.states),
          "candidate_trained_updates":witness.n,
          "bocpd_trained_updates":online.n,
          "evaluation_private_boundaries":private})
    metrics={}
    for phase in (*PHASES,"pooled_late_shift_and_return"):
        rows=[x for x in allrows if (x["phase"] in LATE if phase=="pooled_late_shift_and_return" else x["phase"]==phase)]
        if not rows:raise AssertionError("CKAD44_EVAL_PHASE_MISSING")
        metrics[phase]={"episodes":len(rows),
          "brier":{a:sum(x["loss"][a] for x in rows)/len(rows) for a in ARMS},
          "mean_frozen_A_probability":sum(x["evidence_weight_A"] for x in rows)/len(rows),
          "eligible_evidence_events":sum(x["evidence_window_eligible"] for x in rows),
          "intervention_diverse_events":sum(x["intervention_diversity"] for x in rows)}
    return {"seed":seed,"worlds":worlds,
      "total_episodes":sum(w["episodes"] for w in worlds),
      "total_consequences":sum(w["authentic_observed_consequences"] for w in worlds),
      "metrics":metrics,"evidence_window_eligible":eligible_reads,
      "diverse_evidence_window_count":diverse_reads,
      "wall_seconds":round(time.perf_counter()-start,6),
      "cpu_seconds":round(time.process_time()-cpustart,6)}


def classify(cases):
    if tuple(c["seed"] for c in cases)!=DEV:
        raise AssertionError("CKAD44_SOURCE_SEED_ORDER")
    for c in cases:
        for w in c["worlds"]:
            if not all(w[k] is True for k in
                ("source_complete","source_original48_exact","frozen64_exact",
                 "cold_exact","read_only","duplicate_idempotent","conflict_atomic")):
                return "SOURCE_INTEGRITY_FAILURE"
        metric=c["metrics"]
        p=metric["pooled_late_shift_and_return"]["brier"]
        cand=p["contrastive_recall"]
        best=min(p[a] for a in
            ("native_stream","causal_discount93","causal_full","causal_dual",
             "beta_bocpd",*CONVENTIONAL,"uniform_recall","frozen_reference"))
        if cand>.145 or cand>best-.01 or cand>p["causal_action_masked"]-.015:
            return "DEV_NO_GO"
        er=metric["early_return_A"]["brier"]
        lr=metric["late_return_A"]["brier"]
        lb=metric["late_B"]["brier"]
        if (er["contrastive_recall"]>er["native_stream"]+.005 or
            lr["contrastive_recall"]>lr["native_stream"]-.02 or
            lb["contrastive_recall"]>lb["native_stream"]+.005):
            return "DEV_NO_GO"
    return "DEV_FEASIBLE_NOT_SCIENTIFIC"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("preflight","dev"),required=True)
    p.add_argument("--seed",type=int)
    a=p.parse_args()
    if a.mode=="preflight":
        if a.seed is not None:raise ValueError("CKAD44_PREFLIGHT_SEED_FORBIDDEN")
        print(json.dumps({"schema":SCHEMA,"prereg":PREREG,
             "dev":list(DEV),"pilot_untouched":list(PILOT),
             "primary_untouched":list(PRIMARY),"first_use":False},sort_keys=True))
        return
    if a.seed not in DEV:raise ValueError("CKAD44_ONLY_REGISTERED_DEV")
    print("CKAD44_CASE="+json.dumps(run(a.seed),sort_keys=True))


if __name__=="__main__":
    main()

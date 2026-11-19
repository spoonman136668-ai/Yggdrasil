"""CKAD41: native causal source-trained microanchor archive, research DEV only.

All learning uses witnessed actions, observed transition and terminal outcome.
The original source-native model is trained unchanged.  Readout is label-free.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"CKAD-39"
sys.path.insert(0,str(PARENT))
spec=importlib.util.spec_from_file_location("ckad39_source_for_41",PARENT/"campaign.py")
C=importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

PREREG="3464c859e79b101894c9682042d460ced5068291"
SCHEMA="yggdrasil.ckad41.native-causal-microanchor-dev.v1"
DEV=(41101,41102)
RESERVED=(42101,42102,43101,43102,43103)
DISALLOWED=(40811,40812,38911,38912,39181,39182,14181,14182,14071,14072)
WINDOW=16
CAP=128
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")
LATE=("late_B","late_return_A")
CONVENTIONAL=(*C.CONVENTIONAL,"beta_hedge")
ARMS=("native_micro16","native_anchor32","native_stream",*CONVENTIONAL,"sham")


def outcome_loss(p,q,row):
    if not (0 <= p <= 1 and 0 <= q <= 1):
        raise AssertionError("CKAD41_PROBABILITY_RANGE")
    return ((p-row["s2"])**2+(q-row["y"])**2)/2


def event_prob(model,event):
    """Native model probability of an event known from PREVIOUS observations."""
    _,views,row,_=event
    p=float(model.forecast(views[0],row["x1"]))
    q=float(model.forecast(views[0],row["x1"],row["s2"],row["x2"]))
    if not (0<p<1 and 0<q<1):
        raise AssertionError("CKAD41_EVENT_PROBABILITY")
    return (p if row["s2"] else 1-p)*(q if row["y"] else 1-q)


class NativeAnchors:
    """Bounded, cumulative native-trained anchor memory. Never uses regime tags."""
    def __init__(self, block):
        if block not in (16,32):
            raise ValueError("CKAD41_BLOCK_SIZE")
        self.block=block
        self.archive=[]
        self.live=NativeEpisodeExperience(repair=True)
        self.live_start=0
        self.count=0
        self.seen=set()
        self.training_observations=0
        self.total_frozen=0

    def observe(self,event):
        identifier,views,row,_=event
        if identifier in self.seen:
            raise AssertionError("CKAD41_ANCHOR_DUPLICATE")
        # Exactly one new genuine observation, no source replay.
        self.live=self.live.observe(identifier,views,row)
        self.seen.add(identifier)
        self.count+=1
        self.training_observations+=1
        if self.count-self.live_start==self.block:
            self.archive.append((self.live_start,self.count,self.live))
            self.total_frozen+=1
            self.archive=self.archive[-(CAP//self.block):]
            self.live=NativeEpisodeExperience(repair=True)
            self.live_start=self.count
        if len(self.archive)*self.block>CAP or len(self.live._ledger)>=self.block:
            raise AssertionError("CKAD41_ARCHIVE_CAPACITY")

    def eligible(self,at):
        """Source model must end before the independent 16-event evidence window."""
        return [item for item in self.archive if item[1]<=at-WINDOW]

    def predict(self,events,view,first,next_state=None,second=None):
        at=len(events)
        options=self.eligible(at)
        if not options:
            return None
        recent=events[at-WINDOW:at]
        if len(recent)!=WINDOW:
            raise AssertionError("CKAD41_EVIDENCE_WINDOW")
        scores=[sum(math.log(event_prob(model,event)) for event in recent)
                for _,_,model in options]
        maximum=max(scores)
        weights=[math.exp(score-maximum) for score in scores]
        total=sum(weights)
        if not total>0:
            raise AssertionError("CKAD41_INVALID_EVIDENCE_MASS")
        posterior=[w/total for w in weights]
        if next_state is not None:
            transition=[float(model.forecast(view,first)) for _,_,model in options]
            weights=[w*(p if next_state else 1-p)
                     for w,p in zip(posterior,transition)]
            total=sum(weights)
            if not total>0:
                raise AssertionError("CKAD41_TERMINAL_ZERO_MASS")
            posterior=[w/total for w in weights]
        return sum(w*float(model.forecast(view,first,next_state,second))
                   for w,(_,_,model) in zip(posterior,options))


def phase_family(phase):
    if phase in ("warm","stable_A","early_return_A","late_return_A"):
        return "A"
    if phase in ("early_B","late_B"):
        return "B"
    raise ValueError("CKAD41_INVALID_PRIVATE_PHASE")


def run(seed):
    if seed not in DEV:
        raise ValueError("CKAD41_ONLY_REGISTERED_DEV")
    started=time.perf_counter()
    summaries=[]
    observations=[]
    for world in C.WORLDS:
        events,meta=C.generator(seed,world)
        witnessed=[]
        native=NativeEpisodeExperience(repair=True)
        micro=NativeAnchors(16)
        match=NativeAnchors(32)
        conventional=C.Conventional()
        prefix=None
        native_count=0
        read_count=0
        for t,event in enumerate(events):
            identifier,views,row,phase=event
            if t==48:
                native=native.begin_stream()
                prefix=digest(canonical(native._ledger[:48]))
            view=views[0]
            if t>=48:
                pn=float(native.context_forecast(view,row["x1"]))
                qn=float(native.context_forecast(view,row["x1"],row["s2"],row["x2"]))
            else:
                pn=float(native.forecast(view,row["x1"]))
                qn=float(native.forecast(view,row["x1"],row["s2"],row["x2"]))
            checkpoint=native.checkpoint()
            arch16=micro.eligible(t)
            arch32=match.eligible(t)
            p16=micro.predict(witnessed,view,row["x1"])
            q16=micro.predict(witnessed,view,row["x1"],row["s2"],row["x2"])
            p32=match.predict(witnessed,view,row["x1"])
            q32=match.predict(witnessed,view,row["x1"],row["s2"],row["x2"])
            if (p16 is None)!=(q16 is None) or (p32 is None)!=(q32 is None):
                raise AssertionError("CKAD41_ANCHOR_STAGE_MISMATCH")
            if native.checkpoint()!=checkpoint:
                raise AssertionError("CKAD41_ANCHOR_READ_MUTATED_NATIVE")
            read_count+=1
            probabilities={
                "native_micro16":(pn,qn) if p16 is None else (p16,q16),
                "native_anchor32":(pn,qn) if p32 is None else (p32,q32),
                "native_stream":(pn,qn),
                "sham":(.5,.5)
            }
            for arm in CONVENTIONAL:
                probabilities[arm]=(
                    conventional.p(arm,"transition",row["s1"],row["x1"]),
                    conventional.p(arm,"terminal",row["s1"],row["x1"],
                                   row["s2"],row["x2"]))
            losses={arm:outcome_loss(*probabilities[arm],row) for arm in ARMS}
            if phase in PHASES:
                # Strictly evaluation-only historical phase bookkeeping:
                # never reaches a readout, model.observe or source selector.
                eligible_b=sum(1 for start,stop,_ in arch16
                      if all(phase_family(witnessed[i][3])=="B"
                             for i in range(start,stop)))
                eligible_a=sum(1 for start,stop,_ in arch16
                      if all(phase_family(witnessed[i][3])=="A"
                             for i in range(start,stop)))
                observations.append({"seed":seed,"world":world,"t":t,
                       "phase":phase,"losses":losses,
                       "eligible_micro16":len(arch16),
                       "eligible_anchor32":len(arch32),
                       "pure_A_micro16":eligible_a,
                       "pure_B_micro16":eligible_b})
            # AFTER forecasts and score: train every independent model on
            # exactly the same genuine source tuple, never oracle phase.
            native=native.observe(identifier,views,row)
            micro.observe(event)
            match.observe(event)
            conventional.observe(row,{a:losses[a] for a in C.CONVENTIONAL})
            witnessed.append(event)
            native_count+=1
            if micro.count!=native_count or match.count!=native_count:
                raise AssertionError("CKAD41_SOURCE_EVENT_PARITY")
        if len(witnessed)!=len(events) or len(native._ledger)!=len(events):
            raise AssertionError("CKAD41_SOURCE_LEDGER_MISSING")
        if digest(canonical(native._ledger[:48]))!=prefix:
            raise AssertionError("CKAD41_OLD_SOURCE_ERASED")
        checkpoint=native.checkpoint()
        restored=NativeEpisodeExperience.restore(checkpoint,digest(checkpoint))
        if restored.checkpoint()!=checkpoint:
            raise AssertionError("CKAD41_COLD_INEXACT")
        old_event=events[-1]
        if native.observe(old_event[0],old_event[1],old_event[2]) is not native:
            raise AssertionError("CKAD41_DUPLICATE_NOT_IDEMPOTENT")
        tamper=dict(old_event[2]);tamper["y"]^=1
        try:
            native.observe(old_event[0],old_event[1],tamper)
        except ValueError:
            pass
        else:
            raise AssertionError("CKAD41_CONFLICT_ACCEPTED")
        if native.checkpoint()!=checkpoint:
            raise AssertionError("CKAD41_CONFLICT_MUTATED_NATIVE")
        if micro.training_observations!=len(events) or match.training_observations!=len(events):
            raise AssertionError("CKAD41_SOURCE_BUDGET_MISMATCH")
        summaries.append({"world":world,"episodes":len(events),
                          "consequences":len(events)*2,"cold_exact":True,
                          "source_preserved":True,"read_only":True,
                          "duplicate_idempotent":True,"conflict_atomic":True,
                          "checkpoint_sha256":digest(checkpoint),
                          "micro16_frozen_total":micro.total_frozen,
                          "anchor32_frozen_total":match.total_frozen,
                          "micro16_retained":len(micro.archive),
                          "anchor32_retained":len(match.archive),
                          "micro16_source_records":len(micro.archive)*micro.block,
                          "anchor32_source_records":len(match.archive)*match.block,
                          "forecast_reads":read_count,
                          "native_training_events":native_count,
                          "micro_training_events":micro.training_observations,
                          "anchor32_training_events":match.training_observations})
    groups={}
    for phase in (*PHASES,"pooled_late_shift_and_return"):
        selected=[row for row in observations
                  if (row["phase"] in LATE if phase=="pooled_late_shift_and_return"
                      else row["phase"]==phase)]
        if not selected:raise AssertionError("CKAD41_MISSING_EVALUATION_PHASE")
        groups[phase]={
             "episodes":len(selected),
             "brier":{arm:sum(row["losses"][arm] for row in selected)/len(selected)
                      for arm in ARMS},
             "eligible_micro16":sum(row["eligible_micro16"]>0 for row in selected),
             "eligible_anchor32":sum(row["eligible_anchor32"]>0 for row in selected),
             "pure_B_micro16":sum(row["pure_B_micro16"]>0 for row in selected),
             "pure_A_micro16":sum(row["pure_A_micro16"]>0 for row in selected)}
    return {"seed":seed,"worlds":summaries,
            "total_episodes":sum(w["episodes"] for w in summaries),
            "total_consequences":sum(w["consequences"] for w in summaries),
            "metric_groups":groups,
            "wall_seconds":round(time.perf_counter()-started,5)}


def classify(cases):
    if tuple(c["seed"] for c in cases)!=DEV:
        raise AssertionError("CKAD41_FROZEN_DEV_COHORT")
    integrity=all(all(w[k] is True for k in
            ("cold_exact","source_preserved","read_only","duplicate_idempotent",
             "conflict_atomic")) and
            w["micro16_source_records"]<=CAP and w["anchor32_source_records"]<=CAP
            and w["native_training_events"]==w["micro_training_events"]==
                w["anchor32_training_events"] for c in cases for w in c["worlds"])
    if not integrity:
        return "INVALID_SOURCE"
    for case in cases:
        metrics=case["metric_groups"]
        pooled=metrics["pooled_late_shift_and_return"]["brier"]
        candidate=pooled["native_micro16"]
        competitor=min(pooled[a] for a in
                       ("native_stream","native_anchor32",*CONVENTIONAL))
        if not (candidate<=.145 and candidate<=competitor-.015):
            return "DEV_NO_GO"
        for phase in ("early_B","early_return_A"):
            b=metrics[phase]["brier"]
            if b["native_micro16"]>b["native_stream"]+.005:
                return "DEV_NO_GO"
    return "DEV_FEASIBLE_NOT_SCIENTIFIC"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("preflight","dev"),required=True)
    parser.add_argument("--seed",type=int)
    a=parser.parse_args()
    if a.mode=="preflight":
        if a.seed is not None:raise ValueError("CKAD41_PREFLIGHT_SEED_FORBIDDEN")
        print(json.dumps({"schema":SCHEMA,"prereg":PREREG,
                          "dev_seeds":list(DEV),"reserved":list(RESERVED),
                          "pilot_scored":False,"primary_scored":False}))
        return
    if a.seed not in DEV:raise ValueError("CKAD41_ONLY_REGISTERED_DEV")
    print("CKAD41_CASE="+json.dumps(run(a.seed),sort_keys=True))


if __name__=="__main__":
    main()

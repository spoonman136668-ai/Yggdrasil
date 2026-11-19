"""CKAD45: closed-loop native causal intervention learning vs strong active controls.

Every action is chosen from publicly witnessed state and already trained
knowledge. The environment alone holds true causal families, latent phase
and exogenous outcome randomness. A fixed common exhaustive examiner is
read-only, never fed to any learner and never counted as training evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import random
import sys
import time
from collections import deque
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE=Path(__file__).resolve().parent
EXACT=HERE.parent/"CKAD-42"/"campaign.py"
spec=importlib.util.spec_from_file_location("ckad42_exact_for_45",EXACT)
E=importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)
C=E.C
SCHEMA="yggdrasil.ckad45.closed-loop-native-causal-dev.v1"
PREREG="ab6f435adcbb09116efde103c4be5614db6f1d0c"
DEV=(45111,45112)
PILOT=(45211,45212)
PRIMARY=(45311,45312,45313)
EXCLUDED=(44111,44112,43111,43112,42111,42112,41101,41102,40811,40812)
POLICIES=("ipfc_contradiction","exact_info_gain","beta_info_gain",
          "balanced_coverage","random_interventions","fixed_zero_negative")
N=232
FIRST_CHANGE=92
RETURN=164
WARM=48
PROBE_STEP=8
RECENT=12
ALARM=.19
DISAGREE=4.0
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")
LATE=("late_B","late_return_A")


def private_phase(t):
    if t<WARM:return "warm"
    if t<FIRST_CHANGE:return "stable_A"
    if t<FIRST_CHANGE+24:return "early_B"
    if t<RETURN:return "late_B"
    if t<RETURN+24:return "early_return_A"
    return "late_return_A"


def _true_bits(world,regime,ctx,first,state,second):
    """Private evaluator and environment: NEVER exposed to PolicyLearner."""
    if world not in (0,1) or regime not in ("A","B"):
        raise ValueError("CKAD45_PRIVATE_WORLD")
    if world==0:
        if regime=="A":
            t=ctx ^ first
            y=(ctx&first)^(state&second)
        else:
            t=ctx ^ (first&(1-ctx))
            y=(ctx|first)&(state^second)
    else:
        if regime=="A":
            t=ctx&(1-first)
            y=ctx^(state|second)
        else:
            t=1^(ctx^first)
            y=(ctx&(1-state))^(first|second)
    return t,y


def true_probabilities(world,t,ctx,first,state,second):
    if not all(type(z) is int and z in (0,1) for z in
               (ctx,first,state,second)):
        raise ValueError("CKAD45_PRIVATE_BINARY")
    regime="B" if FIRST_CHANGE<=t<RETURN else "A"
    tbit,ybit=_true_bits(world,regime,ctx,first,state,second)
    return (.85 if tbit else .15),(.90 if ybit else .10)


def exogenous(seed,world):
    """Identical contexts, nuisance bits and outcome uniforms across policies."""
    if seed not in DEV and seed!=999:
        raise ValueError("CKAD45_EXOGENOUS_UNREGISTERED_SEED")
    rng=random.Random(C.seedint("ckad45-exogenous-v1",seed,world))
    return tuple((rng.randrange(2),rng.randrange(2),rng.randrange(2),
                  rng.random(),rng.random()) for _ in range(N))


def binary_entropy(p):
    if not(0.0<=p<=1.0) or not math.isfinite(p):
        raise ValueError("CKAD45_INVALID_PROBABILITY")
    if p==0 or p==1:return 0.0
    return -p*math.log(p)-(1-p)*math.log(1-p)


def _expected_brier(p,target):
    # E[(p-Y)^2] for Y~Bernoulli(target); not a sampled or trained outcome.
    e=p-target
    return e*e+target*(1-target)


class PolicyLearner:
    def __init__(self,policy,seed,world):
        if policy not in POLICIES or world not in (0,1):
            raise ValueError("CKAD45_UNREGISTERED_POLICY")
        self.policy,self.seed,self.world=policy,seed,world
        self.native=NativeEpisodeExperience(repair=True)
        self.causal=E.NativeInterventionRelations()
        self.beta_transition={}
        self.beta_terminal={}
        self.cover_transition={}
        self.cover_terminal={}
        self.loss_history=deque(maxlen=RECENT)
        self.actual_actions=[]
        self.ids=set()
        self.n=0
        self.first48_sha=None
        self.triggered_episodes=0
        self.probe_checks=0

    def _base_key(self,view,first,state=None,second=None):
        ctx=view[0]
        if state is None:return (ctx,first)
        return (ctx,first,state,second)

    def _score(self,view,first,state=None,second=None):
        if self.policy=="beta_info_gain":
            key=self._base_key(view,first,state,second)
            bank=self.beta_transition if state is None else self.beta_terminal
            a,b=bank.get(key,(0,0))
            p=(b+1)/(a+b+2)
            return binary_entropy(p)
        p_short=self.causal.read("short",view,first,state,second)
        info=binary_entropy(p_short)
        if (self.policy=="ipfc_contradiction"
                and len(self.loss_history)==RECENT
                and sum(self.loss_history)/RECENT>ALARM):
            p_full=self.causal.read("full",view,first,state,second)
            diff=p_full-p_short
            return info+DISAGREE*diff*diff
        return info

    def _choose(self,view,t,first=None,state=None):
        stage=1 if first is None else 2
        if self.policy=="fixed_zero_negative":
            return 0
        if self.policy=="random_interventions":
            return C.seedint("ckad45-independent-random",self.seed,self.world,
                             t,stage)&1
        if self.policy=="balanced_coverage":
            bank=self.cover_transition if stage==1 else self.cover_terminal
            options=[(bank.get(self._base_key(view,a) if stage==1
                               else self._base_key(view,first,state,a),0),a)
                     for a in (0,1)]
            minseen=min(x[0] for x in options)
            ties=[a for n,a in options if n==minseen]
            if len(ties)==1:return ties[0]
        else:
            # Both intervention actions are selected before their own
            # consequence: stage2 sees genuine already observed next_state.
            scores=[self._score(view,a) if stage==1 else
                    self._score(view,first,state,a) for a in (0,1)]
            rounded=[round(s,12) for s in scores]
            maximum=max(rounded)
            ties=[i for i,x in enumerate(rounded) if x==maximum]
            if len(ties)==1:return ties[0]
        return C.seedint("ckad45-common-action-tie",self.seed,self.world,t,stage)&1

    def choose_first(self,view,t):
        return self._choose(view,t)

    def choose_second(self,view,t,first,observed_state):
        if (type(first) is not int or first not in (0,1)
                or type(observed_state) is not int or observed_state not in (0,1)):
            raise ValueError("CKAD45_SECOND_ACTION_INPUT")
        return self._choose(view,t,first,observed_state)

    def predict_stage1(self,view,first):
        return float(self.causal.read("short",view,first))

    def predict_stage2(self,view,first,observed_state,second):
        return float(self.causal.read("short",view,first,observed_state,second))

    def observe(self,identifier,views,row,predictions):
        if identifier in self.ids:
            raise AssertionError("CKAD45_DUPLICATED_POLICY_EVENT")
        if len(predictions)!=2:raise ValueError("CKAD45_MISSING_PREQUENTIAL_FORECASTS")
        p,q=predictions
        dt=p-row["s2"]
        dy=q-row["y"]
        self.loss_history.append((dt*dt+dy*dy)*.5)
        self.causal.observe(identifier,views,row)
        self.native=self.native.observe(identifier,views,row)
        a=self._base_key(views[0],row["x1"])
        b=self._base_key(views[0],row["x1"],row["s2"],row["x2"])
        for bank,key,val in ((self.beta_transition,a,row["s2"]),
                             (self.beta_terminal,b,row["y"])):
            n0,n1=bank.get(key,(0,0))
            bank[key]=(n0+int(val==0),n1+int(val==1))
        self.cover_transition[a]=self.cover_transition.get(a,0)+1
        self.cover_terminal[b]=self.cover_terminal.get(b,0)+1
        self.actual_actions.append((row["x1"],row["x2"]))
        self.ids.add(identifier)
        self.n+=1
        if self.n!=self.causal.n or self.n!=len(self.native._ledger):
            raise AssertionError("CKAD45_SOURCE_COUNT_MISMATCH")

    def begin_stream(self):
        if self.n!=WARM:raise AssertionError("CKAD45_WARM_AT_WRONG_SOURCE")
        self.native=self.native.begin_stream()
        self.first48_sha=digest(canonical(self.native._ledger[:WARM]))

    def check_cold_and_source(self,last):
        raw_n=self.native.checkpoint()
        raw_c=self.causal.checkpoint()
        if (NativeEpisodeExperience.restore(raw_n,digest(raw_n)).checkpoint()!=raw_n or
                E.NativeInterventionRelations.restore(raw_c,digest(raw_c)).checkpoint()!=raw_c):
            raise AssertionError("CKAD45_COLD_NONIDENTICAL")
        if digest(canonical(self.native._ledger[:WARM]))!=self.first48_sha:
            raise AssertionError("CKAD45_OLD_SOURCE_ERASED")
        if (self.n!=N or self.causal.n!=N or
                len(self.causal.receipts)!=N or len(self.ids)!=N):
            raise AssertionError("CKAD45_INCOMPLETE_SOURCE")
        identifier,views,row=last
        if self.native.observe(identifier,views,row) is not self.native:
            raise AssertionError("CKAD45_NATIVE_DUPLICATE")
        if self.causal.observe(identifier,views,row) is not self.causal:
            raise AssertionError("CKAD45_CAUSAL_DUPLICATE")
        alternate=dict(row)
        alternate["y"]^=1
        for learner in (self.native,self.causal):
            try:learner.observe(identifier,views,alternate)
            except ValueError:pass
            else:raise AssertionError("CKAD45_CONFLICT_ACCEPTED")
        if raw_n!=self.native.checkpoint() or raw_c!=self.causal.checkpoint():
            raise AssertionError("CKAD45_CONFLICT_MUTATED_SOURCE")
        return {"native_sha256":digest(raw_n),"causal_sha256":digest(raw_c),
                "native_checkpoint_bytes":len(raw_n),
                "causal_checkpoint_bytes":len(raw_c),
                "source_episodes":self.n,
                "chosen_actions":2*self.n,"source_unique":True,
                "prefix48_exact":True,"cold_exact":True,
                "duplicate_idempotent":True,"conflict_atomic":True}


def examiner(learner,world,t):
    """Off-policy action-independent *evaluation only*, zero training events."""
    before_native=learner.native.checkpoint()
    before_causal=learner.causal.checkpoint()
    total_causal=0.0
    total_native=0.0
    nb=learner.native.context_forecast if t>=WARM else learner.native.forecast
    for context in (0,1):
        view=(context,0) # fixed, shared nuisance view on common unseen probe
        for first in (0,1):
            pc=float(learner.causal.read("short",view,first))
            pn=float(nb(view,first))
            for observed_state in (0,1):
                for second in (0,1):
                    pt,py=true_probabilities(world,t,context,first,observed_state,second)
                    qc=float(learner.causal.read("short",view,first,observed_state,second))
                    qn=float(nb(view,first,observed_state,second))
                    total_causal+=(_expected_brier(pc,pt)+_expected_brier(qc,py))*.5
                    total_native+=(_expected_brier(pn,pt)+_expected_brier(qn,py))*.5
    if (before_native!=learner.native.checkpoint() or
            before_causal!=learner.causal.checkpoint()):
        raise AssertionError("CKAD45_EXAMINER_CONTAMINATED_TRAINING")
    learner.probe_checks+=1
    return {"causal":total_causal/16,"native":total_native/16}


def score_world(seed,world):
    if seed not in DEV and seed!=999:
        raise ValueError("CKAD45_ONLY_REGISTERED_DEV")
    exo=exogenous(seed,world)
    members={p:PolicyLearner(p,seed,world) for p in POLICIES}
    probes=[]
    worlds_meta=[]
    observed_source={}
    for t,(context,v1,v2,noise_transition,noise_terminal) in enumerate(exo):
        phase=private_phase(t)
        for name,learner in members.items():
            if t==WARM:learner.begin_stream()
            if t>=WARM and t%PROBE_STEP==0:
                probe=examiner(learner,world,t)
                probes.append({"world":world,"t":t,"phase":phase,"policy":name,
                               "causal_expected_brier":probe["causal"],
                               "native_expected_brier":probe["native"]})
            views=((context,v1),(context,v2))
            action1=learner.choose_first(views[0],t)
            if (name=="ipfc_contradiction" and len(learner.loss_history)==RECENT
                 and sum(learner.loss_history)/RECENT>ALARM):
                learner.triggered_episodes+=1
            first_pred=learner.predict_stage1(views[0],action1)
            transition_true,_=true_probabilities(world,t,context,action1,0,0)
            state=int(noise_transition<transition_true)
            action2=learner.choose_second(views[0],t,action1,state)
            terminal_pred=learner.predict_stage2(views[0],action1,state,action2)
            _,terminal_true=true_probabilities(world,t,context,action1,state,action2)
            outcome=int(noise_terminal<terminal_true)
            row={"s1":context,"x1":action1,"s2":state,"x2":action2,"y":outcome}
            ident=hashlib.sha256(f"ckad45|{seed}|{world}|{name}|{t}".encode("ascii")).hexdigest()
            learner.observe(ident,views,row,(first_pred,terminal_pred))
            if t==N-1:observed_source[name]=(ident,views,row)
    for name,learner in members.items():
        m=learner.check_cold_and_source(observed_source[name])
        m["policy"]=name
        m["world"]=world
        m["triggered_source_episodes"]=learner.triggered_episodes
        m["exhaustive_read_only_probes"]=learner.probe_checks
        m["action_sequence_sha256"]=digest(canonical(learner.actual_actions))
        m["action_sequence"]=learner.actual_actions
        worlds_meta.append(m)
    ipfc=members["ipfc_contradiction"].actual_actions
    ig=members["exact_info_gain"].actual_actions
    disagree=sum(x!=y for pair_x,pair_y in zip(ipfc,ig)
                 for x,y in zip(pair_x,pair_y))
    difference=disagree/(2*N)
    return probes,worlds_meta,difference


def score_seed(seed):
    if seed not in DEV:raise ValueError("CKAD45_ONLY_REGISTERED_DEV")
    start=time.perf_counter()
    cpu=time.process_time()
    probes=[]
    worlds=[]
    diffs=[]
    for world in (0,1):
        p,w,d=score_world(seed,world)
        probes.extend(p)
        worlds.extend(w)
        diffs.append(d)
    metrics={}
    for phase in (*PHASES,"pooled_late_shift_and_return"):
        selected=[r for r in probes if (r["phase"] in LATE if phase=="pooled_late_shift_and_return"
                  else r["phase"]==phase)]
        if not selected:raise AssertionError("CKAD45_MISSING_EXAMINER_PHASE")
        metrics[phase]={"world_probe_count":len(selected)//len(POLICIES),
                        "causal":{},"native":{}}
        for p in POLICIES:
            own=[r for r in selected if r["policy"]==p]
            if not own:raise AssertionError("CKAD45_MISSING_POLICY_EXAMINER")
            metrics[phase]["causal"][p]=sum(x["causal_expected_brier"] for x in own)/len(own)
            metrics[phase]["native"][p]=sum(x["native_expected_brier"] for x in own)/len(own)
    return {"seed":seed,"worlds":worlds,
            "total_actual_training_episodes":sum(w["source_episodes"] for w in worlds),
            "total_actual_training_consequences":2*sum(w["source_episodes"] for w in worlds),
            "common_action_independent_probe_points":len(probes),
            "policies":list(POLICIES),
            "candidate_action_difference_fraction_per_world":diffs,
            "candidate_action_difference_fraction":sum(diffs)/len(diffs),
            "metrics":metrics,
            "wall_seconds":round(time.perf_counter()-start,5),
            "cpu_seconds":round(time.process_time()-cpu,5)}


def classify(cases):
    if tuple(x["seed"] for x in cases)!=DEV:
        raise AssertionError("CKAD45_FROZEN_DEV_ORDER")
    for case in cases:
        if not all(w[k] is True for w in case["worlds"] for k in
            ("source_unique","prefix48_exact","cold_exact","duplicate_idempotent",
             "conflict_atomic")):
            return "SOURCE_INTEGRITY_FAILURE"
        if case["candidate_action_difference_fraction"]<.10:
            return "DEV_NO_GO"
        m=case["metrics"]
        late=m["pooled_late_shift_and_return"]
        candidate=late["causal"]["ipfc_contradiction"]
        best=min(v for k,v in late["causal"].items() if k!="ipfc_contradiction")
        best_native=min(v for k,v in late["native"].items() if k!="ipfc_contradiction")
        if (candidate>.145 or candidate>best-.010 or
            late["native"]["ipfc_contradiction"]>best_native+.005):
            return "DEV_NO_GO"
        er=m["early_return_A"]["causal"]
        if er["ipfc_contradiction"]>min(v for k,v in er.items() if k!="ipfc_contradiction")+.010:
            return "DEV_NO_GO"
        ret=m["late_return_A"]["causal"]
        if ret["ipfc_contradiction"]>ret["exact_info_gain"]-.010:
            return "DEV_NO_GO"
    return "DEV_FEASIBLE_NOT_SCIENTIFIC"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("preflight","dev"),required=True)
    p.add_argument("--seed",type=int)
    x=p.parse_args()
    if x.mode=="preflight":
        if x.seed is not None:raise ValueError("CKAD45_PREFLIGHT_NO_SEED")
        print(json.dumps({"schema":SCHEMA,"prereg":PREREG,"DEV":list(DEV),
             "pilot_unconsumed":list(PILOT),"primary_unconsumed":list(PRIMARY),
             "policies":list(POLICIES),"full_final_regression":False,
             "first_use":False},sort_keys=True))
        return
    if x.seed not in DEV:raise ValueError("CKAD45_ONLY_REGISTERED_DEV")
    print("CKAD45_CASE="+json.dumps(score_seed(x.seed),sort_keys=True,
                                  separators=(",",":")))


if __name__=="__main__":
    main()

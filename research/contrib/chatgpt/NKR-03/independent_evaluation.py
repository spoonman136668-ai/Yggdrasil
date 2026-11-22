"""NKR-03 fresh public causal evidence: independent controls and safe readout.

Source is a new PUBLIC deterministic synthetic family; not a protected first-use
and not proof of open-world native knowledge. Training outcomes shared exactly
across four pre-frozen audit budgets and all distinct native/control learners.
"""
from __future__ import annotations

import hashlib
import json
import time
import tracemalloc

import numpy as np

from source import TRAIN,AUDIT,UNAUDITED,FAMILIES,PAIR_TERMS,law
from yggdrasil.native_relation_memory import NativeRelationMemory
from yggdrasil.public_causal_cells import PublicCausalCells

BUDGETS=(12,8,4,0)
PREREG="257a37a0e5c6c962191da5c247a2fc133eb9ba42"
TEST=AUDIT+UNAUDITED

def exact_quadratic_control(observations):
    """Entirely independent per-action 11-row public GF2 feature fit.

    Six pair-interaction effects are identifiable only if the matching pair
    source context was actually probed. An absent higher-order effect is
    assigned zero (an explicit non-identifiable control assumption).
    """
    fitted={}
    for action in (0,1):
        d={ctx:value for ctx,arm,value in observations if arm==action}
        if not set(TRAIN).issubset(d):
            raise ValueError("independent control lacks public singleton interventions")
        bias=d[0]
        single=sum((d[1<<j]^bias)<<j for j in range(4))
        pairs=0
        for p,(i,j) in enumerate(PAIR_TERMS):
            context=(1<<i)|(1<<j)
            if context in d:
                predicted=bias^((single>>i)&1)^((single>>j)&1)
                pairs|=(d[context]^predicted)<<p
        fitted[action]=(bias,single,pairs)
    def predict(context,action):
        bias,single,pairs=fitted[action]
        out=bias^((context&single).bit_count()&1)
        for p,(i,j) in enumerate(PAIR_TERMS):
            if ((context>>i)&1) and ((context>>j)&1):
                out^=(pairs>>p)&1
        return out
    return predict

class GradientMLP:
    """Actually fit a fixed 32-hidden tanh network with gradient Adam."""
    def __init__(self,seed):
        rng=np.random.default_rng(seed)
        self.W=rng.normal(0,0.23,(5,32))
        self.b=np.zeros((1,32),dtype=np.float64)
        self.V=rng.normal(0,0.23,(32,1))
        self.c=np.zeros((1,1),dtype=np.float64)

    @staticmethod
    def design(rows):
        return np.asarray(
            [[2*((ctx>>bit)&1)-1 for bit in range(4)]+[2*action-1]
             for ctx,action in rows],dtype=np.float64)

    def fit(self,observations):
        x=self.design([(context,action) for context,action,_ in observations])
        y=np.asarray([[value] for _,_,value in observations],dtype=np.float64)
        parameters=(self.W,self.b,self.V,self.c)
        m=[np.zeros_like(p) for p in parameters]
        v=[np.zeros_like(p) for p in parameters]
        for step in range(1,2001):
            hidden=np.tanh(x@self.W+self.b)
            logits=hidden@self.V+self.c
            prob=1/(1+np.exp(-np.clip(logits,-30,30)))
            delta=(prob-y)/len(observations)
            dV=hidden.T@delta
            dc=np.sum(delta,axis=0,keepdims=True)
            upstream=delta@self.V.T*(1-hidden**2)
            dW=x.T@upstream
            db=np.sum(upstream,axis=0,keepdims=True)
            for k,(param,g) in enumerate(zip(parameters,(dW,db,dV,dc))):
                m[k][...]=0.9*m[k]+0.1*g
                v[k][...]=0.999*v[k]+0.001*g*g
                param-=0.035*(m[k]/(1-0.9**step))/(
                    np.sqrt(v[k]/(1-0.999**step))+1e-8)
        self.train_correct=sum(self.predict(ctx,action)==value
                               for ctx,action,value in observations)
        return self

    def predict(self,ctx,action):
        x=self.design(((ctx,action),))
        score=np.tanh(x@self.W+self.b)@self.V+self.c
        return int(score[0,0]>=0)

def evaluate():
    begin=time.perf_counter()
    cpustart=time.process_time()
    tracemalloc.start()
    try:
        records={}
        transcript=[]
        for family in FAMILIES:
            records[family]={}
            for extra in BUDGETS:
                row={method:{"success":0,"total":0}
                     for method in (
                        "native_verified","incumbent","independent_exact_lookup",
                        "independent_quadratic_symbolic","gradient_MLP",
                        "unguarded_native_ablation")}
                payload={
                    "scores":row, "verified_supported_pairs":0,
                    "verified_pair_correct":0,
                    "unsupported_confident_claims":0,
                    "unsupported_fallback_same_as_incumbent":0,
                    "unique_evidence":0,
                    "verified_exceptions":0,
                    "repeat_aliases_ignored":0,
                    "cold_restores":0,
                    "old_ypc_bytes":0,
                    "max_verification_checkpoint_bytes":0,
                    "gradient_train_correct":0,
                    "gradient_train_total":0,
                }
                for slot in range(16):
                    ret=slot>=7
                    addr=slot-7 if ret else slot
                    cells=PublicCausalCells()
                    bank=NativeRelationMemory()
                    obs=[]
                    inputs=list(TRAIN)+list(AUDIT[:extra//2])
                    for context in inputs:
                        for action in (0,1):
                            value=law(slot,context,action,family)
                            event=(context,action,value)
                            obs.append(event)
                            transcript.append((family,extra,slot,context,action,value))
                            cells.observe(addr,action,value,retained=ret)
                            observed=(bank.observe_public
                                      if context in TRAIN
                                      else bank.observe_public_verified)
                            if not observed(addr,context,action,value,
                                     f"nkr03:{family}:{slot}:{context}:{action}",
                                     retained=ret):
                                raise AssertionError("new source observation unexpectedly duplicate")
                    if len(obs)!=10+extra:
                        raise AssertionError("mismatched actual interventions")
                    native_checkpoint=bank.checkpoint()
                    old_checkpoint=cells.snapshot()
                    if len(old_checkpoint)!=164:
                        raise AssertionError("legacy state format changed")
                    payload["old_ypc_bytes"]=164
                    payload["unique_evidence"]+=bank.unique_observations
                    payload["verified_exceptions"]+=bank.verified_exception_count
                    payload["max_verification_checkpoint_bytes"]=max(
                        payload["max_verification_checkpoint_bytes"],len(native_checkpoint))
                    # Same-source duplicate or aliased source must not count again.
                    for context,action,value in obs:
                        if bank.observe_public_verified(addr,context,action,value,
                                  f"nkr03:duplicate:alias:{slot}",retained=ret):
                            raise AssertionError("duplicate semantics added knowledge")
                        payload["repeat_aliases_ignored"]+=1
                    if bank.checkpoint()!=native_checkpoint:
                        raise AssertionError("duplicate evidence rewrote checkpoint")
                    old=PublicCausalCells.restore(old_checkpoint)
                    cold=NativeRelationMemory.restore(native_checkpoint)
                    if cold.checkpoint()!=native_checkpoint:
                        raise AssertionError("cold weight repair not replayable")
                    payload["cold_restores"]+=1
                    external_lookup={(context,action):value
                                     for context,action,value in obs}
                    symbolic=exact_quadratic_control(obs)
                    net=GradientMLP(1000+slot+100*(family=="cubic")+extra).fit(obs)
                    payload["gradient_train_correct"]+=net.train_correct
                    payload["gradient_train_total"]+=len(obs)
                    for context in TEST:
                        direct_pair=bank.observed_action_pair(addr,context,retained=ret)
                        native=cells.choose_verified_contextual(addr,context,
                                                             bank,retained=ret)
                        same_cold=old.choose_verified_contextual(addr,context,
                                                              cold,retained=ret)
                        if native!=same_cold:
                            raise AssertionError("cold native decision changed")
                        incumbent=cells.choose(addr,retained=ret)
                        if incumbent not in (0,1) or native not in (0,1):
                            raise AssertionError("unexpected abstention")
                        if direct_pair is None:
                            if native!=incumbent:
                                raise AssertionError("unsupported context changed incumbent")
                            payload["unsupported_fallback_same_as_incumbent"]+=1
                        else:
                            payload["verified_supported_pairs"]+=1
                            if direct_pair != (law(slot,context,0,family),
                                               law(slot,context,1,family)):
                                raise AssertionError("public observed context effect incorrect")
                            payload["verified_pair_correct"]+=int(
                                law(slot,context,native,family)==1)
                        lookup={
                            a:external_lookup.get((context,a))
                            for a in (0,1)
                        }
                        if lookup[0] is not None and lookup[1] is not None:
                            external=0 if lookup[0]>lookup[1] else 1 if lookup[1]>lookup[0] else incumbent
                        else:
                            external=incumbent
                        symbolic_action=0 if symbolic(context,0)>symbolic(context,1) else 1
                        gradient_action=0 if net.predict(context,0)>net.predict(context,1) else 1
                        unguarded=cells.choose_contextual(addr,context,bank,retained=ret)
                        actions={
                            "native_verified":native,
                            "incumbent":incumbent,
                            "independent_exact_lookup":external,
                            "independent_quadratic_symbolic":symbolic_action,
                            "gradient_MLP":gradient_action,
                            "unguarded_native_ablation":unguarded
                        }
                        for method,action in actions.items():
                            row[method]["success"]+=law(slot,context,action,family)
                            row[method]["total"]+=1
                if payload["verified_supported_pairs"]!=16*(extra//2):
                    raise AssertionError("source budget/verified coverage mismatch")
                if payload["unsupported_fallback_same_as_incumbent"]!=16*(11-extra//2):
                    raise AssertionError("unsupported causal extrapolation")
                if payload["verified_pair_correct"]!=payload["verified_supported_pairs"]:
                    raise AssertionError("actual evidenced pair action predicted incorrectly")
                if payload["unique_evidence"]!=16*(10+extra):
                    raise AssertionError("public observation count mismatch")
                if payload["repeat_aliases_ignored"]!=payload["unique_evidence"]:
                    raise AssertionError("not all aliases rejected")
                if payload["cold_restores"]!=16:
                    raise AssertionError("missing cold restores")
                if row["native_verified"]["success"]!=row["independent_exact_lookup"]["success"]:
                    raise AssertionError("native unexpectedly exceeds/loses against exact lookup")
                improved=row["native_verified"]["success"]-row["incumbent"]["success"]
                payload["native_minus_incumbent_pp"]=round(improved*100/176,6)
                records[family][str(extra)]=payload
        high=[records[f]["12"] for f in FAMILIES]
        good=all(x["verified_pair_correct"]==96
                 and x["unsupported_fallback_same_as_incumbent"]==80
                 and x["native_minus_incumbent_pp"]>=15
                 and x["unsupported_confident_claims"]==0 for x in high)
        return {
            "schema":"nkr03.actual-native-evidence-dev.v1",
            "frozen_prereg_sha":PREREG,
            "public_synthetic_not_original_first_use":True,
            "native_source_unmodified_at_runner":True,
            "native_supported_safety_dev_gate":good,
            "scientific_superiority":False,
            "accepted_main_updated":False,
            "classification":"SUPPORTED_DEV_ONLY_NO_PROMOTION" if good
                else "MIXED_OR_NEGATIVE_NO_PROMOTION",
            "source_namespaces":list(FAMILIES),
            "budget_descending":list(BUDGETS),
            "records":records,
            "observation_transcript_sha256":hashlib.sha256(
                json.dumps(transcript,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
            "cpu_seconds":time.process_time()-cpustart,
            "wall_seconds":time.perf_counter()-begin,
            "peak_tracemalloc_bytes":tracemalloc.get_traced_memory()[1],
            "limitations":"New PUBLIC synthetic quadratic/cubic four-bit world laws. Verified supported pair outcomes are observed, not inferred OOD generalization. Exact lookup control must tie. Unsupported higher-order triples abstain to unchanged incumbent, without guarantee those decisions are correct. No real provider trust or production knowledge population. Tracemalloc total cost not matched native speedup."
        }
    finally:
        tracemalloc.stop()

if __name__=="__main__":
    print("NKR03_SUPPORTED_NATIVE_DEV="+json.dumps(evaluate(),sort_keys=True,separators=(",",":")),flush=True)

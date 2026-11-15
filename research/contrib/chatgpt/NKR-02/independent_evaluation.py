"""NKR-02 preregistered independent DEV comparison, no protected first-use data.

This evaluator imports the Yggdrasil native decision path and gives its incumbent,
an independently authored GF(2) exact symbolic learner, a fully trained Adam MLP,
and an evidence-only policy exactly the SAME PUBLIC interventions.

Quadratic novelty outside NKR01's affine/action-context grammar is a separate
negative control. Original WSP114/115 data and weights are NOT imported.
"""
from __future__ import annotations

import hashlib
import json
import time
import tracemalloc

import numpy as np

from yggdrasil.native_relation_memory import NativeRelationMemory
from yggdrasil.public_causal_cells import PublicCausalCells

TRAIN=(0,1,2,4,8)
TEST=(3,5,6,7,9,10,11,12,13,14,15)
NATIVE=16
PREREG="2aedc2a5ab0da62563fca1c8dbd079a18a634f6d"

def sealed_parameters(slot, family="affine-v2"):
    if type(slot) is not int or not 0<=slot<NATIVE:
        raise ValueError("invalid source slot")
    key=f"NKR02|public|fresh-disjoint-context|20261115|{family}|{slot}".encode()
    digest=hashlib.sha256(key).digest()
    return (digest[0]&15,(digest[1]>>3)&1)

def consequence(slot,context,action,quadratic=False):
    if not 0<=context<16 or action not in (0,1):
        raise ValueError("invalid public intervention")
    mask,bias=sealed_parameters(slot)
    value=bias ^ ((context&mask).bit_count()&1) ^ action
    # Both source families are identical on all five public source contexts.
    # The additional relation only affects never-observed composite contexts.
    if quadratic:
        value^=(context&3)==3
    return int(value)

def independent_symbolic_fit(observations):
    """Five linearly independent known public contexts per action.

    Independent fit via differences from action-specific base responses, not
    NKR's 10-column GF(2) elimination, synapses or internal programmed state.
    """
    fitted={}
    for action in (0,1):
        grouped={ctx:result for ctx,arm,result in observations if arm==action}
        if set(grouped)!=set(TRAIN):
            raise ValueError("control did not receive all its public interventions")
        bias=grouped[0]
        bits=sum((grouped[1<<j]^bias)<<j for j in range(4))
        fitted[action]=(bias,bits)
    return lambda context,action: fitted[action][0]^(
        ((context&fitted[action][1]).bit_count())&1)

class AdamMLP:
    """Actually gradient-fit a conventional tanh neural causal classifier.

    No exposed test labels, no scripted law grammar, no pretrained checkpoint.
    Fixed 32 hidden neurons and 2000 full-batch Adam updates, CPU NumPy only.
    """
    def __init__(self,seed):
        r=np.random.default_rng(seed)
        self.w1=r.normal(0,0.23,size=(5,32))
        self.b1=np.zeros((1,32))
        self.w2=r.normal(0,0.23,size=(32,1))
        self.b2=np.zeros((1,1))
        self.fitted=False

    @staticmethod
    def design(inputs):
        return np.array([[((ctx>>j)&1)*2-1 for j in range(4)]+[action*2-1]
                         for ctx,action in inputs],dtype=np.float64)

    def fit(self,observations):
        x=self.design([(ctx,action) for ctx,action,_ in observations])
        y=np.array([[out] for _,_,out in observations],dtype=np.float64)
        params=(self.w1,self.b1,self.w2,self.b2)
        m=[np.zeros_like(p) for p in params]
        v=[np.zeros_like(p) for p in params]
        for step in range(1,2001):
            hidden=np.tanh(x@self.w1+self.b1)
            logits=hidden@self.w2+self.b2
            probability=1.0/(1.0+np.exp(-np.clip(logits,-30,30)))
            dz=(probability-y)/len(observations)
            dw2=hidden.T@dz
            db2=np.sum(dz,axis=0,keepdims=True)
            dh=dz@self.w2.T*(1-hidden*hidden)
            dw1=x.T@dh
            db1=np.sum(dh,axis=0,keepdims=True)
            for i,(p,grad) in enumerate(zip(params,(dw1,db1,dw2,db2))):
                m[i][...]=0.9*m[i]+0.1*grad
                v[i][...]=0.999*v[i]+0.001*grad*grad
                p-=0.035*(m[i]/(1-0.9**step))/(np.sqrt(v[i]/(1-0.999**step))+1e-8)
        self.fitted=True
        final=self.design([(ctx,action) for ctx,action,_ in observations])
        h=np.tanh(final@self.w1+self.b1)
        logits=h@self.w2+self.b2
        pred=(logits.reshape(-1)>=0).astype(np.int64)
        self.training_correct=int((pred==y.reshape(-1)).sum())
        return self

    def predict(self,context,action):
        if not self.fitted:
            raise ValueError("control not fitted")
        x=self.design([(context,action)])
        output=np.tanh(x@self.w1+self.b1)@self.w2+self.b2
        return int(output[0,0]>=0)

def evaluate():
    start=time.perf_counter()
    cpu_start=time.process_time()
    tracemalloc.start()
    try:
        baseline=PublicCausalCells()
        relations=NativeRelationMemory()
        comparators=[]
        all_public=[]
        all_test=set()
        for slot in range(NATIVE):
            retained=slot>=7
            address=slot-7 if retained else slot
            observations=[]
            for context in TRAIN:
                for action in (0,1):
                    value=consequence(slot,context,action)
                    observations.append((context,action,value))
                    baseline.observe(address,action,value,retained=retained)
                    if not relations.observe_public(
                            address,context,action,value,
                            f"NKR02:public:slot{slot}:ctx{context}:arm{action}",
                            retained=retained):
                        raise AssertionError("duplicate first-use public training")
            all_public.append(observations)
            comparators.append((
                independent_symbolic_fit(observations),
                AdamMLP(seed=101+slot).fit(observations)))
        if relations.unique_observations!=160:
            raise AssertionError("public sample accounting")

        original_counter_checkpoint=baseline.snapshot()
        original_relation_checkpoint=relations.checkpoint()
        duplicates=0
        for slot in range(NATIVE):
            retained=slot>=7
            address=slot-7 if retained else slot
            for context,action,value in all_public[slot]:
                if relations.observe_public(address,context,action,value,
                                            f"NKR02:duplicate:slot{slot}",
                                            retained=retained):
                    raise AssertionError("duplicate counted as novel")
                duplicates+=1
        if (relations.checkpoint()!=original_relation_checkpoint
                or baseline.snapshot()!=original_counter_checkpoint):
            raise AssertionError("duplicate alias mutated native knowledge")
        try:
            relations.observe_public(0,0,0,
                1-consequence(0,0,0),"NKR02:invalid:conflict")
        except ValueError:
            pass
        else:
            raise AssertionError("conflicting source accepted")
        if relations.checkpoint()!=original_relation_checkpoint:
            raise AssertionError("conflict mutated original knowledge")

        methods=("incumbent","native","independent_symbolic",
                 "gradient_MLP","evidence_only")
        scores={family:{name:{"success":0,"total":0,
                              "predicted_effect_correct":0,
                              "both_effect_queries":0} for name in methods}
                for family in ("in_family","out_of_family")}
        native_prediction_false_identified={"in_family":0,"out_of_family":0}
        for slot in range(NATIVE):
            retained=slot>=7
            address=slot-7 if retained else slot
            exact,gradient=comparators[slot]
            for context in TEST:
                all_test.add((slot,context))
                old=baseline.choose(address,retained=retained)
                if old not in (0,1):
                    raise AssertionError("incumbent abstained unexpectedly")
                actual_native=baseline.choose_contextual(
                    address,context,relations,retained=retained)
                if actual_native not in (0,1):
                    raise AssertionError("new policy abstained unexpectedly")
                actions={
                    "incumbent":old,
                    "native":actual_native,
                    "independent_symbolic": 0 if exact(context,0)>exact(context,1) else 1,
                    "gradient_MLP":0 if gradient.predict(context,0)>gradient.predict(context,1) else 1,
                    "evidence_only":old, # none of the combined heldout contexts was observed
                }
                for family,quadratic in (("in_family",False),
                                         ("out_of_family",True)):
                    for name,action in actions.items():
                        obj=scores[family][name]
                        obj["total"]+=1
                        obj["success"]+=consequence(slot,context,action,quadratic)
                        if name=="native":
                            for candidate in (0,1):
                                predicted=relations.predict(
                                    address,context,candidate,retained=retained)
                                if predicted is not None:
                                    obj["both_effect_queries"]+=1
                                    correct=int(predicted==consequence(
                                        slot,context,candidate,quadratic))
                                    obj["predicted_effect_correct"]+=correct
                                    native_prediction_false_identified[family]+=(1-correct)
        if len(all_test)!=176:
            raise AssertionError("heldout coverage")
        cold=NativeRelationMemory.restore(original_relation_checkpoint)
        intact=PublicCausalCells.restore(original_counter_checkpoint)
        if cold.checkpoint()!=original_relation_checkpoint or intact.snapshot()!=original_counter_checkpoint:
            raise AssertionError("lost cold knowledge")
        for slot,context in all_test:
            retained=slot>=7
            address=slot-7 if retained else slot
            if baseline.choose_contextual(address,context,relations,retained=retained)!=(
                    intact.choose_contextual(address,context,cold,retained=retained)):
                raise AssertionError("cold decision drift")
        # Learning one new observation in one retained compartment must not
        # rewrite or change other slots' knowledge/decisions.
        before_other={(slot,ctx):cold.predict(slot-7 if slot>=7 else slot,
                                              ctx,0,retained=slot>=7)
                      for slot,ctx in all_test if slot!=15}
        new_context=3
        if not cold.observe_public(8,new_context,0,
                                  consequence(15,new_context,0),
                                  "NKR02:new:retained15",retained=True):
            raise AssertionError("new distinct valid observation not admitted")
        for (slot,ctx),value in before_other.items():
            if cold.predict(slot-7 if slot>=7 else slot,ctx,0,
                            retained=slot>=7)!=value:
                raise AssertionError("interference leaked across native slots")
        if baseline.snapshot()!=original_counter_checkpoint:
            raise AssertionError("legacy YPC1 state mutation")
        if len(original_counter_checkpoint)!=164:
            raise AssertionError("accepted YPC1 checkpoint altered")

        a=scores["in_family"]
        b=scores["out_of_family"]
        success_in=a["native"]["success"]>=168
        incumbent_gain=a["native"]["success"]-a["incumbent"]["success"]>=36
        symbolic_parity=a["native"]["success"]>=a["independent_symbolic"]["success"]-1
        safe_ood=b["native"]["success"]>=168 and b["native"]["success"]>=b["incumbent"]["success"]
        return {
            "schema":"yggdrasil.nkr02.native-causal-transfer-dev.v1",
            "first_prereg_sha":PREREG,
            "source_name":"PUBLIC_NKR02_INDEPENDENT_SOURCE_NOT_PROTECTED_FIRST_USE",
            "total_public_observations":relations.unique_observations,
            "duplicate_aliases_ignored":duplicates,
            "worlds_per_family":NATIVE,
            "heldout_action_choices_per_family":len(all_test),
            "native_unique_programmed_weight_profiles":relations.unique_programmed_profiles,
            "native_relation_checkpoint_bytes":len(original_relation_checkpoint),
            "legacy_checkpoint_bytes":len(original_counter_checkpoint),
            "gradient_mlp_steps_per_slot":2000,
            "gradient_mlp_training_correct":sum(x[1].training_correct for x in comparators),
            "gradient_mlp_training_total":160,
            "scores":scores,
            "native_prediction_false_identified":native_prediction_false_identified,
            "in_family_gate":success_in and incumbent_gain and symbolic_parity,
            "out_of_family_safety_gate":safe_ood,
            "scientific_classification":"MIXED_NO_PROMOTION" if success_in and incumbent_gain and symbolic_parity and not safe_ood
              else "FROZEN_GATES_PASS_DEV_ONLY" if success_in and incumbent_gain and symbolic_parity and safe_ood
              else "NEGATIVE_NO_PROMOTION",
            "source_code_untouched":True,
            "retention_and_no_interference":True,
            "no_main_mutation":True,
            "original_WSP_first_use_replayed":False,
            "cpu_seconds":time.process_time()-cpu_start,
            "wall_seconds":time.perf_counter()-start,
            "peak_tracemalloc_bytes":tracemalloc.get_traced_memory()[1],
            "limitations":"Public deterministic synthetic contextual grammar, no real provider validation, known small four-bit state/action spaces, OOD violates relation grammar by unobserved quadratic interaction. Fully trained MLP fitted without test labels but no architecture-capacity match. No general-language, whole-model advantage or native-knowledge promotion. Tracemalloc overhead precludes inference-speed advantage claims."
        }
    finally:
        tracemalloc.stop()

if __name__=="__main__":
    print("NKR02_INDEPENDENT_DEV="+json.dumps(evaluate(),sort_keys=True,separators=(",",":")),flush=True)

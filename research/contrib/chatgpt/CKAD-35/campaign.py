"""CKAD35: cold native causal memory as a read-only source for analogical transfer.

Only actual witnessed interventions enter NativeContextAccumulator or
NativeCumulativeLearner. Permutations and donor identity are hypotheses, never
authenticated outcomes. The permutation search is an externally supplied
conventional algorithm, not an intrinsic native analogy mechanism.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import itertools
import json
import random
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, coordinates
from yggdrasil.native_property_knowledge import NativePropertyKnowledge

HERE=Path(__file__).resolve().parent
F30=HERE.parent/"CKAD-30"/"campaign.py"
SPEC=importlib.util.spec_from_file_location("ckad35_original_public_compositions",F30)
C30=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C30)

SCHEMA="yggdrasil.ckad35.cold-relational-transfer.v1"
PREREG="fa14893269bb93b2d192ab4134073d5c148898fd"
PILOT=(13851,13852)
PRIMARY=(23851,23852,23853)
GRAPH=("xor3","majority3","gate3")
DONORS=(0,1,2)
TARGETS=(3,4,5,6,7,8)
PRESSURE=(9,10,11,12)
FAMILIES=("isomorphic","quartic_shift")
ARMS=("native_analogy","conventional_analogy","native_target_only",
      "conventional_target_gf2","polynomial_logistic","smoothed_frequency",
      "sham","ungated_native_analogy")
PAIR=tuple(itertools.combinations(range(6),2))
TRIPLE=tuple(itertools.combinations(range(6),3))
QUARTIC=tuple(itertools.combinations(range(6),4))
MONOMIALS=tuple(i for i in range(64) if i.bit_count()<=3)
PERMS=tuple(itertools.permutations(range(5)))
TRANSFORMS=tuple((perm,mask,flip) for perm in PERMS
                 for mask in range(32) for flip in (0,1))


def seed_int(*labels):
    raw=hashlib.sha256(canonical(["ckad35-fresh-public-worlds-v1",*labels])).digest()
    return int.from_bytes(raw[:8],"big")


def donor_law(seed,slot):
    """Private generator only, never passed to native readout/transfer inference."""
    r=random.Random(seed_int("donor-world",seed,slot))
    return (r.randrange(2),r.randrange(64),tuple(r.sample(PAIR,2)),
            tuple(r.sample(TRIPLE,2)))


def binary_effect(law,x):
    intercept,linear,pairs,triples=law
    y=intercept^((linear&x).bit_count()&1)
    for term in (*pairs,*triples):
        y^=int(all((x>>k)&1 for k in term))
    return y


def context_transform(x,perm,mask):
    context=x&31
    output_context=0
    for destination_bit,source_bit in enumerate(perm):
        output_context|=((context>>source_bit)&1)<<destination_bit
    return ((output_context^mask)&31)|(x&32)


def target_law(seed,slot):
    """Evaluator ONLY: donor identity, permutation and OOD never reach the model."""
    if slot not in TARGETS:raise ValueError("CKAD35_PRIVATE_TARGET_SLOT")
    r=random.Random(seed_int("target-world",seed,slot))
    donor=r.choice(DONORS)
    perm=tuple(r.sample(range(5),5))
    mask=r.randrange(32)
    flip=r.randrange(2)
    quartic=(r.choice(QUARTIC) if slot>=6 else None)
    return donor,perm,mask,flip,quartic


def reveal(seed,slot,x):
    if slot not in (*DONORS,*TARGETS,*PRESSURE) or not 0<=x<64:
        raise ValueError("CKAD35_BAD_PUBLIC_INTERVENTION")
    if slot in DONORS:return binary_effect(donor_law(seed,slot),x)
    if slot in PRESSURE:return binary_effect(donor_law(seed,slot+20),x)
    donor,perm,mask,flip,quartic=target_law(seed,slot)
    y=binary_effect(donor_law(seed,donor),context_transform(x,perm,mask))^flip
    if quartic is not None:
        y^=int(all((x>>k)&1 for k in quartic))
    return y


def public_rows(seed,slot,inputs):
    return [[x&31,x>>5,reveal(seed,slot,x)] for x in inputs]


def degree3_feature(x):
    return sum(1<<i for i,t in enumerate(MONOMIALS) if (x&t)==t)


def source_partition(seed):
    """Input-only design; no consequence can influence the split."""
    xs=sorted(range(64),key=lambda x:(seed_int("donor-public-order",seed,x),x))
    pivots={}
    source=[]
    for x in xs:
        v=degree3_feature(x)
        while v:
            k=v.bit_length()-1
            if k not in pivots:
                pivots[k]=v
                source.append(x)
                break
            v^=pivots[k]
        if len(source)==42:break
    if len(source)!=42:
        raise AssertionError("CKAD35_PUBLIC_DONOR_BASIS_NOT_FULL_RANK")
    target=sorted(range(64),key=lambda x:(seed_int("target-input-order",seed,x),x))
    fit,cal,held=target[:10],target[10:16],target[16:32]
    if len(set(fit+cal+held))!=32 or len(held)!=16 or len(set(source))!=42:
        raise AssertionError("CKAD35_SOURCE_HELD_DISJOINT")
    return tuple(source),tuple(fit),tuple(cal),tuple(held)


def fit_independent(rows):
    """Independent conventional GF2 source model (not native code/hidden law)."""
    pivots={}
    seen=set()
    for c,a,y in rows:
        x=c|(a<<5)
        if x in seen or type(y) is not int or y not in (0,1):
            raise ValueError("CKAD35_BAD_CONVENTIONAL_WITNESS")
        seen.add(x)
        v=degree3_feature(x)
        rhs=y
        while v:
            k=v.bit_length()-1
            if k not in pivots:
                pivots[k]=(v,rhs)
                break
            pv,py=pivots[k]
            v^=pv
            rhs^=py
        if not v and rhs:
            raise ValueError("CKAD35_CONVENTIONAL_OUT_OF_CLASS")
    return pivots


def predict_independent(pivots,x):
    v=degree3_feature(x)
    y=0
    while v:
        k=v.bit_length()-1
        if k not in pivots:return .5
        row,rhs=pivots[k]
        v^=row
        y^=rhs
    return float(y)


def native_stage(model,slot,rows,degree):
    a,r=coordinates(slot)
    return model.stage_update(a,rows,digest(canonical(rows)),
                              max_degree=degree,retained=r)


def native_prob(model,slot,x):
    a,r=coordinates(slot)
    p=model.predict(a,x&31,x>>5,retained=r)
    if p is None:return .5
    if type(p) is not int or p not in (0,1):
        raise AssertionError("CKAD35_NATIVE_NONBINARY")
    return float(p)


def compile_source_memory(seed,donor_inputs,fit,cal,held):
    bank=NativeContextAccumulator(5)
    donor_witness={s:public_rows(seed,s,donor_inputs) for s in DONORS}
    for s in DONORS:bank=native_stage(bank,s,donor_witness[s],3)
    original_bytes=bank.checkpoint()
    cold=NativeContextAccumulator.restore(original_bytes,digest(original_bytes))
    donor_tables=[[native_prob(cold,s,x) for x in range(64)] for s in DONORS]
    if any(v not in (0.,1.) for table in donor_tables for v in table):
        raise AssertionError("CKAD35_DONOR_SOURCE_NOT_IDENTIFIED")
    for s in DONORS:
        conventional=fit_independent(donor_witness[s])
        if len(conventional)!=42 or any(
            donor_tables[s][x]!=predict_independent(conventional,x)
            for x in range(64)
        ):raise AssertionError("CKAD35_DONOR_CONVENTIONAL_PARITY")
    fit_witness={s:public_rows(seed,s,fit) for s in TARGETS}
    calibration={s:public_rows(seed,s,cal) for s in TARGETS}
    for s in TARGETS:
        bank=native_stage(bank,s,fit_witness[s]+calibration[s],6)
    original_predict=[[native_prob(bank,s,x) for x in range(64)] for s in (*DONORS,*TARGETS)]
    pressure_witness={s:public_rows(seed,s,donor_inputs) for s in PRESSURE}
    for s in PRESSURE:bank=native_stage(bank,s,pressure_witness[s],3)
    full_checkpoint=bank.checkpoint()
    restored=NativeContextAccumulator.restore(full_checkpoint,digest(full_checkpoint))
    if restored.checkpoint()!=full_checkpoint or any(
        [native_prob(restored,s,x) for x in range(64)]!=original_predict[s]
        for s in (*DONORS,*TARGETS)
    ):raise AssertionError("CKAD35_COLD_OR_PRESSURE_INTERFERENCE")
    for s in (*DONORS,*TARGETS,*PRESSURE):
        a,r=coordinates(s)
        expected=(42 if s in (*DONORS,*PRESSURE) else 16)
        if restored.profile_info(a,retained=r)["source_records"]!=expected:
            raise AssertionError("CKAD35_SOURCE_WITNESS_LOSS")
    conflict=[list(donor_witness[0][0])]
    conflict[0][2]^=1
    protected=restored.checkpoint()
    try:native_stage(restored,0,conflict,3)
    except ValueError:pass
    else:raise AssertionError("CKAD35_CONTRADICTORY_CAUSAL_SOURCE_ACCEPTED")
    if restored.checkpoint()!=protected:
        raise AssertionError("CKAD35_CONTRADICTORY_SOURCE_MUTATED_SIBLINGS")
    return {
        "cold":restored,
        "donor_native_tables":[[native_prob(restored,s,x) for x in range(64)] for s in DONORS],
        "donor_conventional_tables":[[predict_independent(fit_independent(donor_witness[s]),x)
                                       for x in range(64)] for s in DONORS],
        "donor_witness":donor_witness,"fit_witness":fit_witness,
        "calibration":calibration,"pressure_witness":pressure_witness,
        "source_sha256":digest(original_bytes),"cold_sha256":digest(full_checkpoint),
        "cold_bytes":len(full_checkpoint),
        "donor_exact_retention":True,"target_exact_retention":True,
        "cold_bytes_exact":True,"conflict_atomic":True
    }


def native_target_control(seed,fit_witness,calibration,held):
    raw=NativePropertyKnowledge("ckad35",entities=1,context_bits=5).checkpoint()
    learner=NativeCumulativeLearner(raw,digest(raw))
    for slot in TARGETS:
        data=fit_witness[slot]+calibration[slot]
        blob=canonical(data)
        ref=digest(canonical(["ckad35/native-target-actual-witness",seed,slot,digest(blob)]))
        learner=learner.observe(slot,data,digest(blob),source_ref=ref)
    predictions={slot:[.5 if learner.predict(slot,x&31,x>>5) is None
                        else float(learner.predict(slot,x&31,x>>5))
                        for x in held] for slot in TARGETS}
    checkpoint=learner.checkpoint()
    cold=NativeCumulativeLearner.restore(checkpoint,digest(checkpoint))
    if cold.checkpoint()!=checkpoint:raise AssertionError("CKAD35_NATIVE_TARGET_COLD")
    if any(predictions[s]!=[
            (.5 if cold.predict(s,x&31,x>>5) is None
             else float(cold.predict(s,x&31,x>>5))) for x in held]
           for s in TARGETS):
        raise AssertionError("CKAD35_NATIVE_TARGET_COLD_FORECAST")
    return predictions,{"checkpoint_sha256":digest(checkpoint),"cold_exact":True}


def compatible(tables,fit_records,cal_records,held,with_calibration=True):
    """No hidden target rule, donor ID or held outcomes in candidate inference."""
    fit=[(c|(a<<5),y) for c,a,y in fit_records]
    cal=[(c|(a<<5),y) for c,a,y in cal_records]
    def bit(d,perm,mask,flip,x):
        return int(tables[d][context_transform(x,perm,mask)])^flip
    fit_candidates=[]
    for donor in DONORS:
        for perm,mask,flip in TRANSFORMS:
            if all(bit(donor,perm,mask,flip,x)==y for x,y in fit):
                fit_candidates.append((donor,perm,mask,flip))
    admissible=([h for h in fit_candidates
                 if all(bit(*h,x)==y for x,y in cal)]
                if with_calibration else fit_candidates)
    probs=([
        sum(bit(*h,x) for h in admissible)/len(admissible)
        if admissible else .5 for x in held
    ])
    return probs,{"fit_survivors":len(fit_candidates),
                  "calibrated_survivors":len(admissible),
                  "zero_survivor_veto":len(admissible)==0}


def logistic_fit(rows):
    import numpy as np
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.linear_model import LogisticRegression
    x=np.array([[float((c|(a<<5))>>i&1) for i in range(6)] for c,a,y in rows])
    y=np.array([y for c,a,y in rows])
    feat=PolynomialFeatures(degree=3,interaction_only=True,include_bias=False)
    fitx=feat.fit_transform(x)
    if len(set(y))==1:return (None,float(y[0]),feat)
    m=LogisticRegression(C=1.,max_iter=600,solver="lbfgs",random_state=0)
    m.fit(fitx,y)
    return m,None,feat


def logistic_prob(fitted,x):
    m,constant,features=fitted
    if constant is not None:return constant
    import numpy as np
    return float(m.predict_proba(features.transform(
        np.array([[float((x>>i)&1) for i in range(6)]])
    ))[0,1])


def source_frequency(rows,x):
    act=x>>5
    sub=[r[2] for r in rows if r[1]==act]
    return (1+sum(sub))/(2+len(sub))


def score(seed):
    if seed not in PILOT:raise ValueError("CKAD35_FROZEN_PILOT_ONLY")
    t0,c0=time.perf_counter(),time.process_time()
    donor_inputs,fit,cal,held=source_partition(seed)
    mem=compile_source_memory(seed,donor_inputs,fit,cal,held)
    native_only,native_info=native_target_control(seed,mem["fit_witness"],mem["calibration"],held)
    forecasts={}
    evidence={}
    for slot in TARGETS:
        all_rows=mem["fit_witness"][slot]+mem["calibration"][slot]
        nat,counts=compatible(mem["donor_native_tables"],mem["fit_witness"][slot],
                              mem["calibration"][slot],held)
        conv,convc=compatible(mem["donor_conventional_tables"],mem["fit_witness"][slot],
                              mem["calibration"][slot],held)
        if nat!=conv or counts!=convc:
            raise AssertionError("CKAD35_CONVENTIONAL_ANALOGICAL_PARITY")
        ungated,_=compatible(mem["donor_native_tables"],mem["fit_witness"][slot],
                             mem["calibration"][slot],held,with_calibration=False)
        pivots=fit_independent(all_rows)
        lg=logistic_fit(all_rows)
        forecasts[slot]={
            "native_analogy":nat,
            "conventional_analogy":conv,
            "ungated_native_analogy":ungated,
            "native_target_only":native_only[slot],
            "conventional_target_gf2":[predict_independent(pivots,x) for x in held],
            "polynomial_logistic":[logistic_prob(lg,x) for x in held],
            "smoothed_frequency":[source_frequency(all_rows,x) for x in held],
            "sham":[.5]*len(held)
        }
        evidence[str(slot)]=counts
    truth={slot:[reveal(seed,slot,x) for x in held] for slot in TARGETS}
    held_truth={}
    held_forecasts={}
    metrics={}
    committed={}
    incorrect={}
    for family,slots in (("isomorphic",(3,4,5)),("quartic_shift",(6,7,8))):
        held_truth[family]=[[truth[s][i] for s in slots] for i in range(len(held))]
        held_forecasts[family]={arm:[[forecasts[s][arm][i] for s in slots]
                                   for i in range(len(held))] for arm in ARMS}
        metrics[family]={}
        committed[family]={}
        incorrect[family]={}
        for arm in ARMS:
            predictions=held_forecasts[family][arm]
            loss=0.
            for i,values in enumerate(predictions):
                for g in GRAPH:
                    p=C30.composition(g,values)
                    y=C30.composition(g,held_truth[family][i])
                    if not -1e-10<=p<=1+1e-10:
                        raise AssertionError("CKAD35_INVALID_GRAPH_PROBABILITY")
                    loss+=(max(0.,min(1.,p))-y)**2
            confident=0
            wrong=0
            for vals,correct in zip(predictions,held_truth[family]):
                for pred,label in zip(vals,correct):
                    if pred<=.1 or pred>=.9:
                        confident+=1
                        wrong+=int((pred>=.5)!=label)
            metrics[family][arm]={"brier":round(loss/(len(held)*3),10),"cases":48}
            committed[family][arm]=round(confident/(len(held)*3),10)
            incorrect[family][arm]=wrong
    return {
        "seed":seed,"source_outcomes":390,"donor_source_outcomes":126,
        "target_source_outcomes":96,"pressure_source_outcomes":168,
        "held_composites_each_family":48,"donor_public_inputs":list(donor_inputs),
        "target_fit_inputs":list(fit),"target_calibration_inputs":list(cal),
        "target_held_inputs":list(held),
        "donor_source_witness":{str(s):mem["donor_witness"][s] for s in DONORS},
        "target_fit_witness":{str(s):mem["fit_witness"][s] for s in TARGETS},
        "target_calibration_witness":{str(s):mem["calibration"][s] for s in TARGETS},
        "pressure_source_witness":{str(s):mem["pressure_witness"][s] for s in PRESSURE},
        "donor_native_tables":mem["donor_native_tables"],
        "donor_conventional_tables":mem["donor_conventional_tables"],
        "native_custody":{k:mem[k] for k in ("source_sha256","cold_sha256","cold_bytes",
                            "donor_exact_retention","target_exact_retention",
                            "cold_bytes_exact","conflict_atomic")},
        "target_native_custody":native_info,"target_compatible_counts":evidence,
        "held_truth":held_truth,"held_forecasts":held_forecasts,
        "metrics":metrics,"committed_primitive_coverage":committed,
        "confident_primitive_errors":incorrect,
        "cpu_seconds":round(time.process_time()-c0,6),
        "wall_seconds":round(time.perf_counter()-t0,6),"primary_scored":False
    }


def classify(cases):
    if tuple(c["seed"] for c in cases)!=PILOT:
        raise AssertionError("CKAD35_FROZEN_ORDER")
    def qualified(c):
        a=c["metrics"]["isomorphic"]
        o=c["metrics"]["quartic_shift"]
        if not (a["native_analogy"]["brier"]<=.08
                and a["native_analogy"]["brier"]<=a["native_target_only"]["brier"]-.05
                and a["native_analogy"]["brier"]<=a["conventional_target_gf2"]["brier"]-.05
                and abs(a["native_analogy"]["brier"]-a["conventional_analogy"]["brier"])<=1e-10
                and a["native_analogy"]["brier"]<=a["ungated_native_analogy"]["brier"]
                and c["committed_primitive_coverage"]["isomorphic"]["native_analogy"]>=.50
                and c["confident_primitive_errors"]["isomorphic"]["native_analogy"]==0):
            return False
        if not (sum(c["target_compatible_counts"][str(s)]["zero_survivor_veto"]
                    for s in (6,7,8))>=2
                and c["confident_primitive_errors"]["quartic_shift"]["native_analogy"]==0
                and o["native_analogy"]["brier"]<=o["ungated_native_analogy"]["brier"]):
            return False
        return all(c["native_custody"][k] is True
                   for k in ("donor_exact_retention","target_exact_retention",
                              "cold_bytes_exact","conflict_atomic")) and c["target_native_custody"]["cold_exact"]
    good=all(qualified(c) for c in cases)
    return {"decision":"ENGINEERING_FEASIBLE" if good else "SCREEN_NO_GO",
            "engineering_feasible":good,"scientific_pass":False,
            "conventional_superiority":False,"primary_scored":False}


def validate_lock():
    meta=json.loads((HERE/"source_lock.json").read_text())
    raw=Path(__file__).read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if meta["campaign_blob_sha1"]!=sha or meta["prereg_commit"]!=PREREG:
        raise AssertionError("CKAD35_SOURCE_OR_PREREG_DRIFT")
    return meta


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("preflight","pilot"),required=True)
    ap.add_argument("--seed",type=int)
    args=ap.parse_args()
    lock=validate_lock()
    if args.mode=="preflight":
        if args.seed is not None:raise ValueError("CKAD35_PREFLIGHT_NO_SEED")
        assert len(MONOMIALS)==42 and len(TRANSFORMS)==7680
        assert len(PAIR)==15 and len(TRIPLE)==20 and len(QUARTIC)==15
        assert not set(PILOT)&set(PRIMARY)
        print(json.dumps({"schema":SCHEMA,"mode":"preflight","status":"PASS",
                          "lock":lock,"primary_scored":False},sort_keys=True))
    else:
        if args.seed not in PILOT:raise ValueError("CKAD35_UNREGISTERED_PILOT_SEED")
        print(json.dumps({"schema":SCHEMA,"mode":"pilot","seed":args.seed,
                          "lock":lock,"primary_scored":False,
                          "case":score(args.seed)},sort_keys=True,indent=2))


if __name__=="__main__":
    main()

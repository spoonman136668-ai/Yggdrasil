"""CKAD34: learn the smallest consistent native causal class from source actions.

The portfolio {degree 1,2,3} is declared by the experiment, not discovered
open-endedly. Grounding is synthetic source-only, never production authority.
The independent conventional solver sees exactly the same source witnesses.
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

from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, coordinates
from yggdrasil.native_property_knowledge import NativePropertyKnowledge

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/"CKAD-30"/"campaign.py"
SPEC=importlib.util.spec_from_file_location("ckad34_conventional_composition",BASE)
C30=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C30)

SCHEMA="yggdrasil.ckad34.source-class-selection.v1"
PREREG="2bcd8d5927732caa4c71acf361d7f0a9daf54e47"
PILOT=(13741,13742)
PRIMARY=(23741,23742,23743)
FAMILIES=("affine","quadratic","cubic","quartic_ood")
GRAPHS=("xor3","majority3","gate3")
OLD_SLOTS=tuple(range(12))
PRESSURE_SLOTS=tuple(range(12,16))
FITS=42
CAL=6
HELD=16
CONTEXT_BITS=5
N_INPUTS=64
PAIRS=tuple(itertools.combinations(range(6),2))
TRIPLES=tuple(itertools.combinations(range(6),3))
QUARTETS=tuple(itertools.combinations(range(6),4))
ARMS=("compiled_selected","conventional_mdl","conventional_full_degree3",
      "native_unmodified","polynomial_logistic","smoothed_frequency","sham",
      "compiled_ungated")


def seed_int(*items):
    h=hashlib.sha256(canonical(["ckad34-fresh-disjoint-source",*items])).digest()
    return int.from_bytes(h[:8],"big")


def hidden_law(seed,slot):
    """Private to synthetic revealer and evaluator, never passed to fit/readout."""
    r=random.Random(seed_int("hidden-source-generator",seed,slot))
    bias=r.randrange(2)
    linear=r.randrange(64)
    fam=slot//3 if slot<12 else (slot-12)%3
    pair_a,pair_b=r.sample(PAIRS,2)
    triple_a,triple_b=r.sample(TRIPLES,2)
    quart=r.choice(QUARTETS)
    return (bias,linear,(pair_a,pair_b) if fam>=1 else (),
            (triple_a,triple_b) if fam>=2 else (),
            (quart,) if fam>=3 else ())


def effect(law,x):
    bias,linear,pairs,triples,quartets=law
    ans=bias ^ ((linear&x).bit_count()&1)
    for term in (*pairs,*triples,*quartets):
        ans^=int(all((x>>bit)&1 for bit in term))
    return ans


def reveal(seed,slot,x):
    if slot not in (*OLD_SLOTS,*PRESSURE_SLOTS) or not 0<=x<N_INPUTS:
        raise ValueError("CKAD34_REVEAL_INPUT")
    return effect(hidden_law(seed,slot),x)


def monomials(degree):
    if degree not in (1,2,3):
        raise ValueError("CKAD34_UNDECLARED_CLASS")
    return tuple(mask for mask in range(N_INPUTS) if mask.bit_count()<=degree)


def vector(x,degree):
    if type(x) is not int or not 0<=x<N_INPUTS:
        raise ValueError("CKAD34_INPUT")
    return sum(1<<i for i,m in enumerate(monomials(degree)) if x&m==m)


def independent_insert(pivots,row,rhs=0):
    while row:
        high=row.bit_length()-1
        if high not in pivots:
            pivots[high]=(row,rhs)
            return True
        old,y=pivots[high]
        row^=old
        rhs^=y
    if rhs:
        raise ValueError("CKAD34_CONVENTIONAL_CLASS_INADEQUATE")
    return False


def conventional_fit(data,degree):
    pivots={}
    seen=set()
    for context,action,outcome in data:
        x=context|(action<<CONTEXT_BITS)
        if x in seen or type(outcome) is not int or outcome not in (0,1):
            raise ValueError("CKAD34_BAD_PUBLIC_SOURCE")
        seen.add(x)
        independent_insert(pivots,vector(x,degree),outcome)
    return pivots


def conventional_predict(pivots,x,degree):
    row=vector(x,degree)
    rhs=0
    while row:
        high=row.bit_length()-1
        if high not in pivots:return 0.5
        p,y=pivots[high]
        row^=p
        rhs^=y
    return float(rhs)


def source_partition(seed):
    """Full-rank cubic basis chosen from input features WITHOUT consequences."""
    all_inputs=sorted(range(N_INPUTS),key=lambda x:(seed_int("unlabeled",seed,x),x))
    pivots={}
    fit=[]
    for x in all_inputs:
        if independent_insert(pivots,vector(x,3)):
            fit.append(x)
        if len(fit)==FITS:break
    if len(fit)!=FITS or len(pivots)!=FITS:
        raise AssertionError("CKAD34_NO_CUBIC_INPUT_BASIS")
    remaining=sorted((x for x in range(N_INPUTS) if x not in fit),
                     key=lambda x:(seed_int("cal-order",seed,x),x))
    cal=remaining[:CAL]
    held=remaining[CAL:]
    if len(held)!=HELD or len(set(fit+cal+held))!=N_INPUTS:
        raise AssertionError("CKAD34_HELD_LEAK")
    return tuple(fit),tuple(cal),tuple(held)


def public_rows(seed,slot,xs):
    return [[x&31,x>>CONTEXT_BITS,reveal(seed,slot,x)] for x in xs]


def native_stage(model,slot,data,degree):
    address,retained=coordinates(slot)
    return model.stage_update(address,data,digest(canonical(data)),
                              max_degree=degree,retained=retained)


def native_prob(model,slot,x):
    address,retained=coordinates(slot)
    p=model.predict(address,x&31,x>>CONTEXT_BITS,retained=retained)
    if p is None:return 0.5
    if type(p) is not int or p not in (0,1):
        raise AssertionError("CKAD34_BAD_NATIVE_PROB")
    return float(p)


def profile(model,slot):
    address,retained=coordinates(slot)
    return model.profile_info(address,retained=retained)


def choose_degree(data):
    """Only public outcome consistency can select among declared 1/2/3."""
    for d in (1,2,3):
        try:
            conventional_fit(data,d)
        except ValueError as exc:
            if str(exc)!="CKAD34_CONVENTIONAL_CLASS_INADEQUATE":
                raise
            continue
        return d
    raise AssertionError("CKAD34_COMPLETE_FIT_CLASS")


def native_choose(data,slot=0):
    """The NATIVE fitter, not the conventional solver, decides native class."""
    for d in (1,2,3):
        try:
            learned=native_stage(NativeContextAccumulator(CONTEXT_BITS),slot,data,d)
        except ValueError as exc:
            if str(exc)!="CKAD_NATIVE_MODEL_CLASS_INADEQUATE":
                raise
            continue
        return d,learned
    raise AssertionError("CKAD34_NATIVE_COMPLETE_FIT_CLASS")


def native_profile_bytes(acc,slot):
    data=json.loads(acc._model.checkpoint().decode("ascii"))
    return len(canonical(data["profiles"][slot]))


def train_selected(seed,fit,cal):
    source={s:public_rows(seed,s,fit) for s in OLD_SLOTS}
    calibration={s:public_rows(seed,s,cal) for s in OLD_SLOTS}
    candidate=NativeContextAccumulator(CONTEXT_BITS)
    fixed=NativeContextAccumulator(CONTEXT_BITS)
    selection={}
    admitted={}
    selected_sizes={}
    forced_sizes={}
    ranks={}
    for slot in OLD_SLOTS:
        # Refit in isolation to choose class; stage source exactly once into
        # immutable final shared accumulator, never use private law/class label.
        d,_=native_choose(source[slot],slot)
        candidate=native_stage(candidate,slot,source[slot],d)
        fixed=native_stage(fixed,slot,source[slot],3)
        selection[str(slot)]=d
        admitted[str(slot)]=all(native_prob(candidate,slot,c|(a<<5))==float(y)
                                for c,a,y in calibration[slot])
        selected_sizes[str(slot)]=native_profile_bytes(candidate,slot)
        forced_sizes[str(slot)]=native_profile_bytes(fixed,slot)
        ranks[str(slot)]=profile(candidate,slot)["rank"]
        if profile(candidate,slot)["source_records"]!=FITS:
            raise AssertionError("CKAD34_CUSTODY_SOURCE_COUNT")
    pre_sha=digest(candidate.checkpoint())
    frozen=[[native_prob(candidate,s,x) for x in range(N_INPUTS)] for s in OLD_SLOTS]
    # Four disjoint source-only pressure slots, with no reuse of old slot IDs.
    pressure_records={slot:public_rows(seed,slot,fit) for slot in PRESSURE_SLOTS}
    for slot in PRESSURE_SLOTS:
        candidate=native_stage(candidate,slot,pressure_records[slot],3)
    raw=candidate.checkpoint()
    cold=NativeContextAccumulator.restore(raw,digest(raw))
    if raw!=cold.checkpoint():
        raise AssertionError("CKAD34_COLD_BYTES")
    for slot in OLD_SLOTS:
        if [native_prob(cold,slot,x) for x in range(N_INPUTS)]!=frozen[slot]:
            raise AssertionError("CKAD34_PRESSURE_INTERFERENCE")
    for slot in (*OLD_SLOTS,*PRESSURE_SLOTS):
        if profile(cold,slot)["source_records"]!=FITS:
            raise AssertionError("CKAD34_PRESSURE_SOURCE_LEDGER")
    conflict=[list(source[0][0])]
    conflict[0][2]^=1
    old_raw=cold.checkpoint()
    try:
        native_stage(cold,0,conflict,selection["0"])
    except ValueError:
        pass
    else:
        raise AssertionError("CKAD34_CONFLICT_WAS_ADMITTED")
    if cold.checkpoint()!=old_raw:
        raise AssertionError("CKAD34_CONTRADICTION_MUTATED_STATE")
    return cold,fixed,source,calibration,pressure_records,selection,admitted,{
        "profile_selected_bytes":selected_sizes,
        "profile_fixed_degree3_bytes":forced_sizes,
        "ranks":ranks,
        "before_pressure_sha256":pre_sha,
        "after_pressure_sha256":digest(raw),
        "full_checkpoint_bytes":len(raw),
        "cold_exact":True,"retention_all64_exact":True,
        "conflict_atomic":True,"pressure_slots":len(PRESSURE_SLOTS)
    }


def native_baseline(seed,source,cal,held):
    raw=NativePropertyKnowledge("ckad34",entities=1,context_bits=CONTEXT_BITS).checkpoint()
    model=NativeCumulativeLearner(raw,digest(raw))
    for s in OLD_SLOTS:
        packet=source[s]+cal[s]
        blob=canonical(packet)
        ref=digest(canonical(["ckad34/old-native",seed,s,digest(blob)]))
        model=model.observe(s,packet,digest(blob),source_ref=ref)
    predictions={s:[float(model.predict(s,x&31,x>>5)) if model.predict(s,x&31,x>>5) is not None
                    else .5 for x in held] for s in OLD_SLOTS}
    chk=model.checkpoint()
    restored=NativeCumulativeLearner.restore(chk,digest(chk))
    if restored.checkpoint()!=chk:
        raise AssertionError("CKAD34_OLD_NATIVE_COLD")
    return predictions,{"before_sha256":digest(chk),"cold_exact":True}


def logistic_fit(train):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import PolynomialFeatures
    import numpy as np
    feats=PolynomialFeatures(degree=3,interaction_only=True,include_bias=False)
    x=np.asarray([[int(bool((c|(a<<5))&(1<<k))) for k in range(6)] for c,a,y in train],dtype=float)
    y=np.asarray([row[2] for row in train],dtype=int)
    xx=feats.fit_transform(x)
    if len(set(y))<2:
        return (None,int(y[0]),feats)
    model=LogisticRegression(C=1.,max_iter=600,solver="lbfgs",random_state=0)
    model.fit(xx,y)
    return model,None,feats


def logistic_predict(model,x):
    fitted,constant,feats=model
    if constant is not None:return float(constant)
    import numpy as np
    v=np.array([[float(bool(x&(1<<k))) for k in range(6)]])
    return float(fitted.predict_proba(feats.transform(v))[0,1])


def frequency_prob(train,x):
    a=x>>5
    outcomes=[y for c,action,y in train if action==a]
    return (sum(outcomes)+1)/(len(outcomes)+2)


def score(seed):
    if seed not in PILOT:raise ValueError("CKAD34_ONLY_FROZEN_PILOT_FIRST_USE")
    start,cpu=time.perf_counter(),time.process_time()
    fit,cal,held=source_partition(seed)
    compiled,fixed,source,calibration,pressure_records,selected,admitted,custody=train_selected(seed,fit,cal)
    baseline,oldcustody=native_baseline(seed,source,calibration,held)
    conventional={}
    fixed_conv={}
    model_logistic={}
    for s in OLD_SLOTS:
        d=choose_degree(source[s])
        conventional[s]=(d,conventional_fit(source[s],d))
        fixed_conv[s]=conventional_fit(source[s],3)
        model_logistic[s]=logistic_fit(source[s]+calibration[s])
        if selected[str(s)]!=d:
            raise AssertionError("CKAD34_NATIVE_MDL_DEGREE_DISAGREEMENT")
        if admitted[str(s)]!=all(conventional_predict(conventional[s][1],c|(a<<5),d)==float(y)
                                  for c,a,y in calibration[s]):
            raise AssertionError("CKAD34_NATIVE_MDL_CALIBRATION_DISAGREEMENT")
        if any(native_prob(compiled,s,x)!=conventional_predict(conventional[s][1],x,d)
               for x in range(N_INPUTS)):
            raise AssertionError("CKAD34_NUMERIC_PARITY_DRIFT")
    totals={fam:{arm:{"sq":0.,"count":0} for arm in ARMS} for fam in FAMILIES}
    coverage={fam:{arm:0 for arm in ARMS} for fam in FAMILIES}
    wrong={fam:{arm:0 for arm in ARMS} for fam in FAMILIES}
    held_truth={fam:[] for fam in FAMILIES}
    held_forecasts={fam:{name:[] for name in ARMS} for fam in FAMILIES}
    for i,x in enumerate(held):
        for family_index,fam in enumerate(FAMILIES):
            slots=[family_index*3+s for s in range(3)]
            truth=[reveal(seed,s,x) for s in slots] # only post-fit evaluator
            def pred(arm,slot):
                if arm=="compiled_selected":
                    return native_prob(compiled,slot,x) if admitted[str(slot)] else .5
                if arm=="compiled_ungated":return native_prob(compiled,slot,x)
                if arm=="conventional_mdl":
                    d,p=conventional[slot]
                    return conventional_predict(p,x,d) if admitted[str(slot)] else .5
                if arm=="conventional_full_degree3":return conventional_predict(fixed_conv[slot],x,3)
                if arm=="native_unmodified":return baseline[slot][i]
                if arm=="polynomial_logistic":return logistic_predict(model_logistic[slot],x)
                if arm=="smoothed_frequency":return frequency_prob(source[slot]+calibration[slot],x)
                return .5
            forecasts={name:[pred(name,s) for s in slots] for name in ARMS}
            held_truth[fam].append(truth)
            for arm,v in forecasts.items():
                held_forecasts[fam][arm].append(v)
                for p,y in zip(v,truth):
                    if p!=.5:
                        coverage[fam][arm]+=1
                        wrong[fam][arm]+=int(abs(p-y)>=.5)
                for graph in GRAPHS:
                    actual=C30.composition(graph,truth)
                    prob=C30.composition(graph,v)
                    if not 0<=prob<=1:
                        raise AssertionError("CKAD34_COMPOSITION_BOUND")
                    totals[fam][arm]["sq"]+=(prob-actual)**2
                    totals[fam][arm]["count"]+=1
    metrics={fam:{arm:{"brier":round(v["sq"]/v["count"],10),"cases":v["count"]}
                  for arm,v in d.items()} for fam,d in totals.items()}
    return {
        "seed":seed,"public_source_outcomes":744,"old_fit_source_outcomes":504,
        "old_calibration_source_outcomes":72,"pressure_source_outcomes":168,
        "fit_public_inputs":list(fit),"cal_public_inputs":list(cal),"held_inputs":list(held),
        "held_composites_each_family":48,
        "held_truth":held_truth,"held_forecasts":held_forecasts,
        "source_witnesses":{str(s):source[s] for s in OLD_SLOTS},
        "calibration_witnesses":{str(s):calibration[s] for s in OLD_SLOTS},
        "pressure_witnesses":{str(s):pressure_records[s] for s in PRESSURE_SLOTS},
        "selected_degrees":selected,"source_only_admitted":admitted,
        "native_checkpoint":custody,"old_native_checkpoint":oldcustody,
        "metrics":metrics,
        "primitive_coverage":{f:{a:round(n/48,10) for a,n in d.items()} for f,d in coverage.items()},
        "primitive_confident_wrong":wrong,
        "wall_seconds":round(time.perf_counter()-start,6),
        "cpu_seconds":round(time.process_time()-cpu,6),
        "primary_scored":False
    }


def classify(cases):
    if tuple(c["seed"] for c in cases)!=PILOT:
        raise AssertionError("CKAD34_PILOT_ORDER")
    def eligible(c):
        m=c["metrics"]; cov=c["primitive_coverage"]
        d=c["selected_degrees"];adm=c["source_only_admitted"]
        for fam,degree in zip(FAMILIES[:3],(1,2,3)):
            ids=[FAMILIES.index(fam)*3+i for i in range(3)]
            if any(d[str(slot)]!=degree or not adm[str(slot)] for slot in ids):
                return False
            if not (m[fam]["compiled_selected"]["brier"]<=.01
                    and cov[fam]["compiled_selected"]>=.95
                    and m[fam]["compiled_selected"]["brier"]==
                        m[fam]["conventional_mdl"]["brier"]==
                        m[fam]["conventional_full_degree3"]["brier"]):
                return False
        if not any(m[f]["compiled_selected"]["brier"]<=m[f]["native_unmodified"]["brier"]-.10
                   for f in ("quadratic","cubic")):
            return False
        small=list(range(6))
        a=sum(c["native_checkpoint"]["profile_selected_bytes"][str(s)] for s in small)
        b=sum(c["native_checkpoint"]["profile_fixed_degree3_bytes"][str(s)] for s in small)
        if a>0.9*b:return False
        if (sum(not adm[str(s)] for s in (9,10,11))<2
            or c["primitive_confident_wrong"]["quartic_ood"]["compiled_selected"]!=0
            or m["quartic_ood"]["compiled_selected"]["brier"]>
               m["quartic_ood"]["compiled_ungated"]["brier"]):
            return False
        t=c["native_checkpoint"]
        return t["cold_exact"] and t["retention_all64_exact"] and t["conflict_atomic"] and c["old_native_checkpoint"]["cold_exact"]
    good=all(eligible(c) for c in cases)
    return {"decision":"ENGINEERING_FEASIBLE" if good else "SCREEN_NO_GO",
            "engineering_feasible":good,"scientific_pass":False,
            "strongest_conventional_superiority":False,"primary_scored":False}


def source_lock():
    lock=json.loads((HERE/"source_lock.json").read_text())
    data=Path(__file__).read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if lock["campaign_blob_sha1"]!=blob or lock["prereg_commit"]!=PREREG:
        raise AssertionError("CKAD34_SOURCE_HASH_DRIFT")
    return lock


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("preflight","pilot"),required=True)
    p.add_argument("--seed",type=int)
    args=p.parse_args()
    lock=source_lock()
    if args.mode=="preflight":
        if args.seed is not None:raise ValueError("CKAD34_PREFLIGHT_ONLY")
        assert tuple(len(monomials(d)) for d in (1,2,3))==(7,22,42)
        assert len(PAIRS)==15 and len(TRIPLES)==20 and len(QUARTETS)==15
        assert all(C30.composition(g,b) in (0,1)
                   for g in GRAPHS for b in itertools.product((0,1),repeat=3))
        print(json.dumps({"schema":SCHEMA,"mode":"preflight","status":"PASS",
                          "source_lock":lock,"primary_scored":False},sort_keys=True))
    else:
        if args.seed not in PILOT:raise ValueError("CKAD34_PILOT_SEED_DENIED")
        print(json.dumps({"schema":SCHEMA,"mode":"pilot","seed":args.seed,
                          "source_lock":lock,"primary_scored":False,
                          "case":score(args.seed)},sort_keys=True,indent=2))


if __name__=="__main__":
    main()

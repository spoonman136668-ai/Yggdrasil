"""KNOW13: same-address native accumulation of selected factual context.
Development-only, no canonical training. Underlying native and factual modules
are inherited unmodified from their original source SHA."""
from __future__ import annotations
import argparse, hashlib, json, random, time
from pathlib import Path
from fractions import Fraction

SEEDS=(707,808,909)
PREDS=(940,941,942,943)
IMAGE_SHA="6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1"
JOINT_SHA="576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
PREREG="ffc8d9d27b4fe4fd6b9442e76f6364e38c2cb857"
BASE_S=4_205_000_000
BASE_O=4_206_000_000
FIT=32; N=64

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")
def sha(x):
    return hashlib.sha256(x).hexdigest()
def must(ok,tag):
    if not ok: raise ValueError("YGG_KNOW13_"+tag)
def subject(i,p,e):
    must(type(i) is int and 0<=i<3 and type(p) is int and p in (0,1)
         and type(e) is int and 0<=e<N,"SUBJECT")
    return BASE_S+i*1000+p*100+e
def obj(p,f,b):
    must(type(p) is int and p in (0,1) and type(f) is int and 0<=f<4
         and type(b) is int and b in (0,1),"OBJECT")
    return BASE_O+p*100+f*10+b
def world(i,p):
    """Evaluator-private role; the selector never receives it."""
    seed=SEEDS[i]
    truth=[]
    for split in (0,1):
        vals=[0]*16+[1]*16
        random.Random(seed*10000+p*100+split+31).shuffle(vals)
        truth+=vals
    truth=tuple(truth)
    private=(i+p+2)%4
    cols=[]
    for f in range(4):
        if f==private:
            cols.append(truth)
            continue
        data=[None]*N
        for split in (0,1):
            for mode in (0,1):
                where=[e for e in range(split*FIT,(split+1)*FIT) if truth[e]==mode]
                must(len(where)==16,"MODE_BALANCE")
                vals=[0]*8+[1]*8
                random.Random(seed*100000+p*10000+f*100+split*10+mode+31).shuffle(vals)
                for e,b in zip(where,vals,strict=True):
                    data[e]=b
        cols.append(tuple(data))
    return private,truth,tuple(cols)
def reward(p,mode,action):
    must(all(type(x) is int and x in (0,1) for x in (p,mode,action)),"REWARD")
    return int(action==mode) if p==0 else int(action!=mode)
def bundle(i,p):
    from yggdrasil.native_cumulative_facts import BUNDLE_SCHEMA
    _role,truth,cols=world(i,p)
    rows=[[subject(i,p,e),PREDS[f],obj(p,f,cols[f][e]),
           f"know13:s{SEEDS[i]}:p{p}:e{e:03d}:f{f}"]
          for e in range(N) for f in range(4)]
    return canonical({"schema":BUNDLE_SCHEMA,
        "source_id":f"know13-synthetic-{SEEDS[i]}-p{p}",
        "source_kind":"direct_public_observation",
        "source_mode":"engineering_fixture_only",
        "records":sorted(rows,key=lambda r:r[3])})
def bit(facts,q,p,f):
    answers=[facts.fact(q,PREDS[f],obj(p,f,x)) for x in (0,1)]
    present=[
        v.get("classification")=="DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
        and v.get("source_mode")=="engineering_fixture_only"
        and v.get("source_provenance")=="SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED"
        and v.get("witnessed") is True
        and v.get("native_accepted") is False
        and v.get("verified_new_real_knowledge") is False
        and v.get("can_write_causal_consequence") is False
        for v in answers]
    return present.index(True) if present.count(True)==1 else None
def fit_events(i,p):
    _role,truth,_cols=world(i,p)
    return [(subject(i,p,e),a,reward(p,truth[e],a))
            for e in range(FIT) for a in (0,1)]
def rows_for(facts,events,p,f):
    rows=[]
    for q,act,outcome in events:
        v=bit(facts,q,p,f)
        if v is None: return None
        rows.append([v,act,outcome])
    return rows
def select_role(facts,events,p,fitter):
    """Four-way witness-based search with abstention on ties/missing sources."""
    good=[]
    for f in range(4):
        data=rows_for(facts,events,p,f)
        if data is None:continue
        try:
            candidate=fitter(context_bits=1).stage_fit(
                0,data,sha(canonical(data)),max_degree=1)
        except ValueError as err:
            if any(s in str(err) for s in
                   ("STOCHASTIC_OR_CONFLICTING_INPUT_MODEL_INADEQUATE",
                    "MODEL_CLASS_INADEQUATE","INCONSISTENT_CAUSAL_EVIDENCE")):
                continue
            raise
        if all(candidate.predict(0,v,a)==out for v,a,out in data):
            good.append(f)
    return good[0] if len(good)==1 else None
def shared_rows(facts,events,p,role):
    data=rows_for(facts,events,p,role)
    must(data is not None and len(data)==64,"WITNESSED_ROWS")
    return [[v|(p<<1),a,out] for v,a,out in data]
def symbolic(rows):
    groups={}
    for c,a,y in rows:groups.setdefault((c,a),[]).append(y)
    return {k:Fraction(sum(v),len(v)) for k,v in groups.items()}
def conventional(rows):
    """Independently fully fitted depth-3 complete binary tree leaf estimator."""
    leaves={}
    for c in range(4):
        for a in (0,1):
            data=[y for context,act,y in rows if (context,act)==(c,a)]
            must(bool(data),"TREE_COVERAGE")
            leaves[(c,a)]=Fraction(sum(data),len(data))
    return lambda c,a:leaves[(c,a)]
def evaluate(facts,i,p,f,predictors):
    _,truth,_=world(i,p)
    loss={key:Fraction(0) for key in predictors}
    covered={key:0 for key in predictors}
    total_reward={key:0 for key in predictors}
    h=hashlib.sha256()
    for e in range(FIT,N):
        v=bit(facts,subject(i,p,e),p,f)
        must(v in (0,1),"HELD_PUBLIC_FACT")
        context=v|(p<<1)
        preds={}
        for a in (0,1):
            actual=reward(p,truth[e],a)
            one={}
            for name,fn in predictors.items():
                raw=fn(context,a)
                prob=Fraction(1,2) if raw is None else Fraction(raw)
                must(0<=prob<=1,"PROBABILITY")
                covered[name]+=int(raw is not None)
                loss[name]+=(prob-actual)**2
                one[name]=prob
                if name=="native":
                    h.update(canonical([i,p,e,v,a,prob.numerator,prob.denominator])+b"\n")
            preds[a]=one
        for name in predictors:
            a=int(preds[1][name]>preds[0][name])
            total_reward[name]+=reward(p,truth[e],a)
    return {"held":64,"brier":{k:[(s/64).numerator,(s/64).denominator] for k,s in loss.items()},
            "covered":covered,"rewards":total_reward,"native_fingerprint":h.hexdigest()}

def prove(session,joint_file):
    from yggdrasil.native_context_basis import NativeContextBasis
    from yggdrasil.native_context_accumulator import NativeContextAccumulator
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_knowledge_activation import (
        PINN_ROWS,PINN_PACKED_SHA,open_installed_session)
    t=time.monotonic()
    protocol=json.loads(Path(__file__).with_name("know13_protocol.json").read_bytes())
    must(protocol["schema"]=="yggdrasil.know13.same-address-cumulative-blind-role-development.v1"
         and protocol["frozen_seeds"]==list(SEEDS),"PREREG")
    raw=Path(joint_file).read_bytes()
    must(sha(raw)==JOINT_SHA,"ARCHIVED_AMALGAM")
    results=[]; selected=0; changes=0; max_size=0
    with open_installed_session(session) as history:
        must(len(history._weights)==PINNED_ROWS==21_343_681
             and PINNED_PACKED_SHA==IMAGE_SHA,"HISTORICAL_SOURCE")
        first,last=tuple(history._weights.row_at(0)),tuple(history._weights.row_at(21_343_681-1))
        original=CumulativeNativeFacts(history)
        facts=original
        for i,seed in enumerate(SEEDS):
            native=NativeContextAccumulator(context_bits=2)
            phase_rows=[]; roles=[]; initial_a=None
            for phase in (0,1):
                data=bundle(i,phase)
                facts,receipt=facts.stage(data,sha(data))
                must(receipt["new_unique_facts"]==256,"FACT_BUNDLE")
                events=fit_events(i,phase)
                role=select_role(facts,events,phase,NativeContextBasis)
                must(role is not None and role==world(i,phase)[0],"SELECTOR")
                roles.append(role);selected+=1
                rows=shared_rows(facts,events,phase,role)
                phase_rows.append(rows)
                before=native
                native=native.stage_update(0,rows,sha(canonical(rows)),max_degree=1)
                must(before is not native
                     and native.profile_info(0)["batches"]==phase+1,
                     "SHARED_SLOT_BATCH")
                if phase==0:
                    initial_a=evaluate(facts,i,0,role,{
                        "native":lambda ctx,a:native.predict(0,ctx,a)})
                    must(initial_a["brier"]["native"]==[0,1],"A_HELD_ACQUISITION")
                else:
                    return_a=evaluate(facts,i,0,roles[0],{
                        "native":lambda ctx,a:native.predict(0,ctx,a)})
                    changes+=int(return_a["native_fingerprint"]!=initial_a["native_fingerprint"])
                    must(return_a["native_fingerprint"]==initial_a["native_fingerprint"],
                         "SAME_SLOT_A_RETURN")
                state=native.checkpoint()
                max_size=max(max_size,len(state))
                native=NativeContextAccumulator.restore(state,sha(state))
                must(native.checkpoint()==state,"COLD_ACCUMULATOR")
            all_rows=phase_rows[0]+phase_rows[1]
            fitted=NativeContextBasis(context_bits=2).stage_fit(
                0,all_rows,sha(canonical(all_rows)),max_degree=1)
            replacement=NativeContextBasis(context_bits=2).stage_fit(
                0,phase_rows[1],sha(canonical(phase_rows[1])),max_degree=1)
            table=symbolic(all_rows)
            must(len(table)==8,"CONTROL_FULL_SUPPORT")
            tree=conventional(all_rows)
            measures=[]
            for phase in (0,1):
                mean_action={a:Fraction(sum(y for c,act,y in phase_rows[phase]
                                            if act==a),32)
                             for a in (0,1)}
                arms={
                    "native":lambda c,a:native.predict(0,c,a),
                    "native_full_refit":lambda c,a:fitted.predict(0,c,a),
                    "symbolic":lambda c,a:table[(c,a)],
                    "tree":tree,
                    "replacement_only":lambda c,a:replacement.predict(0,c,a),
                    "action_only":lambda c,a:mean_action[a],
                    "facts_only":lambda c,a:Fraction(1,2)}
                result=evaluate(facts,i,phase,roles[phase],arms)
                must(result["held"]==64 and all(
                    result["brier"][name]==[0,1] for name in
                    ("native","native_full_refit","symbolic","tree")),
                    "STRONG_BASELINE_TIE")
                if phase==0:
                    must(result["native_fingerprint"]==initial_a["native_fingerprint"],
                         "COLD_A_RETURN")
                measures.append(result)
            results.append({"seed":seed,"role_predicates":[PREDS[x] for x in roles],
                            "phases":measures,
                            "accumulator_checkpoint_sha256":sha(native.checkpoint())})
        stored=facts.checkpoint()
        after=CumulativeNativeFacts(history,stored,checkpoint_sha256=facts.checkpoint_sha256)
        must(after.checkpoint()==stored and original.checkpoint()==CumulativeNativeFacts(history).checkpoint(),
             "FACTUAL_COLD_IDENTITY")
        for i in range(3):
            for p in (0,1):
                _role,_truth,cols=world(i,p)
                for e in range(N):
                    for f in range(4):
                        must(bit(after,subject(i,p,e),p,f)==cols[f][e],
                             "FROZEN_FACTUAL_RECALL")
        must(history.fact(*first)["witnessed"] and history.fact(*last)["witnessed"]
             and sha(Path(joint_file).read_bytes())==JOINT_SHA,
             "HISTORICAL_SOURCE_CHANGED")
    allarms=("native","native_full_refit","symbolic","tree","replacement_only",
             "action_only","facts_only")
    cumulative={k:Fraction(0) for k in allarms}
    covered={k:0 for k in allarms}
    earned={k:0 for k in allarms}
    for seed in results:
        for stage in seed["phases"]:
            for k in allarms:
                numerator,denominator=stage["brier"][k]
                cumulative[k]+=Fraction(numerator,denominator)*64
                covered[k]+=stage["covered"][k]
                earned[k]+=stage["rewards"][k]
    brier={k:[(x/384).numerator,(x/384).denominator] for k,x in cumulative.items()}
    must(selected==6 and changes==0 and all(brier[x]==[0,1] for x in
         ("native","native_full_refit","symbolic","tree")),"FROZEN_COMPARISON")
    return {"schema":"yggdrasil.know13.shared-native-slot-dev.v1",
            "classification":"SOURCE_FREE_SYNTHETIC_DEVELOPMENT",
            "prereg_sha":PREREG,"seeds":list(SEEDS),
            "roles_selected":selected,"candidate_qpq_facts":1536,
            "witnessed_fit_action_outcomes":384,"held_action_forecasts":384,
            "native_slots_used":1,"old_A_readout_changes":changes,
            "native_cold_restored":True,"factual_cold_restored":True,
            "historical_train_rows":21_343_681,
            "historical_image_sha256":IMAGE_SHA,
            "original_amalgam_joint_sha256":JOINT_SHA,
            "held_brier":brier,"held_reward":earned,
            "held_coverage":covered,"max_native_bytes":max_size,
            "scientific_decision":"DEV_NO_GO_STRONGEST_CONTROL_TIE",
            "scientific_pass":False,"protected_first_use":False,
            "owner_checkpoint":"UNVERIFIED","deployment":"NONE",
            "elapsed_seconds":round(time.monotonic()-t,6)}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--installed-session",required=True,type=Path)
    parser.add_argument("--joint-checkpoint",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    result=prove(args.installed_session,args.joint_checkpoint)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("YGG_KNOW13_DEV="+json.dumps({
        "roles":result["roles_selected"],"Brier":result["held_brier"]["native"],
        "old_A_changes":result["old_A_readout_changes"],
        "scientific":result["scientific_decision"]},sort_keys=True))
if __name__=="__main__":main()

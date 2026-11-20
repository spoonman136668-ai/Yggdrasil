"""KNOW14 — source-visible causal regime discovery, no supplied phase bit.

Isolated source-free synthetic development. Candidate factual properties provide
numeric public observations; separately witnessed FIT actions provide outcomes.
Four hypothesis accumulators test source properties in one native address each.
No owner model, real first-use, source fact promotion or Amalgam trainer.
"""
from __future__ import annotations
import argparse,hashlib,json,random,time
from fractions import Fraction
from pathlib import Path

SEEDS=(1111,2222,3333)
MODE_P=960
CUES=(961,962,963,964)
SB=4_207_000_000
OB=4_208_000_000
FIT=32
N=64
IMAGE_SHA="6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1"
JOINT_SHA="576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
PREREG="045048c2869a41817d16deddc1ebc49cb444b245"

def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("ascii")
def digest(v):
    return hashlib.sha256(v).hexdigest()
def require(ok,why):
    if not ok:raise ValueError("YGG_KNOW14_"+why)
def subject(i,task,e):
    require(type(i) is int and 0<=i<3 and
            type(task) is int and task in (0,1) and
            type(e) is int and 0<=e<N,"SUBJECT")
    return SB+i*1000+task*100+e
def object_id(task,feature,bit):
    require(type(task) is int and task in (0,1) and
            type(feature) is int and 0<=feature<=4 and
            type(bit) is int and bit in (0,1),"OBJECT")
    return OB+task*100+feature*10+bit
def world(i,task):
    """Private evaluator role never supplied to hypothesis evaluation."""
    require(type(i) is int and 0<=i<3 and
            type(task) is int and task in (0,1),"WORLD_DOMAIN")
    seed=SEEDS[i]
    mode=[]
    for split in (0,1):
        block=[0]*16+[1]*16
        random.Random(seed*10000+task*100+split+83).shuffle(block)
        mode.extend(block)
    mode=tuple(mode)
    private=(i+1)%4
    cols=[]
    for feature in range(4):
        if feature==private:
            cols.append((task,)*N)
            continue
        values=[None]*N
        for split in (0,1):
            for m in (0,1):
                locations=[e for e in range(split*FIT,(split+1)*FIT)
                           if mode[e]==m]
                require(len(locations)==16,"FIT_MODE_BALANCE")
                vals=[0]*8+[1]*8
                random.Random(seed*100000+task*10000+
                              feature*100+split*10+m+83).shuffle(vals)
                for e,v in zip(locations,vals,strict=True):values[e]=v
        require(all(type(x) is int for x in values),"NUISANCE_GENERATION")
        cols.append(tuple(values))
    return private,mode,tuple(cols)

def expected(task,mode,action):
    require(all(type(v) is int and v in (0,1)
                for v in (task,mode,action)),"OUTCOME_DOMAIN")
    return int(action==mode) if task==0 else int(action!=mode)

def bundle(i,task):
    from yggdrasil.native_cumulative_facts import BUNDLE_SCHEMA
    _,modes,cols=world(i,task)
    rows=[]
    for e in range(N):
        q=subject(i,task,e)
        rows.append([q,MODE_P,object_id(task,4,modes[e]),
                     f"know14:s{SEEDS[i]}:t{task}:e{e:03d}:mode"])
        for c in range(4):
            rows.append([q,CUES[c],object_id(task,c,cols[c][e]),
                         f"know14:s{SEEDS[i]}:t{task}:e{e:03d}:cue{c}"])
    require(len(rows)==320,"BUNDLE_ROWS")
    return canonical({"schema":BUNDLE_SCHEMA,
        "source_id":f"know14-synthetic-{SEEDS[i]}-t{task}",
        "source_kind":"direct_public_observation",
        "source_mode":"engineering_fixture_only",
        "records":sorted(rows,key=lambda v:v[3])})

def fact_bit(facts,q,predicate,task,feature):
    """Read exact original source typed direct facts; no two-hop hypotheses."""
    observations=[facts.fact(q,predicate,object_id(task,feature,b))
                  for b in (0,1)]
    bits=[o.get("classification")=="DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
          and o.get("witnessed") is True
          and o.get("source_mode")=="engineering_fixture_only"
          and o.get("source_provenance")=="SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED"
          and o.get("native_accepted") is False
          and o.get("verified_new_real_knowledge") is False
          and o.get("can_write_causal_consequence") is False
          for o in observations]
    return bits.index(True) if bits.count(True)==1 else None

def training_events(i,task):
    _,modes,_=world(i,task)
    return [(subject(i,task,e),a,expected(task,modes[e],a))
            for e in range(FIT) for a in (0,1)]

def rows_for(facts,events,task,candidate):
    rows=[]
    for q,action,outcome in events:
        m=fact_bit(facts,q,MODE_P,task,4)
        cue=fact_bit(facts,q,CUES[candidate],task,candidate)
        if m is None or cue is None:return None
        rows.append([m|(cue<<1),action,outcome])
    return rows

def detect(facts, a_events, b_events, native_type):
    """Portfolio of *ephemeral* native hypotheses, no private role oracle.

    Every arm is an isolated hypothesis instance; all updates target the SAME
    native address 0 within that arm. A's raw witness rows are not replayed
    when the B update stages retained native sufficient constraints.
    """
    surviving=[]
    aborted=[]
    for cue in range(4):
        rows_a=rows_for(facts,a_events,0,cue)
        rows_b=rows_for(facts,b_events,1,cue)
        if rows_a is None or rows_b is None:
            aborted.append([cue,"SOURCE_FACT_ABSTAIN"])
            continue
        try:
            a_native=native_type(context_bits=2).stage_update(
                0,rows_a,digest(canonical(rows_a)),max_degree=1)
            b_native=a_native.stage_update(
                0,rows_b,digest(canonical(rows_b)),max_degree=1)
        except ValueError as err:
            if any(x in str(err) for x in (
                "CUMULATIVE_MODEL_INADEQUATE",
                "MODEL_CLASS_INADEQUATE",
                "STOCHASTIC_OR_CONFLICTING_INPUT_MODEL_INADEQUATE")):
                aborted.append([cue,"INCONSISTENT_WITH_WITNESSED_ACTIONS"])
                continue
            raise
        surviving.append((cue,a_native,b_native,rows_a,rows_b))
    # Abstain if the facts do not uniquely explain the intervention contrast.
    return surviving,aborted

def controls(rows):
    groups={}
    for ctx,action,outcome in rows:
        groups.setdefault((ctx,action),[]).append(outcome)
    return {key:Fraction(sum(vals),len(vals)) for key,vals in groups.items()}

def score(facts,i,task,cue,arms):
    _private,modes,_cols=world(i,task)
    totals={name:Fraction(0) for name in arms}
    covered={name:0 for name in arms}
    rewards={name:0 for name in arms}
    native_hash=hashlib.sha256()
    for e in range(FIT,N):
        q=subject(i,task,e)
        mode=fact_bit(facts,q,MODE_P,task,4)
        visible=fact_bit(facts,q,CUES[cue],task,cue)
        require(mode in (0,1) and visible in (0,1),"HELD_FACT_SOURCE")
        context=mode|(visible<<1)
        vals={}
        for action in (0,1):
            outcome=expected(task,modes[e],action)
            preds={}
            for name,predictor in arms.items():
                raw=predictor(context,action)
                if raw is None:
                    prediction=Fraction(1,2)
                else:
                    require(type(raw) in (Fraction,int) and
                            not isinstance(raw,bool) and
                            0<=raw<=1,"FORECAST_CONTRACT")
                    prediction=Fraction(raw)
                    covered[name]+=1
                totals[name]+=(prediction-outcome)**2
                preds[name]=prediction
                if name=="native":
                    native_hash.update(canonical([i,task,e,mode,visible,action,
                                                  prediction.numerator,prediction.denominator])+b"\n")
            vals[action]=preds
        for name in arms:
            action=int(vals[1][name]>vals[0][name])
            rewards[name]+=expected(task,modes[e],action)
    return {"held_predictions":64,
            "brier":{k:[(v/64).numerator,(v/64).denominator]
                     for k,v in totals.items()},
            "forecast_support":covered,"correct_action_rewards":rewards,
            "native_fingerprint":native_hash.hexdigest()}

def prove(source_session, archived_joint):
    from yggdrasil.native_context_basis import NativeContextBasis
    from yggdrasil.native_context_accumulator import NativeContextAccumulator
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_knowledge_activation import (
        PINNED_ROWS,PINNED_PACKED_SHA,open_installed_session)
    started=time.monotonic()
    plan=json.loads(Path(__file__).with_name("know14_protocol.json").read_bytes())
    require(plan["schema"]=="yggdrasil.know14.blind-regime-cue-cumulative-learning-dev-protocol.v1"
            and plan["frozen_seeds"]==list(SEEDS) and
            plan["hypotheses"]["count"]==4,"PREREG_DRIFT")
    joint=Path(archived_joint).read_bytes()
    require(digest(joint)==JOINT_SHA,"ARCHIVED_JOINT_CHANGED")
    results=[]; selected=0; held=0; witnessed=0; old_changes=0; dropped=0; max_bytes=0
    with open_installed_session(source_session) as history:
        require(len(history._weights)==PINNED_ROWS==21_343_681
                and PINNED_PACKED_SHA==IMAGE_SHA,"HISTORICAL_IMAGE")
        first,last=(tuple(history._weights.row_at(k))
                    for k in (0,PINNED_ROWS-1))
        initial=CumulativeNativeFacts(history);facts=initial
        initial_bytes=initial.checkpoint()
        for i,seed in enumerate(SEEDS):
            for task in (0,1):
                blob=bundle(i,task)
                facts,receipt=facts.stage(blob,digest(blob))
                require(receipt["new_unique_facts"]==320,"NEW_SOURCE_FACTS")
            a_events=training_events(i,0);b_events=training_events(i,1)
            witnessed+=len(a_events)+len(b_events)
            winners,rejected=detect(facts,a_events,b_events,NativeContextAccumulator)
            require(len(winners)==1 and len(rejected)==3,"UNIQUE_REGIME_CUE")
            dropped+=len(rejected)
            cue,before,after,ra,rb=winners[0]
            private,_truth,_cols=world(i,0)
            require(cue==private,"WRONG_REGIME_SELECTION")
            selected+=1
            # Prior A state scored from only A intervention training.
            old=score(facts,i,0,cue,{"native":lambda c,a:before.predict(0,c,a)})
            now=score(facts,i,0,cue,{"native":lambda c,a:after.predict(0,c,a)})
            require(old["native_fingerprint"]==now["native_fingerprint"]
                    and old["brier"]["native"]==[0,1],"SAME_ADDRESS_FORGETTING")
            old_changes+=int(old["native_fingerprint"]!=now["native_fingerprint"])
            raw=after.checkpoint()
            max_bytes=max(max_bytes,len(raw))
            cold=NativeContextAccumulator.restore(raw,digest(raw))
            require(cold.checkpoint()==raw,"NATIVE_COLD_BYTES")
            all_training=ra+rb
            symbolic=controls(all_training)
            require(len(symbolic)==8,"STRONG_CONTROLS_NOT_FULL")
            full_refit=NativeContextBasis(context_bits=2).stage_fit(
                0,all_training,digest(canonical(all_training)),max_degree=1)
            # Fully fitted conventional binary tree over all 3 input bits.
            tree=dict(symbolic)  # independent model class: complete 8-leaf tree
            counts={}
            for ctx,act,y in all_training:
                counts.setdefault((ctx&1,ctx>>1,act),[]).append(y)
            tree={k:Fraction(sum(v),len(v)) for k,v in counts.items()}
            mode_only={}
            for ctx,a,y in all_training:
                mode_only.setdefault((ctx&1,a),[]).append(y)
            mode_only={k:Fraction(sum(v),len(v)) for k,v in mode_only.items()}
            stages=[]
            for task in (0,1):
                predictors={
                    "native":lambda c,a:cold.predict(0,c,a),
                    "full_native_refit":lambda c,a:full_refit.predict(0,c,a),
                    "exact_symbolic":lambda c,a:symbolic.get((c,a)),
                    "fully_fitted_tree":lambda c,a:tree.get((c&1,c>>1,a)),
                    "mode_only":lambda c,a:mode_only.get((c&1,a)),
                    "facts_only":lambda c,a:Fraction(1,2)}
                metrics=score(facts,i,task,cue,predictors)
                require(all(metrics["brier"][arm]==[0,1] for arm in (
                    "native","full_native_refit","exact_symbolic","fully_fitted_tree")),
                    "STRONG_CONTROL_TIE")
                held+=metrics["held_predictions"]
                if task==0:
                    require(metrics["native_fingerprint"]==
                            old["native_fingerprint"],"COLD_OLD_A_DRIFT")
                stages.append(metrics)
            results.append({"seed":seed,
                "selected_cue_predicate":CUES[cue],
                "rejected_cue_count":len(rejected),
                "results":stages,
                "native_candidate_sha256":digest(cold.checkpoint()),
                "same_native_address":0})
        frozen=facts.checkpoint()
        restored=CumulativeNativeFacts(history,frozen,
                                       checkpoint_sha256=facts.checkpoint_sha256)
        require(restored.checkpoint()==frozen and
                initial.checkpoint()==initial_bytes,"FACT_COLD")
        for i in range(3):
            for task in (0,1):
                _,modes,cols=world(i,task)
                for e in range(N):
                    q=subject(i,task,e)
                    require(fact_bit(restored,q,MODE_P,task,4)==modes[e],
                            "MODE_FACT_LOST")
                    for cue in range(4):
                        require(fact_bit(restored,q,CUES[cue],task,cue)==cols[cue][e],
                                "REGIME_SOURCE_FACT_LOST")
        require(history.fact(*first)["witnessed"] and
                history.fact(*last)["witnessed"] and
                digest(Path(archived_joint).read_bytes())==JOINT_SHA,
                "ARCHIVED_SOURCE_MUTATION")
    arms=("native","full_native_refit","exact_symbolic",
          "fully_fitted_tree","mode_only","facts_only")
    total={k:Fraction(0) for k in arms}
    earned={k:0 for k in arms}
    support={k:0 for k in arms}
    for seed in results:
        for stage in seed["results"]:
            for arm in arms:
                numerator,denominator=stage["brier"][arm]
                total[arm]+=Fraction(numerator,denominator)*64
                earned[arm]+=stage["correct_action_rewards"][arm]
                support[arm]+=stage["forecast_support"][arm]
    means={k:[(s/384).numerator,(s/384).denominator]
           for k,s in total.items()}
    require(selected==3 and dropped==9 and
            witnessed==384 and held==384 and old_changes==0
            and all(means[x]==[0,1] for x in (
                "native","full_native_refit","exact_symbolic","fully_fitted_tree")),
            "FROZEN_TRIAL_MEASURES")
    return {"schema":"yggdrasil.know14.blind-regime-cue-dev-result.v1",
            "classification":"SOURCE_FREE_SYNTHETIC_DEV_ONLY",
            "prereg_sha":PREREG,"seed_ids":list(SEEDS),
            "hypothesis_cues_per_seed":4,
            "unique_cues_selected":selected,
            "contradictory_cue_hypotheses_rejected":dropped,
            "staged_synthetic_facts":1920,
            "separately_witnessed_fit_actions":witnessed,
            "held_action_forecasts":held,
            "old_A_native_readout_changes":old_changes,
            "same_native_address":0,
            "factual_checkpoint_cold_restored":True,
            "native_checkpoint_cold_restored":True,
            "max_native_checkpoint_bytes":max_bytes,
            "held_mean_brier":means,
            "held_correct_action_rewards":earned,
            "held_forecast_support":support,
            "original_historical_train_rows":21_343_681,
            "historical_image_sha256":IMAGE_SHA,"amalgam_joint_sha256":JOINT_SHA,
            "scientific_decision":"DEV_NO_GO_STRONGEST_CONTROL_TIE",
            "scientific_pass":False,"canonical_training":False,
            "protected_first_use":False,"deployment":"NONE",
            "wall_seconds_excluding_fetch":round(time.monotonic()-started,6)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--installed-session",type=Path,required=True)
    p.add_argument("--joint-checkpoint",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    receipt=prove(args.installed_session,args.joint_checkpoint)
    args.output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print("KNOW14_FROZEN_BLIND_CUE="+json.dumps({
        "selected":receipt["unique_cues_selected"],
        "retained_A":receipt["old_A_native_readout_changes"]==0,
        "native_brier":receipt["held_mean_brier"]["native"],
        "scientific_decision":receipt["scientific_decision"]
    },sort_keys=True))
if __name__=="__main__":main()

"""KNOW18: learn action-query utility from four RAW factual bits, without
passing a precomputed 'balanced candidate partition' input to native learning.

Research-only fixture: training utility requires actual synthetic actions in
FOUR separately instantiated counterfactual worlds for each source query.
Candidate-set filtering after held witnesses remains an analytic assumption.
No existing accepted model, trained Amalgam head or history is modified.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import time

TRAIN = (2111, 2221)
HELD_SEEDS = (2333, 2441, 2551)
SEEDS = TRAIN + HELD_SEEDS
ROLES = (0,1,2,3)
PREDICATES = (981,982,983,984)
PROBE = tuple(range(16))
COMMON = (16,17)
HELD = tuple(range(18,34))
BASE_SUBJECT = 4_260_000_000
BASE_OBJECT = 4_275_000_000
PREREG = "879742c75d7857083f315a07cd58ea3d069f9141"
JOINT_SHA = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
IMAGE_SHA = "6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("ascii")
def digest(raw):
    return hashlib.sha256(raw).hexdigest()
def require(cond,tag):
    if not cond:raise ValueError("YGG_KNOW18_"+tag)
def subject(seed,e):
    require(type(seed) is int and seed in SEEDS
            and type(e) is int and 0<=e<34,"SUBJECT")
    raw=f"know18:subject-opaque:v1:{seed}:{e}".encode("ascii")
    return BASE_SUBJECT+int.from_bytes(hashlib.sha256(raw).digest()[:8],"big")%9_999_983
def object_id(feature,value):
    require(type(feature) is int and feature in ROLES
            and type(value) is int and value in (0,1),"OBJECT")
    raw=f"know18:object-opaque:v1:{feature}:{value}".encode("ascii")
    return BASE_OBJECT+int.from_bytes(hashlib.sha256(raw).digest()[:8],"big")%9_999_983
def patterns(seed):
    require(type(seed) is int and seed in SEEDS,"PATTERNS")
    probes=list(range(16)); held=list(range(16))
    random.Random(seed*109+31).shuffle(probes)
    random.Random(seed*109+97).shuffle(held)
    return tuple(probes+[0,15]+held)
def source_rows(seed):
    p=patterns(seed)
    require(len(set(subject(seed,e) for e in range(34)))==34
            and len(set(object_id(f,b) for f in ROLES for b in (0,1)))==8,
            "SOURCE_IDENTIFIER_COLLISION")
    rows=[[subject(seed,e),PREDICATES[f],object_id(f,(p[e]>>f)&1),
           f"know18:s{seed}:entity{e:02d}:source{f}"]
          for e in range(34) for f in ROLES]
    require(len(rows)==136,"SOURCE_ROW_BUDGET")
    return sorted(rows,key=lambda r:r[3])
def bundle(seed):
    from yggdrasil.native_cumulative_facts import BUNDLE_SCHEMA
    return canonical({"schema":BUNDLE_SCHEMA,
        "source_id":f"know18-synthetic-{seed}",
        "source_mode":"engineering_fixture_only",
        "source_kind":"direct_public_observation",
        "records":source_rows(seed)})
def bit(facts,seed,e,feature):
    q=subject(seed,e);p=PREDICATES[feature]
    records=[facts.fact(q,p,object_id(feature,b)) for b in (0,1)]
    valid=[
        row.get("classification")=="DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
        and row.get("witnessed") is True
        and row.get("source_mode")=="engineering_fixture_only"
        and row.get("source_provenance")=="SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED"
        and row.get("native_accepted") is False
        and row.get("verified_new_real_knowledge") is False
        and row.get("can_write_causal_consequence") is False
        for row in records]
    return valid.index(True) if valid.count(True)==1 else None
def raw_properties(facts,seed,e):
    vals=[bit(facts,seed,e,f) for f in ROLES]
    require(all(type(x) is int and x in (0,1) for x in vals),
            "MISSING_CONFLICTING_OR_FORGED_SOURCE")
    return tuple(vals)
def numeric_context(raw_bits):
    require(type(raw_bits) in (list,tuple) and len(raw_bits)==4
            and all(type(v) is int and v in (0,1) for v in raw_bits),
            "RAW_CONTEXT")
    return sum(x<<i for i,x in enumerate(raw_bits))
def outcome(action,hidden_bit):
    require(type(action) is int and action in (0,1)
            and type(hidden_bit) is int and hidden_bit in (0,1),
            "ACTION_OUTCOME")
    return action*hidden_bit
def utility_from_witnesses(observed):
    """Four ACTUAL witnessed outcomes, not a source-derived utility label."""
    require(type(observed) is list and len(observed)==4
            and all(type(x) is int and x in (0,1) for x in observed),
            "FOUR_COUNTERFACTUAL_WITNESSES")
    return int(sum(observed)==2)
def training_rows(facts,seed):
    require(type(seed) is int and seed in TRAIN,"TRAIN_SEED")
    rows=[];total_actions=0
    for entity in PROBE:
        features=raw_properties(facts,seed,entity)
        context=numeric_context(features)
        for action in (0,1):
            observed=[outcome(action,features[role]) for role in ROLES]
            # Each oracle output is a separately disclosed action consequence.
            total_actions+=len(observed)
            label=utility_from_witnesses(observed)
            rows.append([context,action,label])
    require(len(rows)==32 and total_actions==128
            and len({(r[0],r[1]) for r in rows})==32,
            "FIXED_TRAINING_ACTION_BUDGET")
    return rows,total_actions

def symbolic(rows):
    groups={}
    for ctx,a,y in rows:
        groups.setdefault((ctx,a),[]).append(y)
    require(len(groups)==32,"SYMBOLIC_COMPLETE_FIT")
    return {k:Fraction(sum(vals),len(vals)) for k,vals in groups.items()}
def conventional_tree(rows):
    """Independent depth-five complete input leaf estimator (all 32 leaves)."""
    leaves={}
    for p in range(16):
        for a in (0,1):
            ys=[y for ctx,act,y in rows if (ctx,act)==(p,a)]
            require(len(ys)>0,"CONVENTIONAL_LEAF_SUPPORT")
            leaves[(p,a)]=Fraction(sum(ys),len(ys))
    return lambda ctx,a:leaves[(ctx,a)]

def choose_query(facts,seed,possible,used,policy,rand=None):
    require(type(possible) is tuple and possible
            and all(type(k) is int and k in ROLES for k in possible),
            "CANDIDATE_SET")
    if policy=="zero":return None
    if policy=="random":
        require(rand is not None,"RANDOM_SOURCE")
        return rand.choice([(e,a) for e in PROBE for a in (0,1)
                            if (e,a) not in used])
    if policy=="passive":
        return next(((e,0) for e in PROBE if (e,0) not in used),None)
    require(policy=="oracle" or callable(policy),"POLICY_CONTRACT")
    scored=[]
    for e in PROBE:
        raw=raw_properties(facts,seed,e)
        ctx=numeric_context(raw)
        for a in (0,1):
            if (e,a) in used:continue
            if policy=="oracle":
                # Explicit handcrafted candidate-aware reference, not learned.
                positive=sum(outcome(a,raw[k]) for k in possible)
                gain=min(positive,len(possible)-positive)
                value=Fraction(int(gain*2==len(possible)))
            else:
                value=policy(ctx,a)
            if value is None:continue
            require(type(value) in (int,Fraction) and
                    not isinstance(value,bool) and 0<=value<=1,
                    "PREDICTION_CONTRACT")
            scored.append((-Fraction(value),subject(seed,e),a,e))
    if not scored:return None
    best=min(scored)
    if best[0]>=0:return None
    return best[3],best[2]
def attempt(facts,seed,private_role,policy):
    require(type(seed) is int and seed in HELD_SEEDS
            and type(private_role) is int and private_role in ROLES,
            "HELD_ROLE_ONLY")
    remain=ROLES;used=set();record=[]
    rng=random.Random(seed*37+73)
    for _ in range(2):
        query=choose_query(facts,seed,remain,used,policy,rng)
        if query is None:break
        e,a=query;used.add(query)
        bits=raw_properties(facts,seed,e)
        disclosed=outcome(a,bits[private_role])
        remain=tuple(k for k in remain if outcome(a,bits[k])==disclosed)
        require(private_role in remain,"TRUE_ROLE_DISCARDED")
        record.append([e,a,disclosed])
    return {"selected":remain[0] if len(remain)==1 else None,
            "remaining":len(remain),"witnessed_actions":len(record),
            "transcript":record}

def prove(history_path,joint_path):
    from yggdrasil.native_context_accumulator import NativeContextAccumulator
    from yggdrasil.native_context_basis import NativeContextBasis
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_knowledge_activation import (
        PINNED_ROWS,PINNED_PACKED_SHA,open_installed_session)
    started=time.monotonic()
    protocol=json.loads(Path(__file__).with_name("know18_protocol.json").read_bytes())
    require(protocol.get("schema")==
            "yggdrasil.know18.raw-feature-intervention-utility-frozen-dev.v1"
            and protocol.get("seeds",{}).get("train_A")==TRAIN[0]
            and protocol.get("seeds",{}).get("train_B")==TRAIN[1]
            and protocol.get("seeds",{}).get("held")==list(HELD_SEEDS),
            "PREREG_DRIFT")
    original_joint=Path(joint_path)
    require(original_joint.is_file() and not original_joint.is_symlink()
            and digest(original_joint.read_bytes())==JOINT_SHA,
            "ORIGINAL_ARCHIVED_MODEL_PIN")
    with open_installed_session(history_path) as history:
        require(len(history._weights)==PINNED_ROWS==21_343_681
                and PINNED_PACKED_SHA==IMAGE_SHA,"ORIGINAL_HISTORICAL_PIN")
        old_edges=[tuple(history._weights.row_at(i))
                   for i in (0,PINNED_ROWS-1)]
        facts=CumulativeNativeFacts(history)
        pristine=facts.checkpoint()
        source_hashes={}
        for seed in SEEDS:
            raw=bundle(seed)
            facts,receipt=facts.stage(raw,digest(raw))
            require(receipt["new_unique_facts"]==136
                    and receipt["native_accepted"] is False,
                    "SYNTHETIC_FACTUAL_ONLY")
            source_hashes[seed]=digest(raw)
        A,nA=training_rows(facts,TRAIN[0])
        B,nB=training_rows(facts,TRAIN[1])
        require(nA+nB==256,"WITNESSED_TRAINING_BUDGET")
        # The lower-degree original model must genuinely be inadequate.
        try:
            NativeContextBasis(context_bits=4).stage_fit(
                0,A,digest(canonical(A)),max_degree=3)
        except ValueError as exc:
            require("MODEL_CLASS_INADEQUATE" in str(exc),
                    "DEGREE_THREE_REJECTION_REASON")
        else:
            raise ValueError("YGG_KNOW18_DEGREE_THREE_FALSE_ACCEPT")
        native=NativeContextAccumulator(context_bits=4).stage_update(
            0,A,digest(canonical(A)),max_degree=4)
        old=tuple(native.predict(0,p,a)
                  for p in range(16) for a in (0,1))
        require(all(type(x) is int and x in (0,1) for x in old),
                "A_FIT_SUPPORT")
        native=native.stage_update(0,B,digest(canonical(B)),max_degree=4)
        now=tuple(native.predict(0,p,a)
                  for p in range(16) for a in (0,1))
        old_changes=sum(x!=y for x,y in zip(old,now))
        require(old_changes==0 and native.profile_info(0)["batches"]==2,
                "A_TO_B_OLD_READOUT")
        chk=native.checkpoint()
        cold=NativeContextAccumulator.restore(chk,digest(chk))
        require(cold.checkpoint()==chk and
                tuple(cold.predict(0,p,a)
                      for p in range(16) for a in (0,1))==old,
                "COLD_NATIVE_READOUT")
        full=A+B
        refit=NativeContextBasis(context_bits=4).stage_fit(
            0,full,digest(canonical(full)),max_degree=4)
        symbol=symbolic(full)
        tree=conventional_tree(full)
        oracle_values={(p,a):int(a==1 and p.bit_count()==2)
                       for p in range(16) for a in (0,1)}
        require(all(old[p*2+a]==oracle_values[p,a]
                    ==refit.predict(0,p,a)
                    ==symbol[p,a]==tree(p,a)
                    for p in range(16) for a in (0,1)),
                "FULLY_TRAINED_EQUAL_INFORMATION_CONTROL_TIE")
        policies={
            "native":lambda p,a:cold.predict(0,p,a),
            "native_full_refit":lambda p,a:refit.predict(0,p,a),
            "symbolic":lambda p,a:symbol[p,a],
            "conventional_tree":tree,
            "oracle":"oracle","random":"random",
            "passive":"passive","zero":"zero"}
        held_result=[]
        for seed in HELD_SEEDS:
            for role in ROLES:
                row={"seed":seed,"role_scoring_only":role,
                     "source_graph_sha256":source_hashes[seed],
                     "policies":{}}
                for name,predictor in policies.items():
                    row["policies"][name]=attempt(
                        facts,seed,role,predictor)
                require(all(
                    row["policies"][p]["transcript"]
                    ==row["policies"]["native"]["transcript"]
                    for p in ("native_full_refit","symbolic","conventional_tree")),
                    "MATCHED_EXPERIMENT_TRAJECTORIES")
                require(row["policies"]["passive"]["selected"] is None
                        and row["policies"]["zero"]["selected"] is None,
                        "PASSIVE_SOURCE_ONLY_FAIL_CLOSED")
                held_result.append(row)
        saved=facts.checkpoint()
        cold_facts=CumulativeNativeFacts(
            history,saved,checkpoint_sha256=facts.checkpoint_sha256)
        require(cold_facts.checkpoint()==saved
                and CumulativeNativeFacts(history).checkpoint()==pristine,
                "COLD_FACTUAL_SOURCE")
        for seed in SEEDS:
            for e in range(34):
                require(raw_properties(cold_facts,seed,e)
                        ==tuple((patterns(seed)[e]>>k)&1 for k in ROLES),
                        "COLD_SOURCE_VALUE")
        require(all(history.fact(*row)["witnessed"] for row in old_edges)
                and digest(original_joint.read_bytes())==JOINT_SHA,
                "OLD_NATIVE_OR_SOURCE_MUTATION")
    counts={name:sum(row["policies"][name]["selected"]==row["role_scoring_only"]
                     for row in held_result) for name in policies}
    actions={name:sum(row["policies"][name]["witnessed_actions"]
                      for row in held_result) for name in policies}
    require(len(held_result)==12 and
            counts["native"]==counts["native_full_refit"]
            ==counts["symbolic"]==counts["conventional_tree"]
            and counts["zero"]==counts["passive"]==0,
            "FROZEN_COMPARISON_CONSISTENCY")
    return {
        "schema":"yggdrasil.know18.raw-input-learned-utility-result.v1",
        "classification":"SOURCE_FREE_DEVELOPMENT_ONLY",
        "preregistration_commit":PREREG,
        "native_input_bits":"four_direct_raw_QPQ_features_plus_action",
        "handcrafted_balanced_feature_provided_to_native":False,
        "full_four_role_counterfactual_oracle_training":True,
        "counterfactual_training_outcomes":256,
        "native_training_utility_examples":64,
        "source_identical_synthetic_QPQ_records":680,
        "native_model_class_degree":4,
        "degree_three_model_inadequate":True,
        "old_A_readout_changes":old_changes,
        "native_and_factual_cold_restored":True,
        "native_checkpoint_bytes":len(chk),
        "held_worlds":len(held_result),
        "role_identification":counts,
        "action_budgets_consumed":actions,
        "engineering_identification_target_met":counts["native"]==12,
        "native_superiority_over_equally_informed_controls":False,
        "scientific_decision":"DEV_NO_GO_STRONGEST_CONTROL_TIE",
        "protected_first_use":False,
        "owner_checkpoint":"UNVERIFIED",
        "canonical_training":False,"deployment":"NONE",
        "historical_image_sha256":IMAGE_SHA,
        "original_amalgam_joint_sha256":JOINT_SHA,
        "per_world":held_result,
        "duration_seconds_excluding_downloads":round(time.monotonic()-started,6)
    }
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--installed-session",type=Path,required=True)
    p.add_argument("--joint-checkpoint",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    r=prove(args.installed_session,args.joint_checkpoint)
    args.output.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",
                           encoding="utf-8")
    print("KNOW18_RAW_INPUT_RESULT="+json.dumps({
        "learned_roles":r["role_identification"]["native"],
        "symbolic_roles":r["role_identification"]["symbolic"],
        "oracle_roles":r["role_identification"]["oracle"],
        "native_target_met":r["engineering_identification_target_met"],
        "science":r["scientific_decision"]},sort_keys=True))
if __name__=="__main__":main()

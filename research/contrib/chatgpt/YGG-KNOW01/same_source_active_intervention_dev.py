"""KNOW16: source-identical counterfactual worlds, bounded interventions.

Independent synthetic development. Four hidden causal roles produce exactly the
same source-typed factual graph and opaque public IDs. Two chosen action probes
test *intervention necessity*; the learned native outcome model is subsequently
fit using the unchanged NativeContextAccumulator. No accepted model writes.
"""
from __future__ import annotations
import argparse,hashlib,json,random,time
from fractions import Fraction
from pathlib import Path

SEEDS=(401,509,617)
ROLES=(0,1,2,3)
PREDICATES=(971,972,973,974)
JOINT_SHA="576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
IMAGE_SHA="6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1"
PREREG="62a6573644dc1dd40cf6f2c8df0e74ab831db9f9"
PROBE=tuple(range(16))
FIXED=tuple(range(16,18))
HELD=tuple(range(18,34))
N=34
SOURCE_BASE=4_221_000_000
OBJECT_BASE=4_222_000_000

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("ascii")
def digest(raw):
    return hashlib.sha256(raw).hexdigest()
def require(condition,label):
    if not condition: raise ValueError("YGG_KNOW16_"+label)
def _opaque(kind,seed,index,base):
    require(type(seed) is int and seed in SEEDS
            and type(index) is int and index>=0 and index<40,"OPAQUE_DOMAIN")
    salt=f"know16:opaque-uuid-v1:{kind}:{seed}:{index}"
    tail=int.from_bytes(hashlib.sha256(salt.encode("ascii")).digest()[:8],"big")%999_983
    return base+tail
def subject(seed,e):
    require(type(e) is int and 0<=e<N,"ENTITY")
    return _opaque("subject",seed,e,SOURCE_BASE)
def object_id(feature,bit):
    require(type(feature) is int and feature in ROLES
            and type(bit) is int and bit in (0,1),"OBJECT")
    # Stable across ALL worlds, without any task/phase/causal-role encoding.
    salt=f"know16:opaque-object-v1:{feature}:{bit}"
    tail=int.from_bytes(hashlib.sha256(salt.encode("ascii")).digest()[:8],"big")%999_983
    return OBJECT_BASE+tail
def patterns(seed):
    require(type(seed) is int and seed in SEEDS,"SEED")
    probe=list(range(16)); random.Random(seed*101+17).shuffle(probe)
    held=list(range(16)); random.Random(seed*101+83).shuffle(held)
    return tuple(probe+[0,15]+held)
def source_rows(seed):
    ps=patterns(seed)
    require(len(ps)==N and len(set(subject(seed,e) for e in range(N)))==N
            and len(set(object_id(f,b) for f in ROLES for b in (0,1)))==8,
            "SOURCE_ID_COLLISION")
    data=[]
    for e,pat in enumerate(ps):
        q=subject(seed,e)
        for feature,p in enumerate(PREDICATES):
            bit=(pat>>feature)&1
            data.append([q,p,object_id(feature,bit),
                f"know16:s{seed}:entity{e:02d}:feature{feature}"])
    require(len(data)==136,"SOURCE_ROWS")
    return sorted(data,key=lambda x:x[3])
def source_bundle(seed):
    from yggdrasil.native_cumulative_facts import BUNDLE_SCHEMA
    return canonical({"schema":BUNDLE_SCHEMA,
        "source_id":f"know16-source-identical-{seed}",
        "source_kind":"direct_public_observation",
        "source_mode":"engineering_fixture_only",
        "records":source_rows(seed)})
def factual_bit(facts,seed,e,feature):
    require(type(feature) is int and feature in ROLES,"FEATURE")
    q=subject(seed,e);p=PREDICATES[feature]
    answers=[facts.fact(q,p,object_id(feature,b)) for b in (0,1)]
    valid=[
        a.get("classification")=="DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
        and a.get("source_mode")=="engineering_fixture_only"
        and a.get("source_provenance")=="SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED"
        and a.get("witnessed") is True
        and a.get("native_accepted") is False
        and a.get("verified_new_real_knowledge") is False
        and a.get("can_write_causal_consequence") is False
        for a in answers]
    return valid.index(True) if valid.count(True)==1 else None
def observations(facts,seed,e):
    results=tuple(factual_bit(facts,seed,e,f) for f in ROLES)
    require(all(type(v) is int and v in (0,1) for v in results),
            "SOURCE_UNQUALIFIED_OR_CONFLICTING")
    return results
def outcome(action,bit):
    require(type(action) is int and action in (0,1)
            and type(bit) is int and bit in (0,1),"CAUSAL_OUTCOME_DOMAIN")
    return action*bit

def best_intervention(facts,seed,possible,used):
    """Public portfolio disagreement maximization, NOT trained native agency.

    Purely hypothesis predictions for action 0 always equal 0; action 1 can
    distinguish roles. The equal-information exact-symbolic arm can use this
    same rule; no special optimization advantage is claimed for the native.
    """
    require(type(possible) is tuple and bool(possible)
            and all(type(k) is int and k in ROLES for k in possible),
            "CANDIDATE_SET")
    choices=[]
    for e in PROBE:
        bits=observations(facts,seed,e)
        for action in (0,1):
            if (e,action) in used:continue
            vals=[outcome(action,bits[k]) for k in possible]
            n1=sum(vals);n0=len(vals)-n1
            gain=min(n0,n1)
            if gain>0:choices.append((-gain,subject(seed,e),action,e))
    if not choices:return None
    _,_,action,e=min(choices)
    return e,action
def update_hypotheses(facts,seed,possible,e,action,witness):
    require(type(witness) is int and witness in (0,1),
            "WITNESSED_CONSEQUENCE")
    bits=observations(facts,seed,e)
    return tuple(k for k in possible if outcome(action,bits[k])==witness)

def solve_role(facts,seed,hidden_role,policy="active"):
    """Hidden role appears ONLY in the oracle response, never source or query."""
    require(type(hidden_role) is int and hidden_role in ROLES,"PRIVATE_ROLE")
    require(policy in ("active","random","passive"),"POLICY")
    possible=ROLES
    used=set()
    transcript=[]
    prng=random.Random(seed*31+79)  # same draws across all hidden roles
    perm=[(e,a) for e in PROBE for a in (0,1)]
    prng.shuffle(perm)
    for step in range(2):
        if policy=="active":
            q=best_intervention(facts,seed,possible,used)
        elif policy=="random":
            q=next(((e,a) for e,a in perm if (e,a) not in used),None)
        else:
            q=next(((e,0) for e in PROBE if (e,0) not in used),None)
        require(q is not None,"INTERVENTION_NOT_INFORMATIVE")
        e,a=q;used.add(q)
        bits=observations(facts,seed,e)
        revealed=outcome(a,bits[hidden_role])
        possible=update_hypotheses(facts,seed,possible,e,a,revealed)
        require(hidden_role in possible,"HIDDEN_ROLE_ELIMINATED")
        transcript.append([e,a,revealed])
    return {
        "selected":possible[0] if len(possible)==1 else None,
        "remaining_candidates":len(possible),
        "observations":transcript,
        "witnessed_actions":2
    }

def fit_rows(facts,seed,role):
    """Role-independent fixed schedule of 4 separately witnessed outcomes."""
    return [
        [factual_bit(facts,seed,e,role),a,
         outcome(a,factual_bit(facts,seed,e,role))]
        for e in FIXED for a in (0,1)
    ]
def score(facts,seed,role,predictors):
    brier={name:Fraction(0) for name in predictors}
    covered={name:0 for name in predictors}
    optimal={name:0 for name in predictors}
    for e in HELD:
        bit=factual_bit(facts,seed,e,role)
        require(bit in (0,1),"HELD_SOURCE_UNKNOWN")
        pred={}
        for a in (0,1):
            y=outcome(a,bit)
            p={}
            for name,fn in predictors.items():
                value=fn(bit,a)
                require(value is not None and type(value) in (Fraction,int)
                        and not isinstance(value,bool) and 0<=value<=1,
                        "HELD_MODEL_ABSTAIN")
                p[name]=Fraction(value)
                brier[name]+=(p[name]-y)**2
                covered[name]+=1
            pred[a]=p
        for name in predictors:
            chosen=int(pred[1][name]>pred[0][name])
            optimal[name]+=int(outcome(chosen,bit)==max(
                outcome(0,bit),outcome(1,bit)))
    return {"predictions":len(HELD)*2,
            "brier":{name:[(score/32).numerator,(score/32).denominator]
                     for name,score in brier.items()},
            "covered":covered,"optimal_decisions":optimal}

def prove(installed_session,joint_checkpoint):
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_context_accumulator import NativeContextAccumulator
    from yggdrasil.native_context_basis import NativeContextBasis
    from yggdrasil.native_knowledge_activation import (
        PINNED_PACKED_SHA,PINNED_ROWS,open_installed_session)
    start=time.monotonic()
    plan=json.loads(Path(__file__).with_name("know16_protocol.json").read_bytes())
    require(plan["schema"]==
            "yggdrasil.know16.source-identical-intervention-value-dev-protocol.v1"
            and plan["frozen_seeds"]==list(SEEDS)
            and plan["counterfactual_roles"]==list(ROLES)
            and plan["source_design"]["new_synthetic_fact_count"]==408,
            "PREREG_DRIFT")
    joint_path=Path(joint_checkpoint)
    require(joint_path.is_file() and not joint_path.is_symlink()
            and digest(joint_path.read_bytes())==JOINT_SHA,"ARCHIVED_MODEL_PIN")
    result=[];before_after_changes=0;max_bytes=0
    with open_installed_session(installed_session) as history:
        require(len(history._weights)==PINNED_ROWS==21_343_681
                and PINNED_PACKED_SHA==IMAGE_SHA,"HISTORICAL_TRAIN_PIN")
        first,last=(tuple(history._weights.row_at(i))
                    for i in (0,PINNED_ROWS-1))
        pristine=CumulativeNativeFacts(history)
        original=pristine.checkpoint()
        facts=pristine
        for seed in SEEDS:
            payload=source_bundle(seed)
            # This identical payload is used in *every* role world for seed.
            facts,receipt=facts.stage(payload,digest(payload))
            require(receipt["new_unique_facts"]==136
                    and receipt["native_accepted"] is False,"NEW_SOURCE_BUNDLE")
            graph_hash=digest(payload)
            for role in ROLES:
                require(digest(source_bundle(seed))==graph_hash,
                        "SOURCE_VARIATION_BY_PRIVATE_ROLE")
                # All four roles are possible after zero actions.
                require(len(ROLES)==4,"SOURCE_ONLY_ROLE_LEAK")
                active=solve_role(facts,seed,role,"active")
                random_control=solve_role(facts,seed,role,"random")
                passive_control=solve_role(facts,seed,role,"passive")
                require(active["selected"]==role
                        and len(active["observations"])==2
                        and all(a==1 for e,a,y in active["observations"])
                        and passive_control["selected"] is None,
                        "ACTIVE_IDENTIFIABILITY")
                # Strong active symbolic model sees exactly the same source,
                # actions, and consequence outcomes, hence same two-step result.
                symbolic_active=solve_role(facts,seed,role,"active")
                require(symbolic_active==active,"SYMBOLIC_ACTIVE_PARITY")
                A=fit_rows(facts,seed,role)
                require(len(A)==4 and all(v is not None for row in A for v in row),
                        "COMMON_FIT_SUPPORT")
                native=NativeContextAccumulator(context_bits=1).stage_update(
                    0,A,digest(canonical(A)),max_degree=2)
                old=tuple(native.predict(0,bit,a)
                          for bit in (0,1) for a in (0,1))
                require(old==(0,0,0,1),"NATIVE_FIT_A")
                B=[]
                for e,a,consequence in active["observations"]:
                    observed=factual_bit(facts,seed,e,role)
                    require(observed in (0,1),"SELECTED_CUE_READOUT")
                    B.append([observed,a,consequence])
                native=native.stage_update(
                    0,B,digest(canonical(B)),max_degree=2)
                require(native.profile_info(0)["batches"]==2,
                        "SHARED_SLOT_BATCHES")
                after=tuple(native.predict(0,bit,a)
                            for bit in (0,1) for a in (0,1))
                before_after_changes+=sum(x!=y for x,y in zip(old,after))
                require(old==after,"OLD_FIT_A_DRIFT")
                checkpoint=native.checkpoint()
                max_bytes=max(max_bytes,len(checkpoint))
                cold=NativeContextAccumulator.restore(checkpoint,digest(checkpoint))
                require(cold.checkpoint()==checkpoint
                        and tuple(cold.predict(0,bit,a)
                                  for bit in (0,1) for a in (0,1))==old,
                        "NATIVE_COLD_RETAIN")
                full=A+B
                refit=NativeContextBasis(context_bits=1).stage_fit(
                    0,full,digest(canonical(full)),max_degree=2)
                symbolic={}
                for ctx,a,y in full:symbolic.setdefault((ctx,a),[]).append(y)
                symbolic={k:Fraction(sum(v),len(v)) for k,v in symbolic.items()}
                tree={}
                for ctx in (0,1):
                    for a in (0,1):
                        vals=[y for c,act,y in full if (c,act)==(ctx,a)]
                        require(bool(vals),"CONVENTIONAL_LEAF_UNTRAINED")
                        tree[(ctx,a)]=Fraction(sum(vals),len(vals))
                metrics=score(facts,seed,role,{
                    "native":lambda bit,a:cold.predict(0,bit,a),
                    "native_full_refit":lambda bit,a:refit.predict(0,bit,a),
                    "exact_symbolic":lambda bit,a:symbolic[(bit,a)],
                    "conventional_tree":lambda bit,a:tree[(bit,a)]})
                require(all(metrics["brier"][a]==[0,1] for a in
                            ("native","native_full_refit","exact_symbolic",
                             "conventional_tree")),"STRONG_CONTROL_TIE")
                result.append({
                    "seed":seed,"hidden_role_test_index":role,
                    "source_bundle_sha256":graph_hash,
                    "static_source_only_resolves_role":False,
                    "active_two_action_resolves_role":True,
                    "symbolic_active_resolves_role":True,
                    "random_two_action_resolves_role":
                        random_control["selected"]==role,
                    "passive_two_action_resolves_role":False,
                    "interventions":active["observations"],
                    "held":metrics,"native_checkpoint_sha256":digest(checkpoint)
                })
        snapshot=facts.checkpoint()
        cold_facts=CumulativeNativeFacts(
            history,snapshot,checkpoint_sha256=facts.checkpoint_sha256)
        require(cold_facts.checkpoint()==snapshot
                and pristine.checkpoint()==original,
                "FACTUAL_CHECKPOINT_DRIFT")
        for seed in SEEDS:
            for e in range(N):
                true=tuple((patterns(seed)[e]>>k)&1 for k in ROLES)
                require(observations(cold_facts,seed,e)==true,
                        "HISTORICAL_COLD_SOURCE_READOUT")
        require(history.fact(*first)["witnessed"]
                and history.fact(*last)["witnessed"]
                and digest(joint_path.read_bytes())==JOINT_SHA,
                "ORIGINAL_MODEL_OR_TRAIN_FACT_CHANGED")
    require(len(result)==12 and before_after_changes==0,
            "FROZEN_COHORT_COUNTS")
    covered={key:sum(run["held"]["covered"][key] for run in result)
             for key in ("native","native_full_refit","exact_symbolic",
                         "conventional_tree")}
    return {"schema":"yggdrasil.know16.source-identical-active-probe-result.v1",
        "classification":"SYNTHETIC_BENCHMARK_VALIDITY_AND_INTERVENTION_NECESSITY",
        "preregistration_commit":PREREG,"seeds":list(SEEDS),
        "counterfactual_worlds":len(result),
        "source_graph_identical_across_four_roles_for_each_seed":True,
        "static_qpq_records":408,
        "source_only_roles_resolved":0,
        "two_action_active_roles_resolved":sum(x["active_two_action_resolves_role"] for x in result),
        "symbolic_active_roles_resolved":sum(x["symbolic_active_resolves_role"] for x in result),
        "two_action_random_roles_resolved":sum(x["random_two_action_resolves_role"] for x in result),
        "two_action_passive_roles_resolved":0,
        "active_witnessed_interventions":24,
        "common_native_fit_witnesses":48,
        "held_predictions":sum(x["held"]["predictions"] for x in result),
        "old_A_native_readout_changes":before_after_changes,
        "native_cold_restored":True,
        "factual_cold_restored":True,
        "held_mean_brier_by_arm":{arm:[0,1] for arm in covered},
        "held_supported_forecasts":covered,
        "held_optimal_action_decisions":{arm:sum(x["held"]["optimal_decisions"][arm]
                                    for x in result) for arm in covered},
        "max_native_checkpoint_bytes":max_bytes,
        "historical_train_rows":21_343_681,
        "historical_image_sha256":IMAGE_SHA,
        "original_amalgam_joint_sha256":JOINT_SHA,
        "scientific_decision":"DEV_NO_GO_STRONGEST_CONTROL_TIE",
        "native_superiority_over_fully_informed_controls":False,
        "original_first_use":False,"canonical_model_training":False,
        "canonical_owner_checkpoint":"UNVERIFIED","deployment":"NONE",
        "per_world":result,
        "wall_seconds_excluding_source_fetch":round(time.monotonic()-start,6)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--installed-session",type=Path,required=True)
    p.add_argument("--joint-checkpoint",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    receipt=prove(args.installed_session,args.joint_checkpoint)
    args.output.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",
                           encoding="utf-8")
    print("KNOW16_SOURCE_IDENTICAL_ACTIVE_DEV="+json.dumps({
        "source_only_roles":receipt["source_only_roles_resolved"],
        "active_roles":receipt["two_action_active_roles_resolved"],
        "strongest_control_advantage":False,
        "decision":receipt["scientific_decision"]},sort_keys=True))
if __name__=="__main__":main()

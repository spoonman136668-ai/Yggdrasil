"""Frozen WSP168 causal relation composition and public old/new retrieval.

Only authored synthetic public action-consequence fixtures are scored.
The generating world's relation identity is used ONLY by the evaluator,
NEVER passed into the learner, independent batch control, or retrieval.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import random
import subprocess
import sys
import time
import unittest

HERE=Path(__file__).resolve().parents[1]
for p in ("WSP-159","WSP-160","WSP-166","WSP-167"):
    sys.path.insert(0,str(HERE/p))

from public_boundary import PublicTransition
from test_direct_weights import solve_gaussian
from paired_action_weights import _pair_features
from test_paired_action_weights import (
    GRID,COEFF,OLD_CONTRAST,TRIPLE,old_action_zero,record,train_old
)
from feature_tournament import features as prev_features
from composed_effects import (
    ComposedPublicEffect, RetainedPublicLaws,constructed_features,
    fit_constructed,fit_public_pairs,choose_composition, MAGIC
)

SEEDS=(3427,3539,3659)
LAMBDA=1./64
FIFTH_AMPLITUDE=4.


def synthetic_pair(state,seed,kind):
    """The synthetic source knows the law; learner never receives kind."""
    old0=old_action_zero(state)
    if kind=="old":
        effect=OLD_CONTRAST
    elif kind in ("new","fifth"):
        s=state
        z=tuple(float(v) for v in prev_features(state,None))
        triple=s[0]*s[1]*s[2]
        quartic=4*triple*s[3]
        offset=(SEEDS.index(seed)-1)/32.
        effect=tuple(
            math.fsum(COEFF[k][j]*z[j] for j in range(8))+
            (offset if k%2==0 else -offset)+
            TRIPLE[k]*(triple+quartic+
                       (FIFTH_AMPLITUDE*quartic*s[3] if kind=="fifth" else 0.))
            for k in range(4))
    else:
        raise ValueError("TEST_GENERATOR_KIND")
    old1=tuple(old0[k]+effect[k] for k in range(4))
    return record(state,0,old0),record(state,1,old1)


def fixture(seed):
    states=list(GRID)
    random.Random(seed).shuffle(states)
    fit_states=states[:48]
    held_states=states[48:96]
    assert len(set(fit_states)&set(held_states))==0
    parent_fit=[synthetic_pair(state,seed,"old") for state in fit_states]
    new_fit=[synthetic_pair(state,seed,"new") for state in fit_states]
    new_held=[synthetic_pair(state,seed,"new") for state in held_states]
    old_held=[synthetic_pair(state,seed,"old") for state in held_states]
    fifth_held=[synthetic_pair(state,seed,"fifth") for state in held_states]
    return parent_fit,new_fit,new_held,old_held,fifth_held,held_states


def fit_batch(pairs,factor):
    """Independent fully trained conventional Gaussian ridge, same public FIT."""
    width=len(constructed_features(pairs[0][0].observation,factor))
    gram=[[float(i==j)*LAMBDA for j in range(width)] for i in range(width)]
    rhs=[[0.]*4 for _ in range(width)]
    for a,b in pairs:
        if a.action!=0 or b.action!=1 or a.observation!=b.observation:
            raise ValueError("BATCH_PUBLIC_PAIR")
        x=tuple(float(v) for v in constructed_features(a.observation,factor))
        y=tuple(b.next_observation[k]-a.next_observation[k] for k in range(4))
        for i in range(width):
            for j in range(width):
                gram[i][j]+=x[i]*x[j]
            for k in range(4):
                rhs[i][k]+=x[i]*y[k]
    weights=tuple(solve_gaussian(gram,[rhs[i][k] for i in range(width)])
                  for k in range(4))
    def effect(state):
        x=tuple(float(v) for v in constructed_features(state,factor))
        return tuple(math.fsum(weights[k][j]*x[j] for j in range(width))
                     for k in range(4))
    return effect


def conventional_selection(inner36,select12):
    def scored(pred):
        sq=[]
        for a,b in select12:
            _,y=_pair_features(a,b)
            guess=pred(a.observation)
            sq.extend((guess[k]-float(y[k]))**2 for k in range(4))
        return math.sqrt(math.fsum(sq)/len(sq))
    null=scored(fit_batch(inner36,None))
    scores={i:scored(fit_batch(inner36,i)) for i in range(4)}
    best=min(range(4),key=lambda i:(scores[i],i))
    return best if null-scores[best]>=.01 else None


def batch_full_13_effect(pairs):
    """Independently fitted stronger full-composition polynomial basis."""
    width=13
    def vector(state):
        x=tuple(float(v) for v in constructed_features(state,None))
        return x+tuple(float(constructed_features(state,i)[-1]) for i in range(4))
    gram=[[float(i==j)*LAMBDA for j in range(width)] for i in range(width)]
    rhs=[[0.]*4 for _ in range(width)]
    for zero,one in pairs:
        x=vector(zero.observation)
        y=tuple(one.next_observation[k]-zero.next_observation[k] for k in range(4))
        for i in range(width):
            for j in range(width):
                gram[i][j]+=x[i]*x[j]
            for k in range(4):
                rhs[i][k]+=x[i]*y[k]
    weights=tuple(solve_gaussian(gram,[rhs[i][k] for i in range(width)])
                  for k in range(4))
    def effect(state):
        x=vector(state)
        return tuple(math.fsum(weights[k][j]*x[j] for j in range(width))
                     for k in range(4))
    return effect


def effect_rmse(pairs,effect):
    errors=[]
    for zero,one in pairs:
        _,truth=_pair_features(zero,one)
        guess=effect(zero.observation)
        errors.extend((guess[k]-float(truth[k]))**2 for k in range(4))
    return math.sqrt(math.fsum(errors)/len(errors))


def independent_public_retriever(parent,new_batch,state,action,history=()):
    """Fully trained conventional two-law last-observation selector.

    Separately fitted batch polynomial; never reads direct model internals,
    hidden source family, true evaluator regime, or current target.
    """
    old=parent.predict(state,action)
    if action==0 or not history:
        return old
    previous=history[-1]
    if type(previous) is not PublicTransition or previous.terminated or previous.truncated:
        raise ValueError("CONVENTIONAL_BAD_HISTORY")
    if previous.action!=1:
        return old
    pred_old=parent.predict(previous.observation,1)
    base_new=parent.predict(previous.observation,0)
    delta_new=new_batch(previous.observation)
    pred_new=tuple(base_new[k]+delta_new[k] for k in range(4))
    err_old=math.fsum((pred_old[k]-previous.next_observation[k])**2 for k in range(4))
    err_new=math.fsum((pred_new[k]-previous.next_observation[k])**2 for k in range(4))
    if err_new>=err_old:
        return old
    zero=parent.predict(state,0)
    delta=new_batch(state)
    return tuple(zero[k]+delta[k] for k in range(4))


def held_episode_streams(seed,held_states):
    """Evaluator regime labels are NOT written into any learner record."""
    order=list(held_states)
    random.Random(seed+6000).shuffle(order)
    groups=[]
    for i in range(16):
        if i<4:
            label="old_only"
        elif i<8:
            label="new_only"
        elif i<12:
            label="old_to_new"
        else:
            label="new_to_old"
        episode=[]
        for t in range(12):
            state=order[(i*13+t*7)%len(order)]
            if label=="old_only" or (label=="old_to_new" and t<6) or (
                    label=="new_to_old" and t>=6):
                truth="old"
            else:
                truth="new"
            _,one=synthetic_pair(state,seed,truth)
            public_row=PublicTransition.from_public(
                observation=one.observation,action=1,
                next_observation=one.next_observation,reward=1.,
                terminated=(t==11),truncated=False)
            episode.append((public_row,truth))
        groups.append((label,tuple(episode)))
    return groups


def score_prequential(episodes,learner,parent,batch_effect):
    pools={k:[] for k in (
        "old_only_later","new_only_later",
        "old_to_new_after_witness","new_to_old_after_witness",
        "old_to_new_switch_first","new_to_old_switch_first",
        "new_only_first","old_only_first",
        "always_old_all","always_new_all","oracle_upper_all",
        "retrieved_all","conventional_all"
    )}
    matched_gap=0.
    chosen={"old":0,"new":0}
    for label,ep in episodes:
        previous=()
        for t,(row,actual_mode) in enumerate(ep):
            state=row.observation
            # Mode is used by evaluator for bucket assignment ONLY.
            decision=learner.choose(previous)
            chosen[decision]+=1
            predicted=learner.predict(state,1,previous)
            control=independent_public_retriever(parent,batch_effect,state,1,previous)
            matched_gap=max(matched_gap,max(
                abs(predicted[k]-control[k]) for k in range(4)))
            always_old=parent.predict(state,1)
            base0=parent.predict(state,0)
            effect=batch_effect(state)
            always_new=tuple(base0[k]+effect[k] for k in range(4))
            oracle=always_old if actual_mode=="old" else always_new
            squared=lambda guess: [(guess[k]-row.next_observation[k])**2 for k in range(4)]
            pools["retrieved_all"].extend(squared(predicted))
            pools["conventional_all"].extend(squared(control))
            pools["always_old_all"].extend(squared(always_old))
            pools["always_new_all"].extend(squared(always_new))
            pools["oracle_upper_all"].extend(squared(oracle))
            bucket=None
            if label in ("old_only","new_only"):
                bucket=label+"_later" if t>0 else label+"_first"
            elif label=="old_to_new":
                bucket="old_to_new_after_witness" if t>=7 else (
                    "old_to_new_switch_first" if t==6 else None)
            elif label=="new_to_old":
                bucket="new_to_old_after_witness" if t>=7 else (
                    "new_to_old_switch_first" if t==6 else None)
            if bucket:
                pools[bucket].extend(squared(predicted))
            previous=(row,)
    return ({k:math.sqrt(math.fsum(v)/len(v)) for k,v in pools.items() if v},
            matched_gap,chosen)


class ComposedRetainedPublicTests(unittest.TestCase):
    def test_three_frozen_seed_composition_and_cold_retained_retrieval(self):
        records=[]
        for seed in SEEDS:
            old_pairs,new_fit,new_held,old_held,fifth_held,states=fixture(seed)
            start_fit=time.process_time()
            parent=train_old(old_pairs)
            original_parent=parent.checkpoint()
            learned,diagnostics=fit_constructed(new_fit)
            nine=fit_public_pairs(new_fit,None)
            matched=fit_batch(new_fit,learned.factor)
            full13=batch_full_13_effect(new_fit)
            conventional_selected=conventional_selection(new_fit[:36],new_fit[36:])
            learned_state=learned.checkpoint()
            archived=RetainedPublicLaws(parent,learned)
            cold=RetainedPublicLaws(parent,ComposedPublicEffect.restore(learned_state))
            fit_time=time.process_time()-start_fit
            self.assertEqual(parent.checkpoint(),original_parent)
            self.assertEqual(learned.seen,48)
            self.assertEqual(conventional_selected,learned.factor)
            self.assertEqual(cold.new_effect_checkpoint(),learned_state)
            start_score=time.process_time()
            native_new=effect_rmse(new_held,learned.effect)
            base_nine=effect_rmse(new_held,nine.effect)
            matched_error=effect_rmse(new_held,matched)
            full_error=effect_rmse(new_held,full13)
            fifth=effect_rmse(fifth_held,learned.effect)
            streams=held_episode_streams(seed,states)
            retrieval,gap,selected_heads=score_prequential(
                streams,archived,parent,matched)
            parent0gap=max(
                abs(archived.predict(z.observation,0)[k]-
                    parent.predict(z.observation,0)[k])
                for z,o in new_held for k in range(4))
            effect_gap=max(abs(learned.effect(z.observation)[k]-
                               matched(z.observation)[k])
                           for z,o in new_held for k in range(4))
            old_return=effect_rmse(old_held,lambda st: tuple(
                parent.predict(st,1)[k]-parent.predict(st,0)[k]
                for k in range(4)))
            old_return_when_new_forced=effect_rmse(old_held,learned.effect)
            # Same-process cold exact score output including old retrieval.
            cold_gap=max(
                abs(archived.predict(row.observation,1,()) [k]-
                    cold.predict(row.observation,1,())[k])
                for _,ep in streams for row,_ in ep for k in range(4))
            score_time=time.process_time()-start_score
            self.assertEqual(parent0gap,0.)
            self.assertEqual(cold_gap,0.)
            self.assertLessEqual(effect_gap,1e-8)
            self.assertLessEqual(gap,1e-8)
            self.assertEqual(archived.old_checkpoint_sha256,
                             hashlib.sha256(original_parent).hexdigest())
            self.assertNotIn("causal_gym",sys.modules)
            records.append({
                "seed":seed,"old_public_fit_actions":96,
                "new_public_fit_pairs":48,"inner_fit_pairs":36,
                "inner_select_pairs":12,"disjoint_held_states":48,
                "held_prequential_episodes":16,"held_steps_per_episode":12,
                "generated_extra_factor":learned.factor,
                "independent_conventional_factor":conventional_selected,
                "fit_inner_baseline_rmse":diagnostics["baseline_inner_rmse"],
                "fit_inner_best_rmse":diagnostics["best_inner_rmse"],
                "fit_inner_candidate_rmse":diagnostics["candidate_inner_rmse"],
                "held_new_effect_composed_rmse":native_new,
                "held_new_effect_nine_rmse":base_nine,
                "held_new_effect_matched_batch_rmse":matched_error,
                "held_new_effect_full13_batch_rmse":full_error,
                "held_unrepresented_fifth_rmse":fifth,
                "old_return_archived_effect_rmse":old_return,
                "old_return_forced_new_effect_rmse":old_return_when_new_forced,
                "retrieved_old_only_later_rmse":retrieval["old_only_later"],
                "retrieved_new_only_later_rmse":retrieval["new_only_later"],
                "retrieved_old_to_new_after_witness_rmse":
                    retrieval["old_to_new_after_witness"],
                "retrieved_new_to_old_after_witness_rmse":
                    retrieval["new_to_old_after_witness"],
                "old_to_new_switch_first_rmse":retrieval["old_to_new_switch_first"],
                "new_to_old_switch_first_rmse":retrieval["new_to_old_switch_first"],
                "old_only_first_rmse":retrieval["old_only_first"],
                "new_only_first_rmse":retrieval["new_only_first"],
                "retrieved_full_rmse":retrieval["retrieved_all"],
                "independent_conventional_retrieved_rmse":retrieval["conventional_all"],
                "fixed_always_old_rmse":retrieval["always_old_all"],
                "fixed_always_new_rmse":retrieval["always_new_all"],
                "unavailable_oracle_upper_rmse":retrieval["oracle_upper_all"],
                "selected_old_head_count":selected_heads["old"],
                "selected_new_head_count":selected_heads["new"],
                "matched_new_effect_max_gap":effect_gap,
                "matched_retrieval_max_gap":gap,
                "frozen_old_action0_max_gap":parent0gap,
                "cold_prediction_max_gap":cold_gap,
                "checkpoint_bytes":len(learned_state),
                "checkpoint_sha256":hashlib.sha256(learned_state).hexdigest(),
                "training_cpu_seconds":fit_time,
                "validation_cpu_seconds":score_time,
                "original_external_source_actions":0,
                "precommitted_composition_signal":(
                    learned.factor==3 and native_new<=.020
                    and base_nine-native_new>=.08
                    and effect_gap<=1e-8),
                "precommitted_retrieval_signal":all(
                    retrieval[k]<=.020 for k in (
                        "old_only_later","new_only_later",
                        "old_to_new_after_witness","new_to_old_after_witness")),
                "precommitted_fifth_transfer_signal":fifth<=.08
            })
        print("WSP168_FROZEN_COMPOSED_RETRIEVAL_RESULTS="+json.dumps(
            records,sort_keys=True,separators=(",",":")))

    def test_symbolic_multiplication_is_operator_not_prebaked_quartic(self):
        state=GRID[8]
        prior=prev_features(state,"s0*s1*s2")
        self.assertEqual(len(prior),9)
        self.assertEqual(len(constructed_features(state,None)),9)
        for factor in range(4):
            created=constructed_features(state,factor)
            self.assertEqual(created[-1],prior[-1]*prior[1+factor])
            self.assertEqual(created[:9],prior)
        with self.assertRaisesRegex(ValueError,"FACTOR_INVALID"):
            constructed_features(state,7)
        with self.assertRaisesRegex(ValueError,"FACTOR_INVALID"):
            constructed_features(state,True)

    def test_train_only_inner_selection_no_duplicate_future_or_private(self):
        prior,fit_pairs,held,_,_,_=fixture(SEEDS[0])
        model=fit_public_pairs(fit_pairs,None)
        self.assertEqual(model.seen,48)
        with self.assertRaisesRegex(ValueError,"INNER_SPLIT"):
            choose_composition(fit_pairs[:20],fit_pairs[36:])
        with self.assertRaisesRegex(ValueError,"FIT_DUPLICATE_STATE"):
            choose_composition(fit_pairs[:1]*36,fit_pairs[36:])
        with self.assertRaises(TypeError):
            model.observe_pair(*fit_pairs[0],future_target=3)
        zero,one=fit_pairs[0]
        with self.assertRaisesRegex(ValueError,"PAIR_ACTION_ORDER"):
            model.observe_pair(one,zero)
        with self.assertRaisesRegex(ValueError,"UNMATCHED_PUBLIC_STATE"):
            model.observe_pair(zero,fit_pairs[1][1])
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELD_SET"):
            PublicTransition.from_public(**{**zero.model_input(),"hidden_source_regime":1})

    def test_episodic_public_retrieval_no_hidden_regime_or_terminal_crossing(self):
        old_pairs,new_fit,held,_,_,states=fixture(SEEDS[1])
        parent=train_old(old_pairs)
        new,diag=fit_constructed(new_fit)
        model=RetainedPublicLaws(parent,new)
        episodes=held_episode_streams(SEEDS[1],states)
        row,mode=episodes[0][1][0]
        self.assertEqual(model.choose(()),"old")
        self.assertEqual(model.predict(row.observation,1,()),
                         parent.predict(row.observation,1))
        self.assertEqual(model.predict(row.observation,0,()),
                         parent.predict(row.observation,0))
        with self.assertRaisesRegex(ValueError,"PUBLIC_HISTORY_WINDOW"):
            model.predict(row.observation,1,(row,row))
        with self.assertRaisesRegex(ValueError,"HISTORY_PUBLIC_ONLY"):
            model.predict(row.observation,1,({"source_regime":"new"},))
        with self.assertRaisesRegex(ValueError,"EPISODE_RESET_REQUIRED"):
            terminal=episodes[0][1][-1][0]
            model.predict(row.observation,1,(terminal,))
        with self.assertRaises(TypeError):
            model.predict(row.observation,1,(),regime="new")
        with self.assertRaises(ValueError):
            model.predict([float("nan"),0,0,0],1,())
        with self.assertRaisesRegex(ValueError,"ACTION_INVALID"):
            model.predict(row.observation,2,())
        with self.assertRaisesRegex(ValueError,"ARCHIVED_PARENT_REQUIRED"):
            RetainedPublicLaws("not parent",new)

    def test_exact_cross_process_order_invariant_cold_and_tamper(self):
        old,new_fit,_,_,_,_=fixture(SEEDS[2])
        selected,diag=fit_constructed(new_fit)
        full=fit_public_pairs(new_fit,selected.factor)
        reversed_fit=fit_public_pairs(tuple(reversed(new_fit)),selected.factor)
        self.assertEqual(full.checkpoint(),reversed_fit.checkpoint())
        first=fit_public_pairs(new_fit[:22],selected.factor)
        cold=ComposedPublicEffect.restore(first.checkpoint())
        for zero,one in new_fit[22:]:
            first=first.observe_pair(zero,one)
            cold=cold.observe_pair(zero,one)
        self.assertEqual(first.checkpoint(),cold.checkpoint())
        self.assertEqual(first.checkpoint(),full.checkpoint())
        raw=full.checkpoint()
        snippet=(
            "import sys,hashlib;"
            "sys.path[:0]=[sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]];"
            "from composed_effects import ComposedPublicEffect;"
            "b=bytes.fromhex(sys.argv[6]);"
            "print(hashlib.sha256(ComposedPublicEffect.restore(b).checkpoint()).hexdigest())"
        )
        proc=subprocess.run(
            [sys.executable,"-B","-c",snippet,
             str(HERE/"WSP-159"),str(HERE/"WSP-160"),
             str(HERE/"WSP-166"),str(HERE/"WSP-167"),
             str(HERE/"WSP-168"),raw.hex()],
            capture_output=True,text=True,check=True,timeout=25)
        self.assertEqual(proc.stdout.strip(),hashlib.sha256(raw).hexdigest())
        for damaged in (raw[:-1],raw+b"x",b"FAIL"+raw[4:],
                        raw[:20]+bytes([raw[20]^1])+raw[21:],
                        "text",bytearray(raw)):
            with self.subTest(kind=str(type(damaged))):
                with self.assertRaises(ValueError):
                    ComposedPublicEffect.restore(damaged)
        obj=json.loads(raw[8:-32])
        obj["oracle_family"]="hidden"
        payload=json.dumps(obj,sort_keys=True,separators=(",",":")).encode("ascii")
        forged=MAGIC+len(payload).to_bytes(4,"big")+payload
        forged+=hashlib.sha256(forged).digest()
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_FIELDS"):
            ComposedPublicEffect.restore(forged)
        obj.pop("oracle_family")
        obj["w"][0][0]="2/4"
        payload=json.dumps(obj,sort_keys=True,separators=(",",":")).encode("ascii")
        forged=MAGIC+len(payload).to_bytes(4,"big")+payload
        forged+=hashlib.sha256(forged).digest()
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_FIELDS"):
            ComposedPublicEffect.restore(forged)

    def test_pair_cap_and_effect_empty(self):
        _,fit_pairs,_,_,_,_=fixture(SEEDS[0])
        m=fit_public_pairs(fit_pairs,3)
        full=ComposedPublicEffect._new(m.factor,m._weights,m._inverse,64)
        with self.assertRaisesRegex(ValueError,"PAIR_LIMIT"):
            full.observe_pair(*fit_pairs[0])
        self.assertEqual(ComposedPublicEffect.restore(full.checkpoint()).seen,64)
        with self.assertRaisesRegex(ValueError,"FACTOR_INVALID"):
            ComposedPublicEffect(-1)
        with self.assertRaises(ValueError):
            m.effect([float("inf"),0,0,0])


if __name__=="__main__":
    unittest.main()

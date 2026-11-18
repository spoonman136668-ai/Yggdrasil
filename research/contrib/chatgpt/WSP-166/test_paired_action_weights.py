"""WSP166 source-free matched-action causal effect development and negatives.

Only investigator-authored pure-dyadic 4D public transition observations.
The user-supplied source/original simulator is never imported or executed.
The learner is not passed private coefficients, paired-world identities, or
current held targets. Equal-info fully fitted controls are always compared.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import subprocess
import sys
import time
import unittest

HERE=Path(__file__).resolve().parents[1]
for directory in ("WSP-159","WSP-160"):
    sys.path.insert(0,str(HERE/directory))

from public_boundary import PublicTransition
from direct_weights import ProgrammedPublicDynamics
from test_direct_weights import solve_gaussian
from paired_action_weights import (
    ExactPairedActionEffect, public_effect_features, MAGIC, MAX_PAIRS)

SEEDS=(2663,2777,2887)
GRID=tuple(tuple(float(a) for a in values) for values in itertools.product(
    (-.75,-.25,.25,.75),(-1.,-.5,.5,1.),
    (-.5,-.25,.25,.5),(-.75,-.25,.25,.75)))
OLD_CONTRAST=(.03125,-.03125,.0625,-.015625)
BIAS=(.03125,-.0625,.09375,-.015625)
TRIPLE=(1.,-.75,.75,-.5)
COEFF=(
    (.25,.125,-.0625,.03125,-.03125,.375,.125,-.125),
    (-.1875,-.0625,.125,-.0625,.03125,-.25,-.125,.0625),
    (.125,.125,-.125,.0625,.0625,.25,.0625,-.1875),
    (-.125,-.125,.0625,-.03125,.0625,-.125,.125,.0625)
)


def old_action_zero(state):
    return tuple(
        state[k]+BIAS[k]+.125*state[k]+.0625*state[(k+1)%4]
        for k in range(4))


def new_contrast(state,seed):
    pos=SEEDS.index(seed)-1
    z=tuple(float(x) for x in public_effect_features(state))
    return tuple(sum(COEFF[k][j]*z[j] for j in range(8))
                 + (1 if k%2==0 else -1)*pos*.03125
                 for k in range(4))


def record(state,action,outcome):
    return PublicTransition.from_public(
        observation=state,action=action,next_observation=outcome,
        reward=1.,terminated=False,truncated=False)


def paired(state,seed,novel=True,triple=False):
    action0=old_action_zero(state)
    if novel:
        extra=new_contrast(state,seed)
    else:
        extra=OLD_CONTRAST
    if triple:
        influence=state[0]*state[1]*state[2]
        extra=tuple(extra[k]+TRIPLE[k]*influence for k in range(4))
    action1=tuple(action0[k]+extra[k] for k in range(4))
    return record(state,0,action0),record(state,1,action1)


def fixture(seed):
    rng=random.Random(seed)
    states=list(GRID)
    rng.shuffle(states)
    training=states[:48]
    validation=states[48:96]
    old_train=[paired(s,seed,novel=False) for s in training]
    novel_fit=[paired(s,seed,novel=True) for s in training]
    held=[paired(s,seed,novel=True) for s in validation]
    ood=[paired(s,seed,novel=True,triple=True) for s in validation]
    old_return=[paired(s,seed,novel=False) for s in validation]
    assert len(set(training)&set(validation))==0
    return old_train,novel_fit,held,ood,old_return


def train_old(pairs):
    m=ProgrammedPublicDynamics()
    for a,b in pairs:
        m=m.observe(a.observation,a.action,a.next_observation)
        m=m.observe(b.observation,b.action,b.next_observation)
    return m


def train_new(pairs):
    m=ExactPairedActionEffect()
    for a,b in pairs:
        m=m.observe_pair(a,b)
    return m


def fit_independent_contrast(pairs):
    # Conventional double-precision BATCH normal-equation ridge, completely
    # separate code path and no access to native covariance or weights.
    gram=[[float(i==j) for j in range(8)] for i in range(8)]
    rhs=[[0.]*4 for _ in range(8)]
    for a,b in pairs:
        z=tuple(float(x) for x in public_effect_features(a.observation))
        y=tuple(b.next_observation[k]-a.next_observation[k] for k in range(4))
        for i in range(8):
            for j in range(8):
                gram[i][j]+=z[i]*z[j]
            for k in range(4):
                rhs[i][k]+=z[i]*y[k]
    solved=tuple(solve_gaussian(gram,[rhs[i][k] for i in range(8)])
                 for k in range(4))
    def prediction(state):
        x=tuple(float(v) for v in public_effect_features(state))
        return tuple(math.fsum(solved[k][j]*x[j] for j in range(8))
                     for k in range(4))
    return prediction


def full_conventional_joint(pairs,with_action):
    # Fully fitted independent ordinary Gaussian-elimination ridge on the
    # same 96 NEW public FIT records. Feature dimension 16 if action-aware,
    # otherwise 8. Do NOT underspecify the strongest conventional control.
    n=16 if with_action else 8
    gram=[[float(i==j) for j in range(n)] for i in range(n)]
    rhs=[[0.]*4 for _ in range(n)]
    for a,b in pairs:
        for r in (a,b):
            q=tuple(float(v) for v in public_effect_features(r.observation))
            x=q+(tuple(q[j]*r.action for j in range(8))) if with_action else q
            y=tuple(r.next_observation[k]-r.observation[k] for k in range(4))
            for i in range(n):
                for j in range(n):
                    gram[i][j]+=x[i]*x[j]
                for k in range(4):
                    rhs[i][k]+=x[i]*y[k]
    weights=tuple(solve_gaussian(gram,[rhs[i][k] for i in range(n)])
                  for k in range(4))
    def predict(state,action):
        q=tuple(float(v) for v in public_effect_features(state))
        x=q+tuple(q[j]*action for j in range(8)) if with_action else q
        return tuple(state[k]+math.fsum(weights[k][j]*x[j] for j in range(n))
                     for k in range(4))
    return predict


def rmse(pairs,predict,action=None):
    squared=[]
    for a,b in pairs:
        for r in (a,b):
            if action is not None and action!=r.action:
                continue
            forecast=predict(r.observation,r.action)
            squared.extend((forecast[k]-r.next_observation[k])**2
                           for k in range(4))
    return math.sqrt(math.fsum(squared)/len(squared))


class PairedInterventionDevelopmentTests(unittest.TestCase):
    def test_frozen_three_seed_paired_effect_and_unsupported_structure(self):
        receipts=[]
        for seed in SEEDS:
            old,fit,held,ood,returning=fixture(seed)
            start=time.process_time()
            parent=train_old(old)
            original=parent.checkpoint()
            direct=train_new(fit)
            matched_effect=fit_independent_contrast(fit)
            full=full_conventional_joint(fit,True)
            erased=full_conventional_joint(fit,False)
            fit_seconds=time.process_time()-start
            self.assertEqual(parent.seen,96)
            self.assertEqual(direct.seen,48)
            self.assertEqual(parent.checkpoint(),original)
            cold=ExactPairedActionEffect.restore(direct.checkpoint())
            self.assertEqual(cold.checkpoint(),direct.checkpoint())
            def native(state,action):
                return direct.predict(parent,state,action)
            def matched(state,action):
                base0=parent.predict(state,0)
                if action==0:
                    return base0
                effect=matched_effect(state)
                return tuple(base0[k]+effect[k] for k in range(4))
            # Frozen parent used under unchanged historical source world.
            def old_parent(state,action):
                return parent.predict(state,action)
            start_score=time.process_time()
            native_a1=rmse(held,native,action=1)
            frozen_a1=rmse(held,old_parent,action=1)
            new_all=rmse(held,native)
            batch_a1=rmse(held,matched,action=1)
            joint_a1=rmse(held,full,action=1)
            erased_all=rmse(held,erased)
            novel_triple_a1=rmse(ood,native,action=1)
            old_return_native_a1=rmse(returning,native,action=1)
            old_return_base_a1=rmse(returning,old_parent,action=1)
            zero_drift=max(abs(native(a.observation,0)[k]-
                               old_parent(a.observation,0)[k])
                           for a,b in held for k in range(4))
            paired_gap=max(
                abs(direct.effect(a.observation)[k]-
                    matched_effect(a.observation)[k])
                for a,b in held for k in range(4))
            cold_gap=max(
                abs(native(a.observation,1)[k]-
                    cold.predict(parent,a.observation,1)[k])
                for a,b in held for k in range(4))
            score_seconds=time.process_time()-start_score
            self.assertEqual(zero_drift,0.)
            self.assertEqual(cold_gap,0.)
            self.assertLessEqual(paired_gap,1e-8)
            self.assertNotIn("causal_gym",sys.modules)
            receipts.append({
                "seed":seed,"old_parent_public_fit_actions":96,
                "new_public_fit_paired_states":48,
                "new_public_fit_actions":96,
                "unseen_public_valid_states":48,
                "unseen_public_valid_actions":96,
                "unexposed_triple_valid_states":48,
                "original_source_actions":0,
                "direct_paired_effect_test_rmse":native_a1,
                "frozen_parent_unadapted_action1_test_rmse":frozen_a1,
                "direct_new_both_actions_rmse":new_all,
                "independent_batch_paired_action1_rmse":batch_a1,
                "fully_fit_joint_action1_rmse":joint_a1,
                "action_erased_fully_fit_both_rmse":erased_all,
                "held_triple_unrepresented_action1_rmse":novel_triple_a1,
                "returning_old_family_frozen_action1_rmse":old_return_base_a1,
                "returning_old_family_new_action1_rmse":old_return_native_a1,
                "action0_parent_max_prediction_drift":zero_drift,
                "matched_batch_max_effect_gap":paired_gap,
                "same_host_cold_prediction_max_gap":cold_gap,
                "checkpoint_bytes":len(direct.checkpoint()),
                "checkpoint_sha256":hashlib.sha256(direct.checkpoint()).hexdigest(),
                "fit_cpu_seconds":fit_seconds,
                "scoring_cpu_seconds":score_seconds,
                "paired_development_success":(
                    native_a1<=.08 and frozen_a1-native_a1>=.10
                    and zero_drift==0. and paired_gap<=1e-8),
                "unexposed_triple_transfer_signal":novel_triple_a1<=.08
            })
        print("WSP166_FROZEN_PAIRED_RESULTS="+json.dumps(
            receipts,sort_keys=True,separators=(",",":")))

    def test_public_match_and_action_order_reject_unsafe_pairs(self):
        old,fit,held,ood,returning=fixture(SEEDS[0])
        a,b=fit[0]
        original=ExactPairedActionEffect()
        frozen=original.checkpoint()
        with self.assertRaisesRegex(ValueError,"PAIR_ACTION_ORDER"):
            original.observe_pair(b,a)
        with self.assertRaisesRegex(ValueError,"UNMATCHED_PUBLIC_STATE"):
            original.observe_pair(a,fit[1][1])
        with self.assertRaisesRegex(ValueError,"PUBLIC_PAIR_REQUIRED"):
            original.observe_pair({"action":0},b)
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELD_SET"):
            PublicTransition.from_public(**{
                **a.model_input(),"hidden_wind":.125})
        changed=PublicTransition.from_public(**{
            **b.model_input(),"reward":-1.})
        with self.assertRaisesRegex(ValueError,"PAIR_FLAGS_MISMATCH"):
            original.observe_pair(a,changed)
        with self.assertRaisesRegex(ValueError,"PREDICT_ACTION"):
            original.predict(train_old(old),a.observation,2)
        with self.assertRaisesRegex(ValueError,"PARENT_TYPE"):
            original.predict("no model",a.observation,0)
        with self.assertRaises(TypeError):
            original.observe_pair(a,b,source_oracle=True)
        self.assertEqual(original.checkpoint(),frozen)

    def test_exact_order_invariance_and_cold_continuation(self):
        old,pairs,held,_,_=fixture(SEEDS[1])
        first=train_new(pairs)
        reverse=train_new(list(reversed(pairs)))
        self.assertEqual(first.checkpoint(),reverse.checkpoint())
        partial=train_new(pairs[:27])
        cold=ExactPairedActionEffect.restore(partial.checkpoint())
        for a,b in pairs[27:]:
            partial=partial.observe_pair(a,b)
            cold=cold.observe_pair(a,b)
        self.assertEqual(partial.checkpoint(),cold.checkpoint())
        self.assertEqual(cold.checkpoint(),first.checkpoint())

    def test_external_cold_process_and_checksum_negative(self):
        old,fit,_,_,_=fixture(SEEDS[2])
        program=train_new(fit)
        raw=program.checkpoint()
        # A separate Python interpreter uses the snapshot without FIT data.
        snippet=(
            "import sys,hashlib;"
            "sys.path.insert(0,sys.argv[1]);"
            "sys.path.insert(0,sys.argv[2]);"
            "sys.path.insert(0,sys.argv[3]);"
            "from paired_action_weights import ExactPairedActionEffect;"
            "blob=bytes.fromhex(sys.argv[4]);"
            "m=ExactPairedActionEffect.restore(blob);"
            "print(hashlib.sha256(m.checkpoint()).hexdigest())"
        )
        run=subprocess.run(
            [sys.executable,"-B","-c",snippet,
             str(HERE/"WSP-159"),str(HERE/"WSP-160"),
             str(HERE/"WSP-166"),raw.hex()],
            capture_output=True,text=True,check=True,timeout=20)
        self.assertEqual(run.stdout.strip(),hashlib.sha256(raw).hexdigest())
        self.assertEqual(run.stderr.strip(),"")
        for damaged in (raw[:-1],raw+b"x",b"FAKE"+raw[4:],
                        raw[:20]+bytes([raw[20]^1])+raw[21:],
                        "string",bytearray(raw)):
            with self.subTest(kind=str(type(damaged))):
                with self.assertRaises(ValueError):
                    ExactPairedActionEffect.restore(damaged)
        obj=json.loads(raw[8:-32])
        obj["source_hidden_regime"]=7
        payload=json.dumps(obj,sort_keys=True,separators=(",",":")).encode("ascii")
        signed=MAGIC+len(payload).to_bytes(4,"big")+payload
        signed+=hashlib.sha256(signed).digest()
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_FIELDS"):
            ExactPairedActionEffect.restore(signed)
        obj.pop("source_hidden_regime")
        obj["w"][0][0]="2/4"  # correct SHA does not permit uncanonical ratio
        payload=json.dumps(obj,sort_keys=True,separators=(",",":")).encode("ascii")
        signed=MAGIC+len(payload).to_bytes(4,"big")+payload
        signed+=hashlib.sha256(signed).digest()
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_FIELDS"):
            ExactPairedActionEffect.restore(signed)

    def test_exact_budget_and_bad_public_numeric(self):
        old,fit,held,_,_=fixture(SEEDS[0])
        program=train_new(fit)
        a,b=fit[0]
        full=ExactPairedActionEffect._new(
            program._weights,program._inverse,MAX_PAIRS)
        with self.assertRaisesRegex(ValueError,"PAIR_LIMIT"):
            full.observe_pair(a,b)
        with self.assertRaises(ValueError):
            program.effect([math.inf,0.,0.,0.])
        with self.assertRaises(ValueError):
            program.effect([0.,0.,0.])
        with self.assertRaises(TypeError):
            program.predict(train_old(old),a.observation,0,hidden_family=1)
        self.assertEqual(ExactPairedActionEffect.restore(
            full.checkpoint()).seen,MAX_PAIRS)


if __name__=="__main__":
    unittest.main()

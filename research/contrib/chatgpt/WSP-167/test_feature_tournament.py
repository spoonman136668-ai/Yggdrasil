"""WSP167: frozen three-seed public action-consequence feature tournament.

Training-only feature choice, disjoint held public states; all matched
intervention pairs are authored synthetic data, not external CausalGym
simulator reset/do calls, and not proof of new-grammar invention.
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
for name in ("WSP-159","WSP-160","WSP-166"):
    sys.path.insert(0,str(HERE/name))

from public_boundary import PublicTransition
from direct_weights import ProgrammedPublicDynamics
from paired_action_weights import ExactPairedActionEffect
from test_paired_action_weights import (
    GRID, COEFF, OLD_CONTRAST, TRIPLE, old_action_zero, record,
    train_old, train_new
)
from test_direct_weights import solve_gaussian
from feature_tournament import (
    CANDIDATES, SelectedPublicEffect, fit_selected, fit, select_feature,
    features, MAGIC, MAX_PAIRS
)

SEEDS=(3001,3119,3229)
RIDGE=1./64
QUARTIC_AMPLITUDE=4.


def public_pair(state,seed,new_triple=False,quartic=False):
    old0=old_action_zero(state)
    if new_triple:
        z=tuple(float(x) for x in features(state,None))
        shift=SEEDS.index(seed)-1
        triple=state[0]*state[1]*state[2]
        effect=tuple(
            math.fsum(COEFF[k][j]*z[j] for j in range(8)) +
            (shift/32 if k%2==0 else -shift/32) +
            TRIPLE[k]*triple
            for k in range(4))
    else:
        effect=OLD_CONTRAST
    if quartic:
        x=QUARTIC_AMPLITUDE*state[0]*state[1]*state[2]*state[3]
        effect=tuple(effect[k]+TRIPLE[k]*x for k in range(4))
    old1=tuple(old0[k]+effect[k] for k in range(4))
    return record(state,0,old0),record(state,1,old1)


def fixtures(seed):
    states=list(GRID)
    random.Random(seed).shuffle(states)
    train,valid=states[:48],states[48:96]
    assert len(set(train)&set(valid))==0
    prior=[public_pair(s,seed) for s in train]
    fit_pairs=[public_pair(s,seed,new_triple=True) for s in train]
    held=[public_pair(s,seed,new_triple=True) for s in valid]
    quartic=[public_pair(s,seed,new_triple=True,quartic=True) for s in valid]
    returning=[public_pair(s,seed) for s in valid]
    return prior,fit_pairs,held,quartic,returning


def batch_conventional(pairs,candidate):
    """Independent fully FIT double precision normal-equation Gaussian ridge.

    Does NOT read direct-trained weights, covariance, selected candidate,
    checkpoint or original-world author coefficients. Candidate supplied
    by prereg hypothesis selector or independent conventional selector.
    """
    width=8+int(candidate is not None)
    gram=[[float(i==j)*RIDGE for j in range(width)] for i in range(width)]
    rhs=[[0.]*4 for _ in range(width)]
    for zero,one in pairs:
        if zero.action!=0 or one.action!=1 or zero.observation!=one.observation:
            raise ValueError("WSP167_BATCH_PAIR_REQUIRED")
        x=tuple(float(z) for z in features(zero.observation,candidate))
        target=tuple(one.next_observation[k]-zero.next_observation[k]
                     for k in range(4))
        for i in range(width):
            for j in range(width):
                gram[i][j]+=x[i]*x[j]
            for k in range(4):
                rhs[i][k]+=x[i]*target[k]
    weights=tuple(solve_gaussian(gram,[rhs[i][k] for i in range(width)])
                  for k in range(4))
    def forecast(state):
        x=tuple(float(z) for z in features(state,candidate))
        return tuple(math.fsum(weights[k][j]*x[j] for j in range(width))
                     for k in range(4))
    return forecast


def full_15_conventional(pairs):
    """Stronger fully fitted conventional 8-base+7-candidates ridge."""
    allnames=CANDIDATES
    width=15
    gram=[[float(i==j)*RIDGE for j in range(width)] for i in range(width)]
    rhs=[[0.]*4 for _ in range(width)]
    def augmented(state):
        basic=tuple(float(x) for x in features(state,None))
        return basic+tuple(float(features(state,key)[-1]) for key in allnames)
    for zero,one in pairs:
        x=augmented(zero.observation)
        target=tuple(one.next_observation[k]-zero.next_observation[k]
                     for k in range(4))
        for i in range(width):
            for j in range(width):
                gram[i][j]+=x[i]*x[j]
            for k in range(4):
                rhs[i][k]+=x[i]*target[k]
    weights=tuple(solve_gaussian(gram,[rhs[i][k] for i in range(width)])
                  for k in range(4))
    def predict(state):
        x=augmented(state)
        return tuple(math.fsum(weights[k][j]*x[j] for j in range(width))
                     for k in range(4))
    return predict


def contrast_rmse(pairs,predict):
    error=[]
    for zero,one in pairs:
        guess=predict(zero.observation)
        diff=tuple(one.next_observation[k]-zero.next_observation[k]
                   for k in range(4))
        error.extend((guess[k]-diff[k])**2 for k in range(4))
    return math.sqrt(math.fsum(error)/len(error))


def consequence_rmse(pairs,predict,action=1):
    error=[]
    for zero,one in pairs:
        row=one if action==1 else zero
        guess=predict(row.observation,row.action)
        error.extend((guess[k]-row.next_observation[k])**2 for k in range(4))
    return math.sqrt(math.fsum(error)/len(error))


def conventional_select(training36,selection12):
    """Independently refit conventional batch model for all hypotheses."""
    null=contrast_rmse(selection12,batch_conventional(training36,None))
    scores={name:contrast_rmse(
        selection12,batch_conventional(training36,name))
        for name in CANDIDATES}
    winner=min(CANDIDATES,key=lambda k:(scores[k],CANDIDATES.index(k)))
    return winner if null-scores[winner]>=.003 else None


class FrozenFeatureTournamentTests(unittest.TestCase):

    def test_three_seed_frozen_selection_conventional_and_hard_ood(self):
        receipts=[]
        for seed in SEEDS:
            prior,fit_pairs,held,quartic,old_return=fixtures(seed)
            t0=time.process_time()
            parent=train_old(prior)
            old_custody=parent.checkpoint()
            selected,inner=fit_selected(fit_pairs)
            small_8=fit(fit_pairs,None)
            previous_8=train_new(fit_pairs)
            selected_batch=batch_conventional(fit_pairs,selected.candidate)
            full15=full_15_conventional(fit_pairs)
            conventional_choice=conventional_select(
                fit_pairs[:36],fit_pairs[36:])
            fit_seconds=time.process_time()-t0
            self.assertEqual(parent.checkpoint(),old_custody)
            self.assertEqual(selected.seen,48)
            self.assertEqual(small_8.seen,48)
            self.assertEqual(selected.candidate,conventional_choice)
            cold=SelectedPublicEffect.restore(selected.checkpoint())
            self.assertEqual(cold.checkpoint(),selected.checkpoint())
            def direct(state,action):
                return selected.predict(parent,state,action)
            def eight(state,action):
                if action==0:
                    return parent.predict(state,0)
                effect=small_8.effect(state)
                old0=parent.predict(state,0)
                return tuple(old0[k]+effect[k] for k in range(4))
            def old8(state,action):
                return previous_8.predict(parent,state,action)
            def conventional(state,action):
                if action==0:
                    return parent.predict(state,0)
                base=parent.predict(state,0)
                effect=selected_batch(state)
                return tuple(base[k]+effect[k] for k in range(4))
            def full_conventional(state,action):
                if action==0:
                    return parent.predict(state,0)
                base=parent.predict(state,0)
                effect=full15(state)
                return tuple(base[k]+effect[k] for k in range(4))
            t1=time.process_time()
            native=consequence_rmse(held,direct)
            base8=consequence_rmse(held,eight)
            old8score=consequence_rmse(held,old8)
            parent_old=consequence_rmse(held,parent.predict)
            match=consequence_rmse(held,conventional)
            fullscore=consequence_rmse(held,full_conventional)
            hardscore=consequence_rmse(quartic,direct)
            original_old=consequence_rmse(old_return,parent.predict)
            return_new=consequence_rmse(old_return,direct)
            no_edit=max(abs(
                direct(zero.observation,0)[k]-
                parent.predict(zero.observation,0)[k])
                for zero,one in held for k in range(4))
            parity=max(abs(selected.effect(zero.observation)[k]-
                           selected_batch(zero.observation)[k])
                       for zero,one in held for k in range(4))
            coldgap=max(abs(direct(zero.observation,1)[k]-
                            cold.predict(parent,zero.observation,1)[k])
                        for zero,one in held for k in range(4))
            valid_seconds=time.process_time()-t1
            self.assertEqual(no_edit,0.)
            self.assertEqual(coldgap,0.)
            self.assertLessEqual(parity,1e-8)
            self.assertNotIn("causal_gym",sys.modules)
            receipts.append({
                "seed":seed,
                "unique_public_fit_states":48,
                "inner_fit_states":36,
                "internal_selection_states":12,
                "disjoint_held_states":48,
                "new_source_held_action_records":96,
                "selected_feature":selected.candidate,
                "independent_conventional_selected_feature":conventional_choice,
                "internal_null_effect_rmse":inner["null_inner_rmse"],
                "internal_best_effect_rmse":inner["selected_inner_rmse"],
                "internal_candidate_rmse":inner["all_candidate_inner_rmse"],
                "new_action1_selected_rmse":native,
                "new_action1_same_ridge_eight_rmse":base8,
                "new_action1_wsp166_lambda1_rmse":old8score,
                "new_action1_frozen_parent_rmse":parent_old,
                "new_action1_independent_batch_selected_rmse":match,
                "new_action1_full15_conventional_rmse":fullscore,
                "new_action1_unrepresented_degree4_rmse":hardscore,
                "old_return_original_action1_rmse":original_old,
                "old_return_selected_action1_rmse":return_new,
                "protected_action0_max_drift":no_edit,
                "independent_batch_max_effect_gap":parity,
                "cold_prediction_max_gap":coldgap,
                "effect_checkpoint_bytes":len(selected.checkpoint()),
                "effect_checkpoint_sha256":hashlib.sha256(
                    selected.checkpoint()).hexdigest(),
                "fit_cpu_seconds":fit_seconds,
                "valid_cpu_seconds":valid_seconds,
                "original_external_source_actions":0,
                "frozen_development_feature_signal":(
                    selected.candidate=="s0*s1*s2" and native<=.055
                    and base8-native>=.035 and no_edit==0.
                    and parity<=1e-8),
                "frozen_degree4_transfer_signal":hardscore<=.08,
                "return_old_family_action1_retained":return_new<=original_old+.01
            })
        print("WSP167_FROZEN_FEATURE_RESULTS="+json.dumps(
            receipts,sort_keys=True,separators=(",",":")))

    def test_null_feature_grammar_and_train_only_selection(self):
        seed=SEEDS[0]
        _,fit_pairs,held,_,_=fixtures(seed)
        # The sourcefree old-family exact public effects have no new triple.
        prior=[public_pair(pair[0].observation,seed,new_triple=False)
               for pair in fit_pairs]
        choice,diagnostic=select_feature(prior[:36],prior[36:])
        self.assertGreaterEqual(diagnostic["null_inner_rmse"],0.)
        self.assertIn(choice,(None,)+CANDIDATES)
        with self.assertRaisesRegex(ValueError,"INNER_SPLIT"):
            select_feature(fit_pairs[:34],fit_pairs[36:])
        with self.assertRaisesRegex(ValueError,"DUPLICATE_PUBLIC_FIT"):
            select_feature([fit_pairs[0]]*36,fit_pairs[36:])
        self.assertEqual(len(fit_pairs),48)
        self.assertEqual(len(held),48)

    def test_public_action_pair_and_private_field_fail_closed(self):
        _,fit_pairs,_,_,_=fixtures(SEEDS[1])
        zero,one=fit_pairs[0]
        model=SelectedPublicEffect("s0*s1*s2")
        pristine=model.checkpoint()
        with self.assertRaisesRegex(ValueError,"PAIR_ACTION_ORDER"):
            model.observe_pair(one,zero)
        with self.assertRaisesRegex(ValueError,"UNMATCHED_PUBLIC_STATE"):
            model.observe_pair(zero,fit_pairs[1][1])
        with self.assertRaisesRegex(ValueError,"PUBLIC_PAIR_REQUIRED"):
            model.observe_pair({"secret":1},one)
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELD_SET"):
            PublicTransition.from_public(**{
                **zero.model_input(),"source_wind":.1})
        with self.assertRaisesRegex(ValueError,"ACTION_INVALID"):
            model.predict(train_old(fixtures(SEEDS[1])[0]),
                          zero.observation,2)
        with self.assertRaises(TypeError):
            model.observe_pair(zero,one,hidden_regime=1)
        with self.assertRaisesRegex(ValueError,"WSP167_CANDIDATE"):
            SelectedPublicEffect("secret-triple-source")
        self.assertEqual(pristine,model.checkpoint())

    def test_exact_pair_order_invariance_budget_and_cold_continuation(self):
        _,pairs,held,_,_=fixtures(SEEDS[2])
        model=fit(pairs,"s0*s1*s2")
        reversed_model=fit(tuple(reversed(pairs)),"s0*s1*s2")
        self.assertEqual(model.checkpoint(),reversed_model.checkpoint())
        prefix=fit(pairs[:23],"s0*s1*s2")
        cold=SelectedPublicEffect.restore(prefix.checkpoint())
        for zero,one in pairs[23:]:
            prefix=prefix.observe_pair(zero,one)
            cold=cold.observe_pair(zero,one)
        self.assertEqual(prefix.checkpoint(),cold.checkpoint())
        self.assertEqual(prefix.checkpoint(),model.checkpoint())
        maxed=SelectedPublicEffect._new(
            model._candidate,model._weights,model._inverse,MAX_PAIRS)
        with self.assertRaisesRegex(ValueError,"PAIR_LIMIT"):
            maxed.observe_pair(*pairs[0])

    def test_independent_process_and_canonical_integrity(self):
        _,fit_pairs,_,_,_=fixtures(SEEDS[0])
        model,_=fit_selected(fit_pairs)
        wire=model.checkpoint()
        snippet=(
            "import sys,hashlib;"
            "sys.path[:0]=[sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]];"
            "from feature_tournament import SelectedPublicEffect;"
            "raw=bytes.fromhex(sys.argv[5]);"
            "model=SelectedPublicEffect.restore(raw);"
            "print(hashlib.sha256(model.checkpoint()).hexdigest())"
        )
        check=subprocess.run(
            [sys.executable,"-B","-c",snippet,
             str(HERE/"WSP-159"),str(HERE/"WSP-160"),
             str(HERE/"WSP-166"),str(HERE/"WSP-167"),wire.hex()],
            capture_output=True,text=True,check=True,timeout=25)
        self.assertEqual(check.stdout.strip(),hashlib.sha256(wire).hexdigest())
        self.assertEqual(check.stderr.strip(),"")
        for bad in (wire[:-1],wire+b"x",b"NOPE"+wire[4:],
                    wire[:16]+bytes([wire[16]^1])+wire[17:],
                    "wrong",bytearray(wire)):
            with self.subTest(kind=str(type(bad))):
                with self.assertRaises(ValueError):
                    SelectedPublicEffect.restore(bad)
        obj=json.loads(wire[8:-32])
        obj["hidden_original_source"]="private"
        raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode("ascii")
        forged=MAGIC+len(raw).to_bytes(4,"big")+raw
        forged+=hashlib.sha256(forged).digest()
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_FIELDS"):
            SelectedPublicEffect.restore(forged)
        obj.pop("hidden_original_source")
        obj["weights"][0][0]="2/4"
        raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode("ascii")
        forged=MAGIC+len(raw).to_bytes(4,"big")+raw
        forged+=hashlib.sha256(forged).digest()
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_FIELDS"):
            SelectedPublicEffect.restore(forged)


if __name__=="__main__":
    unittest.main()

"""WSP-164: frozen source-free reliability-gated history training.

No protected original source, hidden regime input or current outcome leakage.
Conventional Bayesian two-mode and prior un-gated learned RLS are controls.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import random
import sys
import time
import unittest

HERE=Path(__file__).resolve().parents[1]
for p in ("WSP-159","WSP-160","WSP-161","WSP-162","WSP-163"):
    sys.path.insert(0,str(HERE/p))

from public_boundary import PublicTransition
from history_weights import PublicHistoryWeights
from test_history_weights import fixtures, fit_static, fit_memory, public_residual
from reliability_gate import ReliablePublicHistory, fit_public_threshold, MAGIC

SEEDS=(1931,2053,2179)
FIT_EPISODES=32
VALID_EPISODES=16
STEPS=16


def dot(a,b):
    return math.fsum(x*y for x,y in zip(a,b))


class FittedBayesianPersistence:
    """Conventional two-mode Bayesian persistence-vs-iid mixture control.

    Prototypes and within-episode mode-stay rate are estimated from the SAME
    public FIT source used by direct-weight programs; two modes inferred by
    sign of a public residual coordinate, not a source-provided family label.
    Mixture prior 1/2 persistent vs 1/2 iid, and iid stay prior 1/2.
    The model never sees any current held target at prediction.
    """
    def __init__(self,base,fit_episodes):
        self.base=base
        pos=[]
        neg=[]
        same=0
        count=0
        for ep in fit_episodes:
            previous=None
            for row in ep:
                residual=public_residual(base,row)
                sign=1 if residual[0]>=0 else -1
                (pos if sign==1 else neg).append(residual)
                if previous is not None:
                    same+=int(sign==previous)
                    count+=1
                previous=sign
        if not pos or not neg or count!=480:
            raise ValueError("WSP164_BAYES_FIT_INVALID")
        mean_pos=[math.fsum(r[k] for r in pos)/len(pos) for k in range(4)]
        mean_neg=[math.fsum(r[k] for r in neg)/len(neg) for k in range(4)]
        self.center=tuple((mean_pos[k]+mean_neg[k])/2 for k in range(4))
        self.amp=tuple((mean_pos[k]-mean_neg[k])/2 for k in range(4))
        self.stay=max(.51,min(.99,(same+1)/(count+2)))

    def predict(self,state,action,history):
        base=self.base.predict(state,action)
        if not history:
            return base
        if any(type(x) is not PublicTransition or x.terminated or x.truncated
               for x in history):
            raise ValueError("WSP164_BAYES_EPISODE_RESET")
        signs=[1 if public_residual(self.base,r)[0]>=self.center[0] else -1
               for r in history]
        log_odds=0.
        for a,b in zip(signs[:-1],signs[1:]):
            chance=self.stay if a==b else 1-self.stay
            log_odds+=math.log(chance/.5)
        if log_odds>=0:
            p=1./(1.+math.exp(-log_odds))
        else:
            e=math.exp(log_odds)
            p=e/(1.+e)
        expected=(2*self.stay-1)*p*signs[-1]
        return tuple(base[k]+self.center[k]+expected*self.amp[k]
                     for k in range(4))


def rmse(values):
    return math.sqrt(math.fsum(values)/len(values))


def evaluate(episodes,gate,program,static,bayes,random_history_pool,seed):
    random_draw=random.Random(seed)
    result={name:[] for name in ("static_all","gated_all",
        "static_later","gated_later","ungated_later","bayes_later",
        "carry_later","shuffle_later","static_first","gated_first")}
    num_on=0
    num_later=0
    for ep in episodes:
        history=[]
        for row in ep:
            prior=history[-5:]
            state,action=row.observation,row.action
            target=row.next_observation
            a=static.predict(state,action)
            b=gate.predict(state,action,prior)
            if not history and a!=b:
                raise AssertionError("WSP164_FUTURE_LEAK_FIRST")
            v=program.predict(state,action,history[-1] if history else None)
            control=bayes.predict(state,action,history)
            shuffled=gate.predict(state,action,
                                  random_draw.sample(random_history_pool,5)
                                  if history else [])
            for k in range(4):
                result["static_all"].append((a[k]-target[k])**2)
                result["gated_all"].append((b[k]-target[k])**2)
            if history:
                num_later+=1
                num_on+=int(gate.permitted(prior))
                prevres=public_residual(static,history[-1])
                carried=tuple(a[k]+prevres[k] for k in range(4))
                for k in range(4):
                    result["static_later"].append((a[k]-target[k])**2)
                    result["gated_later"].append((b[k]-target[k])**2)
                    result["ungated_later"].append((v[k]-target[k])**2)
                    result["bayes_later"].append((control[k]-target[k])**2)
                    result["carry_later"].append((carried[k]-target[k])**2)
                    result["shuffle_later"].append((shuffled[k]-target[k])**2)
            else:
                for k in range(4):
                    result["static_first"].append((a[k]-target[k])**2)
                    result["gated_first"].append((b[k]-target[k])**2)
            history.append(row)
    return {k:rmse(v) for k,v in result.items() if v} | {
        "gate_fraction_later":num_on/num_later,
        "gate_count":num_on
    }


class ReliabilityGateTests(unittest.TestCase):
    def test_three_frozen_sourcefree_replica_and_strong_controls(self):
        receipts=[]
        for seed in SEEDS:
            fit,valid,iid=fixtures(seed)
            start_fit=time.process_time()
            base=fit_static(fit)
            prior=fit_memory(base,fit)
            gate=ReliablePublicHistory.from_fit(prior,fit)
            bayes=FittedBayesianPersistence(base,fit)
            train_cpu=time.process_time()-start_fit
            raw=gate.checkpoint()
            cold=ReliablePublicHistory.restore(raw)
            self.assertEqual(cold.checkpoint(),raw)
            self.assertEqual(cold.threshold,gate.threshold)
            fit_pool=[r for ep in fit for r in ep if not (r.terminated or r.truncated)]
            start_valid=time.process_time()
            persistent=evaluate(valid,gate,prior,base,bayes,fit_pool,seed+2777)
            iid_result=evaluate(iid,gate,prior,base,bayes,fit_pool,seed+3777)
            eval_cpu=time.process_time()-start_valid
            persistent_improve=persistent["static_later"]-persistent["gated_later"]
            iid_regret=iid_result["gated_later"]-iid_result["static_later"]
            orig_iid_regret=iid_result["ungated_later"]-iid_result["static_later"]
            self.assertGreaterEqual(persistent_improve,.04)
            self.assertLessEqual(iid_regret,.01)
            self.assertGreaterEqual(orig_iid_regret,.01)
            self.assertEqual(persistent["static_first"],persistent["gated_first"])
            self.assertEqual(iid_result["static_first"],iid_result["gated_first"])
            self.assertGreater(persistent["shuffle_later"],persistent["gated_later"])
            self.assertGreater(persistent["gate_fraction_later"],.3)
            self.assertLess(iid_result["gate_fraction_later"],.25)
            maxcold=0.
            for ep in valid:
                history=[]
                for r in ep:
                    a=gate.predict(r.observation,r.action,history[-5:])
                    b=cold.predict(r.observation,r.action,history[-5:])
                    maxcold=max(maxcold,max(abs(x-y) for x,y in zip(a,b)))
                    history.append(r)
            self.assertEqual(maxcold,0.)
            receipts.append({
                "seed":seed,"fit_episodes":32,"fit_public_rows":512,
                "fit_public_history_pairs":480,
                "valid_episodes":16,"iid_episodes":16,"episode_steps":16,
                "learned_gate_threshold":gate.threshold,
                "fitted_bayesian_stay":bayes.stay,
                "persistent_static_later_rmse":persistent["static_later"],
                "persistent_ungated_later_rmse":persistent["ungated_later"],
                "persistent_gated_later_rmse":persistent["gated_later"],
                "persistent_bayes_later_rmse":persistent["bayes_later"],
                "persistent_carry_later_rmse":persistent["carry_later"],
                "persistent_shuffle_later_rmse":persistent["shuffle_later"],
                "persistent_improvement":persistent_improve,
                "persistent_gated_on_fraction":persistent["gate_fraction_later"],
                "iid_static_later_rmse":iid_result["static_later"],
                "iid_ungated_later_rmse":iid_result["ungated_later"],
                "iid_gated_later_rmse":iid_result["gated_later"],
                "iid_bayes_later_rmse":iid_result["bayes_later"],
                "iid_gated_regret":iid_regret,
                "iid_ungated_regret":orig_iid_regret,
                "iid_gated_on_fraction":iid_result["gate_fraction_later"],
                "first_step_absolute_error_gap":abs(
                    persistent["static_first"]-persistent["gated_first"]),
                "same_os_cold_prediction_max_gap":maxcold,
                "checkpoint_bytes":len(raw),
                "checkpoint_sha256":hashlib.sha256(raw).hexdigest(),
                "fit_cpu_seconds":train_cpu,
                "validate_cpu_seconds":eval_cpu,
                "original_source_actions":0
            })
        self.assertNotIn("causal_gym",sys.modules)
        print("WSP164_FROZEN_SOURCEFREE_RESULTS="+json.dumps(
            receipts,sort_keys=True,separators=(",",":")))

    def test_gate_requires_five_prior_public_outcomes_and_resets(self):
        fit,valid,_=fixtures(1931)
        base=fit_static(fit)
        prior=fit_memory(base,fit)
        gate=ReliablePublicHistory.from_fit(prior,fit)
        row=valid[0][0]
        self.assertFalse(gate.permitted([]))
        for n in range(1,5):
            self.assertFalse(gate.permitted(list(valid[0][:n])))
            self.assertEqual(
                gate.predict(row.observation,row.action,list(valid[0][:n])),
                base.predict(row.observation,row.action))
        self.assertTrue(.75<=gate.threshold<=.86)
        with self.assertRaisesRegex(ValueError,"EPISODE_HISTORY_RESET"):
            gate.predict(row.observation,row.action,list(valid[0][-5:]))
        for bad in ("hidden source",{"regime":1},object()):
            with self.assertRaisesRegex(ValueError,"PUBLIC_HISTORY_ONLY"):
                gate.predict(row.observation,row.action,[bad])
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELD_SET"):
            PublicTransition.from_public(**{**row.model_input(),"regime_id":1})
        with self.assertRaises(ValueError):
            gate.predict([float("nan"),0,0,0],1,[])
        with self.assertRaises(ValueError):
            gate.predict(row.observation,2,[])

    def test_gate_does_not_accept_current_future_outcome(self):
        fit,valid,_=fixtures(1931)
        gate=ReliablePublicHistory.from_fit(fit_memory(fit_static(fit),fit),fit)
        row=valid[0][0]
        frozen=gate.checkpoint()
        with self.assertRaises(TypeError):
            gate.predict(row.observation,row.action,[],future_target=row.next_observation)
        with self.assertRaises(TypeError):
            gate.predict(row.observation,row.action,[],hidden_regime=1)
        self.assertEqual(frozen,gate.checkpoint())

    def test_same_host_cold_integrity_and_negative_private_poison(self):
        fit,_,_=fixtures(2053)
        gate=ReliablePublicHistory.from_fit(fit_memory(fit_static(fit),fit),fit)
        frozen=gate.checkpoint()
        self.assertEqual(ReliablePublicHistory.restore(frozen).checkpoint(),frozen)
        for bad in (frozen[:-1],frozen+b"a",b"BORK"+frozen[4:],
                    frozen[:15]+bytes([frozen[15]^1])+frozen[16:],
                    "string",bytearray(frozen)):
            with self.subTest(kind=str(type(bad))):
                with self.assertRaises(ValueError):
                    ReliablePublicHistory.restore(bad)
        data=json.loads(frozen[8:-32])
        data["hidden_source_regime"]=0
        wire=json.dumps(data,sort_keys=True,separators=(",",":")).encode("ascii")
        wire=MAGIC+len(wire).to_bytes(4,"big")+wire
        wire+=hashlib.sha256(wire).digest()
        with self.assertRaisesRegex(ValueError,"FIELDS"):
            ReliablePublicHistory.restore(wire)

    def test_frozen_fit_only_threshold_and_source_boundaries(self):
        fit,valid,_=fixtures(2179)
        program=fit_memory(fit_static(fit),fit)
        first=fit_public_threshold(program,fit)
        self.assertEqual(first,fit_public_threshold(program,fit))
        with self.assertRaisesRegex(ValueError,"FIT_EPISODE_COUNT"):
            fit_public_threshold(program,fit[:1])
        with self.assertRaisesRegex(ValueError,"FIT_EPISODE_SHAPE"):
            fit_public_threshold(program,[tuple(x[:2]) for x in fit])
        with self.assertRaisesRegex(ValueError,"PROGRAM_TYPE"):
            fit_public_threshold("not a model",fit)
        with self.assertRaisesRegex(ValueError,"THRESHOLD_INVALID"):
            ReliablePublicHistory(program,1.)
        self.assertEqual(program.seen,480)
        self.assertEqual(program._base.seen,512)


if __name__=="__main__":
    unittest.main()

"""WSP-163 frozen source-free 4D continuous public-history weight experiments.

All data are investigator-authored. Models see public records and past
consequences only, never the generator's latent regime or future feedback.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import sys
import time
import unittest

HERE=Path(__file__).resolve().parents[1]
for p in ("WSP-159","WSP-160","WSP-162"):
    sys.path.insert(0,str(HERE/p))

from public_boundary import PublicTransition
from direct_weights import ProgrammedPublicDynamics
from test_direct_weights import solve_gaussian
from test_overlap_certificate import old_target
from history_weights import PublicHistoryWeights, MAGIC

SHIFT=(.20,-.15,.10,-.05)
SEEDS=(1631,1741,1867)
EPISODE_LEN=16
NOISE_SIGMA=.02
CONTEXTS=[
    (tuple(float(x) for x in (*corner,0.0)),a)
    for corner in itertools.product((-.75,.75),(-.5,.5),(-.4,.4))
    for a in (0,1)
]


def fixtures(seed):
    """All episodes are disjoint records; only public inputs are reused."""
    rng=random.Random(seed)
    def episodes(n,persistent):
        results=[]
        for _ in range(n):
            regime=rng.choice((-1,1)) if persistent else None
            ep=[]
            for t in range(EPISODE_LEN):
                public_s, public_a = CONTEXTS[rng.randrange(len(CONTEXTS))]
                sign=regime if persistent else rng.choice((-1,1))
                base=old_target(public_s,public_a)
                observed=tuple(base[k]+sign*SHIFT[k]+rng.gauss(0.,NOISE_SIGMA)
                               for k in range(4))
                ep.append(PublicTransition.from_public(
                    observation=public_s,action=public_a,
                    next_observation=observed,reward=1.0,
                    terminated=(t==EPISODE_LEN-1),truncated=False))
            results.append(tuple(ep))
        return tuple(results)
    fit=episodes(32,True)
    valid=episodes(16,True)
    iid=episodes(16,False)
    return fit,valid,iid


def fit_static(fit_episodes):
    m=ProgrammedPublicDynamics()
    for ep in fit_episodes:
        for row in ep:
            m=m.observe(row.observation,row.action,row.next_observation)
    return m


def fit_memory(base,fit_episodes):
    m=PublicHistoryWeights(base)
    for ep in fit_episodes:
        previous=None
        for row in ep:
            if previous is not None:
                m=m.observe_pair(previous,row)
            previous=row
    return m


def public_residual(base,row):
    expected=base.predict(row.observation,row.action)
    return tuple(row.next_observation[k]-expected[k] for k in range(4))


def fitted_independent_lag_ridge(base,fit_episodes):
    gram=[[float(i==j) for j in range(4)] for i in range(4)]
    rhs=[[0.]*4 for _ in range(4)]
    for ep in fit_episodes:
        previous=None
        for row in ep:
            if previous is not None:
                x=public_residual(base,previous)
                y=public_residual(base,row)
                for i in range(4):
                    for j in range(4):
                        gram[i][j]+=x[i]*x[j]
                    for k in range(4):
                        rhs[i][k]+=x[i]*y[k]
            previous=row
    weights=tuple(solve_gaussian(gram, [rhs[i][k] for i in range(4)])
                  for k in range(4))
    def forecast(public_state,action,previous):
        b=base.predict(public_state,action)
        if previous is None:
            return b
        x=public_residual(base,previous)
        return tuple(b[k]+math.fsum(weights[k][j]*x[j] for j in range(4))
                     for k in range(4))
    return forecast


def _rmse(squares):
    return math.sqrt(math.fsum(squares)/len(squares))


def evaluate(episodes,model,base,independent=None,carry=False,
             shuffle_source=None,shuffle_seed=None):
    """Prequential scoring: current target never enters prediction API."""
    pools={"native_all":[],"static_all":[],"native_later":[],
           "static_later":[],"carry_later":[],"batch_later":[],
           "native_first":[],"static_first":[],"shuffle_later":[]}
    rand=random.Random(shuffle_seed) if shuffle_source is not None else None
    for ep in episodes:
        previous=None
        for row in ep:
            state,action=row.observation,row.action
            true=row.next_observation
            static=base.predict(state,action)
            native=model.predict(state,action,previous)
            # Current outcome is consulted by evaluator only AFTER prediction.
            for k in range(4):
                pools["static_all"].append((static[k]-true[k])**2)
                pools["native_all"].append((native[k]-true[k])**2)
                if previous is None:
                    pools["static_first"].append((static[k]-true[k])**2)
                    pools["native_first"].append((native[k]-true[k])**2)
                else:
                    pools["static_later"].append((static[k]-true[k])**2)
                    pools["native_later"].append((native[k]-true[k])**2)
            if previous is None:
                assert native==static, "first forecast leaked history"
            else:
                prev_r=public_residual(base,previous)
                carried=tuple(static[k]+prev_r[k] for k in range(4))
                batch=(independent(state,action,previous)
                       if independent is not None else native)
                shuffled=(model.predict(state,action,rand.choice(shuffle_source))
                          if rand is not None else native)
                for k in range(4):
                    pools["carry_later"].append((carried[k]-true[k])**2)
                    pools["batch_later"].append((batch[k]-true[k])**2)
                    pools["shuffle_later"].append((shuffled[k]-true[k])**2)
            previous=row
    return {k:_rmse(v) for k,v in pools.items() if v}


class HistoryWeightsTests(unittest.TestCase):
    def test_frozen_three_seed_persistent_and_iid_stress(self):
        receipts=[]
        for seed in SEEDS:
            fit,valid,iid=fixtures(seed)
            start_fit=time.process_time()
            base=fit_static(fit)
            model=fit_memory(base,fit)
            matched=fitted_independent_lag_ridge(base,fit)
            fit_cpu=time.process_time()-start_fit
            self.assertEqual(base.seen,512)
            self.assertEqual(model.seen,32*15)
            ckpt=model.checkpoint()
            cold=PublicHistoryWeights.restore(ckpt)
            self.assertEqual(cold.checkpoint(),ckpt)
            self.assertEqual(cold._base.checkpoint(),base.checkpoint())
            fit_public_nonterminal=[
                row for ep in fit for row in ep if not row.terminated]
            start_valid=time.process_time()
            persistent=evaluate(
                valid,model,base,independent=matched,
                shuffle_source=fit_public_nonterminal,
                shuffle_seed=seed+777)
            iid_stress=evaluate(iid,model,base)
            val_cpu=time.process_time()-start_valid
            self.assertGreaterEqual(persistent["static_later"]-
                                    persistent["native_later"],.05)
            self.assertLessEqual(abs(persistent["native_first"]-
                                     persistent["static_first"]),1e-14)
            self.assertGreater(persistent["shuffle_later"],
                               persistent["native_later"])
            self.assertAlmostEqual(persistent["native_later"],
                                   persistent["batch_later"],places=9)
            max_parity=0.0
            max_cold_gap=0.0
            for ep in valid:
                prev=None
                for row in ep:
                    a=model.predict(row.observation,row.action,prev)
                    b=matched(row.observation,row.action,prev)
                    c=cold.predict(row.observation,row.action,prev)
                    max_parity=max(max_parity,max(abs(a[k]-b[k]) for k in range(4)))
                    max_cold_gap=max(max_cold_gap,max(abs(a[k]-c[k]) for k in range(4)))
                    prev=row
            self.assertLessEqual(max_parity,1e-8)
            self.assertEqual(max_cold_gap,0.0)
            iid_regret=iid_stress["native_later"]-iid_stress["static_later"]
            receipts.append({
                "seed":seed,"fit_episodes":32,"valid_persistent_episodes":16,
                "iid_stress_episodes":16,"steps_per_episode":16,
                "static_fit_rows":base.seen,"direct_history_fit_pairs":model.seen,
                "persistent_later_static_rmse":persistent["static_later"],
                "persistent_later_native_rmse":persistent["native_later"],
                "persistent_later_independent_batch_rmse":persistent["batch_later"],
                "persistent_later_carry_rmse":persistent["carry_later"],
                "persistent_later_shuffled_history_rmse":persistent["shuffle_later"],
                "persistent_first_static_rmse":persistent["static_first"],
                "persistent_first_native_rmse":persistent["native_first"],
                "persistent_all_static_rmse":persistent["static_all"],
                "persistent_all_native_rmse":persistent["native_all"],
                "iid_later_static_rmse":iid_stress["static_later"],
                "iid_later_native_rmse":iid_stress["native_later"],
                "iid_regret_rmse":iid_regret,
                "iid_regression_gt_0p01":iid_regret>.01,
                "max_independent_batch_forecast_gap":max_parity,
                "max_cold_prediction_gap":max_cold_gap,
                "checkpoint_bytes":len(ckpt),
                "checkpoint_sha256":hashlib.sha256(ckpt).hexdigest(),
                "fit_cpu_seconds":fit_cpu,"validation_cpu_seconds":val_cpu,
                "original_source_actions":0
            })
        self.assertNotIn("causal_gym",sys.modules)
        print("WSP163_FROZEN_SOURCEFREE_RESULTS="+json.dumps(
            receipts,sort_keys=True,separators=(",",":")))

    def test_history_api_rejects_nonpublic_and_future_leakage(self):
        fit,valid,_=fixtures(1631)
        model=PublicHistoryWeights(fit_static(fit))
        before=model.checkpoint()
        first=fit[0][0]
        last=fit[0][-1]
        for previous in (None, "private", {"regime":1}, object()):
            if previous is None:
                self.assertEqual(model.predict(first.observation,first.action,None),
                                 model.static_predict(first.observation,first.action))
            else:
                with self.assertRaises(ValueError):
                    model.predict(first.observation,first.action,previous)
        with self.assertRaisesRegex(ValueError,"EPISODE_RESET"):
            model.predict(first.observation,first.action,last)
        with self.assertRaisesRegex(ValueError,"EPISODE_RESET"):
            model.observe_pair(last,valid[0][0])
        with self.assertRaises(ValueError):
            model.observe_pair(first,{"hidden_regime":1})
        with self.assertRaises(TypeError):
            model.observe_pair(first,fit[0][1],future_target=1)
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELD_SET"):
            PublicTransition.from_public(**{
                **first.model_input(),"hidden_regime":1})
        self.assertEqual(model.checkpoint(),before)

    def test_cold_continuation_retains_exact_same_weights(self):
        fit,_,_=fixtures(1631)
        base=fit_static(fit)
        program=PublicHistoryWeights(base)
        previous,new=fit[0][:2]
        program=program.observe_pair(previous,new)
        frozen=program.checkpoint()
        cold=PublicHistoryWeights.restore(frozen)
        next_record=fit[0][2]
        a=program.observe_pair(new,next_record)
        b=cold.observe_pair(new,next_record)
        self.assertEqual(a.checkpoint(),b.checkpoint())
        self.assertEqual(ProgrammedPublicDynamics.restore(
            cold._base.checkpoint()).checkpoint(),base.checkpoint())

    def test_checksum_tamper_duplicate_keys_and_rehash_poison(self):
        fit,_,_=fixtures(1741)
        program=fit_memory(fit_static(fit),fit)
        frozen=program.checkpoint()
        for raw in (frozen[:-1],frozen+b"x",b"FAKE"+frozen[4:],
                    frozen[:15]+bytes([frozen[15]^1])+frozen[16:],
                    "not bytes",bytearray(frozen)):
            with self.subTest(kind=str(type(raw))):
                with self.assertRaises(ValueError):
                    PublicHistoryWeights.restore(raw)
        data=json.loads(frozen[8:-32])
        data["inverse"][0][0]=-1.0
        payload=json.dumps(data,sort_keys=True,separators=(",",":")).encode("ascii")
        raw=MAGIC+len(payload).to_bytes(4,"big")+payload
        raw+=hashlib.sha256(raw).digest()
        with self.assertRaisesRegex(ValueError,"FIELDS"):
            PublicHistoryWeights.restore(raw)
        # Even when the digest is correctly recomputed, private metadata
        # cannot be laundered into a learned checkpoint.
        data=json.loads(frozen[8:-32])
        data["regime_label"]=1
        payload=json.dumps(data,sort_keys=True,separators=(",",":")).encode("ascii")
        raw=MAGIC+len(payload).to_bytes(4,"big")+payload
        raw+=hashlib.sha256(raw).digest()
        with self.assertRaisesRegex(ValueError,"FIELDS"):
            PublicHistoryWeights.restore(raw)

    def test_bounded_update_public_invalid_and_cumulative_limit(self):
        fit,_,_=fixtures(1867)
        base=fit_static(fit)
        program=PublicHistoryWeights(base)
        a,b=fit[0][:2]
        for malformed in ([float("nan"),0.,0.,0.],
                          [0.,float("inf"),0.,0.],[1.,2.,3.],"abc"):
            with self.assertRaises(ValueError):
                program.predict(malformed,1,a)
        with self.assertRaises(ValueError):
            program.predict(a.observation,2,a)
        with self.assertRaises(TypeError):
            program.predict(a.observation,1,a,hidden_source=1)
        maxed=PublicHistoryWeights._new(
            program._base,program._w,program._inv,2048)
        with self.assertRaisesRegex(ValueError,"ROW_CAP"):
            maxed.observe_pair(a,b)
        self.assertEqual(PublicHistoryWeights.restore(
            maxed.checkpoint()).seen,2048)


if __name__=="__main__":
    unittest.main()

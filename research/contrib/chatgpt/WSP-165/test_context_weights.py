"""WSP165 frozen source-free context learning and unseen-structure stress.

Only public action-consequence records are passed to learning/prediction.
The synthetic evaluator alone constructs the hidden sign; the sign is never
attached to any public learner, conventional control or held forecast.
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
for p in ("WSP-159","WSP-160","WSP-161","WSP-162","WSP-163","WSP-164"):
    sys.path.insert(0,str(HERE/p))

from public_boundary import PublicTransition
from test_history_weights import fixtures, fit_static, fit_memory, public_residual, CONTEXTS, SHIFT
from test_overlap_certificate import old_target
from reliability_gate import ReliablePublicHistory
from test_reliability_gate import FittedBayesianPersistence
from context_weights import DirectPublicContext, MAGIC, MAX_HISTORY

SEEDS=(2281,2393,2503)
NEW_SHIFT=(.05,.18,-.20,.12)
P_MODERATE_STAY=.8
N_HELD_EPISODES=16
EPISODE_LENGTH=16


def unfamiliar_public_episodes(seed, rotated_action):
    rng=random.Random(seed + (12000 if rotated_action else 9000))
    output=[]
    for episode_id in range(N_HELD_EPISODES):
        sign=rng.choice((-1,1))
        ep=[]
        for t in range(EPISODE_LENGTH):
            if t>0 and rng.random() > P_MODERATE_STAY:
                sign=-sign
            state,action=CONTEXTS[rng.randrange(len(CONTEXTS))]
            causal=old_target(state,action)
            multiplier=(2*action-1) if rotated_action else 1
            shift=NEW_SHIFT if rotated_action else SHIFT
            observed=tuple(
                causal[k]+sign*multiplier*shift[k]+rng.gauss(0,.02)
                for k in range(4))
            ep.append(PublicTransition.from_public(
                observation=state,action=action,next_observation=observed,
                reward=1.,terminated=(t==EPISODE_LENGTH-1),truncated=False))
        output.append(tuple(ep))
    return tuple(output)


class IndependentlyFittedBatchBayes:
    """Separate FIT batch sums and posterior filter, equal public information.

    Deliberately does not read WSP165 internals, checkpoint, coefficients or
    inferred classes. It receives the same static public FIT base and
    public transition episodes and makes the same likelihood assumption.
    """
    def __init__(self,base,fit_episodes):
        self.base=base
        negatives=[]
        positives=[]
        same=0
        total=0
        for ep in fit_episodes:
            prior_mode=None
            for record in ep:
                baseline=base.predict(record.observation,record.action)
                resid=tuple(record.next_observation[k]-baseline[k] for k in range(4))
                mode=int(resid[0]>=0.)
                (positives if mode else negatives).append(resid)
                if prior_mode is not None:
                    total+=1
                    same+=int(prior_mode==mode)
                prior_mode=mode
        if total!=480 or not positives or not negatives:
            raise ValueError("WSP165_BATCH_FIT_INVALID")
        self.prototypes=tuple(
            tuple(math.fsum(v[k] for v in population)/len(population)
                  for k in range(4)) for population in (negatives,positives))
        self.persistence=min(.999,max(.50,(same+1)/(total+2)))

    def predict(self,state,action,history):
        baseline=self.base.predict(state,action)
        if len(history)<MAX_HISTORY:
            return baseline
        inferred=[]
        for row in history:
            prev=self.base.predict(row.observation,row.action)
            r=tuple(row.next_observation[k]-prev[k] for k in range(4))
            errors=[math.fsum((r[k]-self.prototypes[m][k])**2 for k in range(4))
                    for m in (0,1)]
            inferred.append(int(errors[1]<errors[0]))
        count_stay=sum(int(a==b) for a,b in zip(inferred[:-1],inferred[1:]))
        count_flip=len(inferred)-1-count_stay
        likelihood_persistent=(self.persistence/.5)**count_stay * (
            (1-self.persistence)/.5)**count_flip
        posterior=likelihood_persistent/(1+likelihood_persistent)
        middle=tuple((self.prototypes[0][k]+self.prototypes[1][k])/2
                     for k in range(4))
        coefficient=posterior*(2*self.persistence-1)
        prototype=self.prototypes[inferred[-1]]
        return tuple(baseline[k]+middle[k]+coefficient*(
            prototype[k]-middle[k]) for k in range(4))


def _rmse(squares):
    return math.sqrt(math.fsum(squares)/len(squares))


def score(episodes,base,program,ungated,older_gate,bayes,matched,fit_public,shuffle_seed):
    rng=random.Random(shuffle_seed)
    squares={key:[] for key in ("static","native","ungated","older_gate",
        "bayes","matched","carry","shuffled")}
    first_drift=0.
    max_matched=0.
    total_later=0
    for ep in episodes:
        history=[]
        for row in ep:
            obs,action=row.observation,row.action
            public_history=history[-MAX_HISTORY:]
            base_out=base.predict(obs,action)
            direct=program.predict(obs,action,public_history)
            independent=matched.predict(obs,action,public_history)
            if not history:
                first_drift=max(first_drift,max(
                    abs(direct[k]-base_out[k]) for k in range(4)))
            max_matched=max(max_matched,max(
                abs(direct[k]-independent[k]) for k in range(4)))
            if history:
                total_later+=1
                others={
                    "static":base_out,
                    "native":direct,
                    "ungated":ungated.predict(obs,action,history[-1]),
                    "older_gate":older_gate.predict(obs,action,public_history),
                    "bayes":bayes.predict(obs,action,history),
                    "matched":independent,
                    "carry":tuple(base_out[k]+public_residual(base,history[-1])[k]
                                  for k in range(4)),
                    "shuffled":program.predict(
                        obs,action,rng.sample(fit_public,MAX_HISTORY))
                }
                for name,out in others.items():
                    squares[name].extend((out[k]-row.next_observation[k])**2
                                         for k in range(4))
            history.append(row)  # current next-state only after current forecast
    if total_later!=N_HELD_EPISODES*(EPISODE_LENGTH-1):
        raise AssertionError("WSP165_HELD_ROWS_CHANGED")
    return {name+"_rmse":_rmse(s) for name,s in squares.items()} | {
        "first_step_static_max_gap":first_drift,
        "strong_matched_max_prediction_gap":max_matched,
        "later_steps":total_later
    }


class ContextTransferTests(unittest.TestCase):
    def test_frozen_three_seed_four_domain_transfer_with_all_controls(self):
        receipts=[]
        for seed in SEEDS:
            train,persistent,iid=fixtures(seed)
            moderate=unfamiliar_public_episodes(seed,rotated_action=False)
            rotated=unfamiliar_public_episodes(seed,rotated_action=True)
            fit_start=time.process_time()
            base=fit_static(train)
            lag=fit_memory(base,train)
            gate=ReliablePublicHistory.from_fit(lag,train)
            learner=DirectPublicContext.fit(base,train)
            conventional=FittedBayesianPersistence(base,train)
            matched=IndependentlyFittedBatchBayes(base,train)
            fit_cpu=time.process_time()-fit_start
            self.assertEqual(base.seen,512)
            self.assertEqual(lag.seen,480)
            checkpoint=learner.checkpoint()
            cold=DirectPublicContext.restore(checkpoint)
            self.assertEqual(cold.checkpoint(),checkpoint)
            fit_public=[r for ep in train for r in ep if not r.terminated]
            val_start=time.process_time()
            metrics={}
            for domain,episodes in (
                    ("persistent",persistent),
                    ("iid",iid),
                    ("moderate",moderate),
                    ("rotated_action",rotated)):
                metrics[domain]=score(
                    episodes,base,learner,lag,gate,conventional,matched,
                    fit_public,seed+len(domain)*37)
                self.assertLessEqual(
                    metrics[domain]["strong_matched_max_prediction_gap"],1e-8)
                self.assertEqual(metrics[domain]["first_step_static_max_gap"],0.)
                # Same-source checkpoint predictions are exact with no
                # retraining, action replay, extra source exposure or oracle.
                for ep in episodes[:2]:
                    hist=[]
                    for row in ep:
                        expected=learner.predict(
                            row.observation,row.action,hist[-5:])
                        self.assertEqual(expected,cold.predict(
                            row.observation,row.action,hist[-5:]))
                        hist.append(row)
            val_cpu=time.process_time()-val_start
            persist=metrics["persistent"]
            rapid=metrics["iid"]
            mod=metrics["moderate"]
            rot=metrics["rotated_action"]
            receipts.append({
                "seed":seed,
                "fit_public_rows":512,"fit_episodes":32,
                "held_episodes_per_domain":16,
                "public_steps_per_episode":16,
                "fitted_persistence_probability":learner.stay_probability,
                "sourcefree_threshold_persistent_pass":persist["native_rmse"]<=.08,
                "persistent_native_rmse":persist["native_rmse"],
                "persistent_static_rmse":persist["static_rmse"],
                "persistent_wsp163_rmse":persist["ungated_rmse"],
                "persistent_wsp164_rmse":persist["older_gate_rmse"],
                "persistent_bayesian_rmse":persist["bayes_rmse"],
                "persistent_matched_rmse":persist["matched_rmse"],
                "persistent_carry_rmse":persist["carry_rmse"],
                "persistent_shuffled_rmse":persist["shuffled_rmse"],
                "iid_static_rmse":rapid["static_rmse"],
                "iid_native_rmse":rapid["native_rmse"],
                "iid_bayesian_rmse":rapid["bayes_rmse"],
                "iid_ungated_rmse":rapid["ungated_rmse"],
                "iid_regret_rmse":rapid["native_rmse"]-rapid["static_rmse"],
                "sourcefree_threshold_iid_pass":
                    rapid["native_rmse"]-rapid["static_rmse"]<=.01,
                "moderate_static_rmse":mod["static_rmse"],
                "moderate_native_rmse":mod["native_rmse"],
                "moderate_bayesian_rmse":mod["bayes_rmse"],
                "moderate_transfer_signal":
                    mod["static_rmse"]-mod["native_rmse"]>=.015,
                "rotated_static_rmse":rot["static_rmse"],
                "rotated_native_rmse":rot["native_rmse"],
                "rotated_bayesian_rmse":rot["bayes_rmse"],
                "rotated_structural_transfer_signal":
                    rot["static_rmse"]-rot["native_rmse"]>=.015,
                "max_matched_control_prediction_gap":max(
                    m["strong_matched_max_prediction_gap"]
                    for m in metrics.values()),
                "same_os_checkpoint_sha256":hashlib.sha256(checkpoint).hexdigest(),
                "checkpoint_bytes":len(checkpoint),
                "cpu_fit_seconds":fit_cpu,"cpu_scoring_seconds":val_cpu,
                "original_source_actions":0
            })
        self.assertNotIn("causal_gym",sys.modules)
        print("WSP165_FROZEN_TRANSFER_RESULTS="+json.dumps(
            receipts,sort_keys=True,separators=(",",":")))

    def test_source_blind_five_witness_minimum_and_episode_boundary(self):
        train,valid,_=fixtures(2281)
        base=fit_static(train)
        model=DirectPublicContext.fit(base,train)
        row=valid[0][0]
        for n in range(5):
            self.assertEqual(model.predict(
                row.observation,row.action,list(valid[0][:n])),
                base.predict(row.observation,row.action))
        self.assertGreater(model.stay_probability,.5)
        with self.assertRaisesRegex(ValueError,"HISTORY_TERMINAL_RESET"):
            model.predict(row.observation,row.action,list(valid[0][-5:]))
        with self.assertRaisesRegex(ValueError,"HISTORY_WINDOW"):
            model.predict(row.observation,row.action,list(valid[0][:6]))
        with self.assertRaisesRegex(ValueError,"HISTORY_PUBLIC_ONLY"):
            model.predict(row.observation,row.action,[{"secret_regime":1}])
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELD_SET"):
            PublicTransition.from_public(**{**row.model_input(),"hidden_regime":1})
        with self.assertRaises(ValueError):
            model.predict([math.nan,0,0,0],0,[])
        with self.assertRaises(ValueError):
            model.predict(row.observation,2,[])

    def test_frozen_fit_source_only_and_no_oracle_labels(self):
        train,valid,_=fixtures(2393)
        base=fit_static(train)
        model=DirectPublicContext.fit(base,train)
        frozen=model.checkpoint()
        with self.assertRaises(TypeError):
            model.predict(valid[0][0].observation,1,[],future_target=1)
        with self.assertRaises(TypeError):
            model.predict(valid[0][0].observation,1,[],regime_id=1)
        with self.assertRaisesRegex(ValueError,"EPISODE_COUNT"):
            DirectPublicContext.fit(base,train[:1])
        with self.assertRaisesRegex(ValueError,"FIT_EPISODE_SHAPE"):
            DirectPublicContext.fit(base,[ep[:3] for ep in train])
        self.assertEqual(model.checkpoint(),frozen)

    def test_checksum_and_rehashed_privileged_tamper_rejected(self):
        train,_,_=fixtures(2503)
        model=DirectPublicContext.fit(fit_static(train),train)
        raw=model.checkpoint()
        for broken in (raw[:-1],raw+b"x",b"FAKE"+raw[4:],
                       raw[:15]+bytes([raw[15]^1])+raw[16:],
                       "text",bytearray(raw)):
            with self.subTest(kind=str(type(broken))):
                with self.assertRaises(ValueError):
                    DirectPublicContext.restore(broken)
        obj=json.loads(raw[8:-32])
        obj["hidden_source"] = "oracle"
        payload=json.dumps(obj,sort_keys=True,separators=(",",":")).encode("ascii")
        data=MAGIC+len(payload).to_bytes(4,"big")+payload
        data+=hashlib.sha256(data).digest()
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_FIELDS"):
            DirectPublicContext.restore(data)
        obj.pop("hidden_source")
        obj["means"][1][0]=float("nan")
        payload=json.dumps(obj,sort_keys=True,separators=(",",":")).encode("ascii")
        data=MAGIC+len(payload).to_bytes(4,"big")+payload
        data+=hashlib.sha256(data).digest()
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_FIELDS"):
            DirectPublicContext.restore(data)


if __name__=="__main__":
    unittest.main()

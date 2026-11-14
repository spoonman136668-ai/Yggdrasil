"""AAI-07B: reward-trained, observation-only cue/action association on official MiniGrid.

Frozen external research: no Yggdrasil native model changes, no hard-coded
cue-matching decision. Every training target is derived from terminal reward
following a real chosen action; all baselines receive exactly the same ledger.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time

import gymnasium as gym
import minigrid
import numpy as np
from minigrid.core.constants import OBJECT_TO_IDX

PREREG = "10e0ad453454a0f85eafbda1c8618657979810bd"
SOURCE_SHA = "64e1eaec904bc35e7de041167274e2c0dfe541d2"
CUES = (OBJECT_TO_IDX["key"], OBJECT_TO_IDX["ball"])
WALL = OBJECT_TO_IDX["wall"]
TRAIN = range(981000, 981048)
DEV = range(982000, 982064)
TRANSFER = range(983000, 983064)
CONTINUATION = range(984000, 984016)
NEGATIVE = range(985000, 985064)
MAX_ACTIONS = 120
EPOCHS = 2000
BOOTSTRAP = 1024


def h(seed, *items):
    raw = ":".join(str(x) for x in (seed, *items)).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def observed_ahead(observation, distance=1):
    array = np.asarray(observation["image"])
    assert array.shape == (7, 7, 3)
    assert np.issubdtype(array.dtype, np.integer)
    assert int(observation["direction"]) in (0, 1, 2, 3)
    assert distance in (1, 2)
    return int(array[3, 6-distance, 0])


def execute_episode(env_id, seed, choose):
    """Navigate via public partial observation; caller alone makes terminal choice."""
    env = gym.make(env_id, render_mode=None)
    actions = []
    try:
        observation, info = env.reset(seed=seed)
        assert env.action_space.n == 7
        assert isinstance(info, dict)
        def step(action):
            nonlocal observation
            assert env.action_space.contains(action)
            observation, reward, ended, truncated, info = env.step(action)
            actions.append(action)
            assert len(actions) <= MAX_ACTIONS, "Action budget exceeded"
            assert isinstance(info, dict)
            return float(reward), bool(ended or truncated)
        for action in (1, 1):
            _, done = step(action)
            assert not done
        for _ in range(24):
            if observed_ahead(observation) == WALL:
                break
            _, done = step(2)
            assert not done
        else:
            raise AssertionError("Entrance boundary invisible")
        _, done = step(1)
        assert not done
        entrance_cue = observed_ahead(observation)
        assert entrance_cue in CUES, ("no visual cue", entrance_cue)
        _, done = step(1)
        assert not done
        for _ in range(24):
            if observed_ahead(observation) == WALL:
                break
            _, done = step(2)
            assert not done
        else:
            raise AssertionError("Junction invisible")
        _, done = step(0)
        assert not done
        upper_cue = observed_ahead(observation, distance=2)
        assert upper_cue in CUES, ("no visible branch object", upper_cue)
        # No explicit cue comparison here. Behavior is supplied by learned model.
        chosen_top = bool(choose(entrance_cue, upper_cue))
        if not chosen_top:
            for turn in (1, 1):
                _, done = step(turn)
                assert not done
        reward, done = step(2)
        assert done, "Must terminate upon entering one of the two end cells"
        assert 0.0 <= reward <= 1.0
        return {
            "seed": seed,
            "cue": entrance_cue, "upper": upper_cue,
            "chosen_top": chosen_top, "success": reward > 0,
            "reward": round(reward, 8), "actions": len(actions),
            "terminated": done,
        }
    finally:
        env.close()


def common_ledger(env_id, seeds):
    # A genuinely external random action policy (same actual outcomes for all arms).
    return [execute_episode(env_id, seed,
            lambda cue, upper, seed=seed: h(seed, "behavior") % 2 == 0)
            for seed in seeds]


def key(row):
    return str(row["cue"]) + ":" + str(row["upper"])


def winning_top(row):
    # Published two-branch deterministic task: one terminal branch is correct.
    # Derive the winning branch solely from chosen action and actual reward.
    return bool(row["chosen_top"]) == bool(row["success"])


class DirectAssociation:
    """One mutable associative state updated sequentially by actual consequences."""
    def __init__(self):
        self.weights = {}

    def learn(self, ledger):
        for row in ledger:
            token = key(row)
            direction = 1 if row["chosen_top"] else -1
            consequence = 1 if row["success"] else -1
            self.weights[token] = self.weights.get(token, 0) + direction * consequence

    def choose(self, cue, upper):
        return self.weights.get(str(cue) + ":" + str(upper), 0) >= 0

    def dump(self):
        return json.dumps(self.weights, separators=(",", ":"), sort_keys=True)

    @classmethod
    def restore(cls, payload):
        x=cls()
        x.weights=json.loads(payload)
        assert all(isinstance(v, int) for v in x.weights.values())
        return x


class BetaTable:
    """Exact conventional Laplace-smoothed contextual two-action table."""
    def __init__(self):
        self.counts = {}

    def learn(self, ledger):
        for row in ledger:
            token=key(row)
            win=self.counts.setdefault(token, [1, 1])
            win[0 if winning_top(row) else 1] += 1

    def choose(self, cue, upper):
        top, bottom = self.counts.get(str(cue) + ":" + str(upper), [1, 1])
        return top >= bottom

    def dump(self):
        return json.dumps(self.counts, separators=(",", ":"), sort_keys=True)

    @classmethod
    def restore(cls, payload):
        x=cls()
        x.counts=json.loads(payload)
        return x


class LogisticControl:
    """Fully trained categorical conventional logistic, 2000 full-batch steps."""
    def __init__(self):
        self.weights=[0.0] * 5

    @staticmethod
    def features(cue, upper):
        # Explicit four-category interaction features: no equality feature.
        k=CUES.index(cue)*2+CUES.index(upper)
        return [1.0]+[1.0 if i==k else 0.0 for i in range(4)]

    def learn(self, ledger):
        xs=[self.features(row["cue"], row["upper"]) for row in ledger]
        ys=[int(winning_top(row)) for row in ledger]
        for _ in range(EPOCHS):
            grad=[0.0]*5
            for x,y in zip(xs,ys):
                z=sum(w*v for w,v in zip(self.weights,x))
                z=max(-40.0,min(40.0,z))
                prediction=1.0/(1.0+math.exp(-z))
                for i in range(5):
                    grad[i]+=(prediction-y)*x[i]
            for i in range(5):
                self.weights[i]-=.25*grad[i]/len(xs)

    def choose(self, cue, upper):
        x=self.features(cue,upper)
        return sum(w*v for w,v in zip(self.weights,x))>=0.0

    def dump(self):
        return json.dumps(self.weights, separators=(",", ":"))

    @classmethod
    def restore(cls,payload):
        x=cls()
        x.weights=json.loads(payload)
        return x


def fit(learner_class, ledger):
    obj=learner_class()
    started=time.perf_counter()
    obj.learn(ledger)
    duration=time.perf_counter()-started
    return obj, duration


def fixed_predictions(model):
    return [model.choose(cue, upper) for cue in CUES for upper in CUES]


def single_cohort(env_id, seeds, models):
    rows=[]
    for seed in seeds:
        current={"seed":seed}
        feature_pair=None
        for name, model in models.items():
            decide=(lambda cue, upper, model=model: model.choose(cue,upper)
                    if model is not None else True)
            result=execute_episode(env_id,seed,decide)
            observed=(result["cue"],result["upper"])
            if feature_pair is None:
                feature_pair=observed
            else:
                assert observed==feature_pair
            current[name]=result["success"]
            current[name+"_reward"]=result["reward"]
            current[name+"_actions"]=result["actions"]
        current["cue"],current["upper"]=feature_pair
        rows.append(current)
    return rows


def ci(rows, method, baseline):
    diffs=[int(z[method])-int(z[baseline]) for z in rows]
    n=len(diffs)
    rng=random.Random(18181)
    draws=sorted(sum(diffs[rng.randrange(n)] for _ in range(n))/n
                 for _ in range(BOOTSTRAP))
    return [round(draws[25],8),round(draws[998],8)]


def summary(rows, methods):
    n=len(rows)
    return {name:{
        "n":n,"success":round(sum(int(row[name]) for row in rows)/n,8),
        "mean_reward":round(sum(row[name+"_reward"] for row in rows)/n,8),
        "mean_actions":round(sum(row[name+"_actions"] for row in rows)/n,6)}
        for name in methods}


def audit():
    assert len(set(TRAIN)|set(DEV)|set(TRANSFER)|set(NEGATIVE)|set(CONTINUATION))==256
    assert (len(TRAIN),len(DEV),len(TRANSFER),len(NEGATIVE),len(CONTINUATION))==(48,64,64,64,16)
    assert len(CUES)==2 and CUES[0]!=CUES[1]
    sample=[
        {"cue":CUES[0],"upper":CUES[0],"chosen_top":False,"success":False},
        {"cue":CUES[0],"upper":CUES[1],"chosen_top":True,"success":False},
        {"cue":CUES[1],"upper":CUES[0],"chosen_top":False,"success":False},
        {"cue":CUES[1],"upper":CUES[1],"chosen_top":True,"success":True},
    ]
    for cls in (DirectAssociation, BetaTable, LogisticControl):
        learner,_=fit(cls,sample)
        assert learner.dump()==cls.restore(learner.dump()).dump()
        assert fixed_predictions(learner)==[True,False,True,True]
    return True


def main():
    started=time.perf_counter()
    assert audit()
    assert minigrid.__version__=="3.2.0"
    ledger=common_ledger("MiniGrid-MemoryS11-v0",TRAIN)
    models={}
    fit_times={}
    bytes_inference={}
    for name, cls in (("direct",DirectAssociation),
                      ("beta",BetaTable),
                      ("logistic",LogisticControl)):
        model,seconds=fit(cls,ledger)
        models[name]=model
        fit_times[name]=round(seconds,8)
        bytes_inference[name]=len(model.dump().encode("utf-8"))
        assert fixed_predictions(model)==fixed_predictions(cls.restore(model.dump()))
    models["reactive"]=None
    dev=single_cohort("MiniGrid-MemoryS11-v0",DEV,models)
    transfer=single_cohort("MiniGrid-MemoryS13Random-v0",TRANSFER,models)
    # Negative control preserves each observed context and chosen action but
    # scrambles only genuine observed reward outcomes, before learner training.
    shuffled=[row["success"] for row in ledger]
    random.Random(18081).shuffle(shuffled)
    shuffled_ledger=[dict(z,success=y) for z,y in zip(ledger,shuffled)]
    random_model,_=fit(DirectAssociation,shuffled_ledger)
    negative=single_cohort("MiniGrid-MemoryS13Random-v0",NEGATIVE,
                           {"proper":models["direct"],"shuffled":random_model})
    pre_continue={k:fixed_predictions(models[k]) for k in ("direct","beta","logistic")}
    snapshot={k:models[k].dump() for k in ("direct","beta","logistic")}
    cold_ok=all(fixed_predictions(models[k])==fixed_predictions(
        cls.restore(snapshot[k])) for k,cls in (
        ("direct",DirectAssociation),("beta",BetaTable),("logistic",LogisticControl)))
    # Continue *the same mutable objects*, with new reward-bearing experience.
    other=common_ledger("MiniGrid-MemoryS13Random-v0",CONTINUATION)
    for model in (models["direct"],models["beta"],models["logistic"]):
        model.learn(other)
    post_continue={k:fixed_predictions(models[k]) for k in ("direct","beta","logistic")}
    continuation_stable=pre_continue==post_continue
    restored_original_exact=all(fixed_predictions(
        cls.restore(snapshot[k]))==pre_continue[k] for k,cls in (
        ("direct",DirectAssociation),("beta",BetaTable),("logistic",LogisticControl)))
    d=summary(dev,models)
    t=summary(transfer,models)
    n=summary(negative,("proper","shuffled"))
    strongest=max(("beta","logistic"),key=lambda m:t[m]["success"])
    gaps={
        "dev_direct_minus_reactive":round(d["direct"]["success"]-d["reactive"]["success"],8),
        "transfer_direct_minus_reactive":round(t["direct"]["success"]-t["reactive"]["success"],8),
        "transfer_direct_minus_strongest":round(t["direct"]["success"]-t[strongest]["success"],8),
        "negative_proper_minus_shuffled":round(n["proper"]["success"]-n["shuffled"]["success"],8)
    }
    ci_values={
        "dev_direct_vs_reactive":ci(dev,"direct","reactive"),
        "transfer_direct_vs_reactive":ci(transfer,"direct","reactive"),
        "transfer_direct_vs_strongest":ci(transfer,"direct",strongest),
        "negative_proper_vs_shuffled":ci(negative,"proper","shuffled"),
    }
    learning_checks={
        "dev_min_success":d["direct"]["success"]>=.80,
        "transfer_min_success":t["direct"]["success"]>=.80,
        "dev_ablation_gap":gaps["dev_direct_minus_reactive"]>=.20,
        "transfer_ablation_gap":gaps["transfer_direct_minus_reactive"]>=.20,
        "dev_paired_ci_positive":ci_values["dev_direct_vs_reactive"][0]>0,
        "transfer_paired_ci_positive":ci_values["transfer_direct_vs_reactive"][0]>0,
        "negative_shuffle_ablation":gaps["negative_proper_minus_shuffled"]>=.15,
        "cold_restore":cold_ok and restored_original_exact,
        "continued_model_retains_rule":continuation_stable,
    }
    science_checks={
        "all_learning_checks":all(learning_checks.values()),
        "beats_strongest_trained_method":gaps["transfer_direct_minus_strongest"]>=.03,
        "paired_ci_superior":ci_values["transfer_direct_vs_strongest"][0]>0,
        "training_time_ratio":fit_times["direct"]<=1.5*min(
            fit_times["beta"],fit_times["logistic"]),
    }
    if all(science_checks.values()):
        cls="SCIENTIFIC_CANDIDATE_UNQUALIFIED"
    elif all(learning_checks.values()):
        cls="LEARNING_DEMONSTRATED_NOT_SUPERIOR"
    else:
        cls="VALID_NEGATIVE_OR_MIXED_NO_INTEGRATION"
    per_world={"dev":dev,"transfer":transfer,"negative":negative}
    return {
        "schema":"yggdrasil.aai07b.reward-trained-memory.v1",
        "prereg_commit":PREREG,
        "classification":cls,
        "cohorts":{"dev":d,"transfer":t,"negative":n},
        "strongest_conventional":strongest,
        "gaps":gaps,"paired_bootstrap_95":ci_values,
        "learning_checks":learning_checks,"superiority_checks":science_checks,
        "fit_seconds":fit_times,"serialized_inference_bytes":bytes_inference,
        "training_episodes":len(ledger),"continuation_episodes":len(other),
        "cold_restore_exact":cold_ok and restored_original_exact,
        "continued_shared_model_stable":continuation_stable,
        "pre_continuation_model_policy":pre_continue,
        "post_continuation_model_policy":post_continue,
        "world_records_sha256":hashlib.sha256(json.dumps(
            per_world,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        "world_rows":per_world,
        "limitations":"All methods know categorical observation types and task is the same equality-based goal in both environments; navigation is scripted. The direct association equals a standard Beta-table decision under these data and is not a new learning algorithm. No unknown dynamics or conflicting-task interference was measured. No native model changed.",
        "source_environment_commit":SOURCE_SHA,
        "integration":"NONE",
        "duration_seconds":round(time.perf_counter()-started,6),
    }


if __name__=="__main__":
    print(json.dumps(main(),sort_keys=True,indent=2))

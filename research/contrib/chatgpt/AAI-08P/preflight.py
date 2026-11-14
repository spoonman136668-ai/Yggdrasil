"""AAI-08P: independent NS-Gym Bridge mechanical-only nonstationarity proof.
The action trace uses official API. No scientific/learner seed is consumed.
"""
import hashlib
import json

import gymnasium as gym
import ns_gym
from ns_gym.schedulers import DiscreteScheduler
from ns_gym.update_functions import DistributionStepWiseUpdate
from ns_gym.wrappers import NSBridgeWrapper

UPSTREAM = "127df4b714fe4fcf680721d8e9278a96090acd7e"
MECHANICAL_SEEDS = (996000, 996001, 996002, 996003)
ACTIONS = (2, 0, 2, 2)
INITIAL = (1.0, 0.0, 0.0)
CHANGED = (0.0, 1.0, 0.0)


def rollout(seed, shift):
    base = gym.make("ns_gym/Bridge-v0")
    if shift:
        scheduler = DiscreteScheduler({3})
    else:
        scheduler = DiscreteScheduler({999})
    rule = DistributionStepWiseUpdate(scheduler, [list(CHANGED)])
    env = NSBridgeWrapper(
        base, tunable_params={"P": rule},
        initial_prob_dist=list(INITIAL),
        change_notification=False, delta_change_notification=False,
        scalar_reward=True, persistent_params=False)
    try:
        observation, _diagnostic_info = env.reset(seed=seed)
        assert set(observation) == {"state", "env_change", "delta_change", "relative_time"}
        assert observation["env_change"]["P"] == 0
        assert observation["delta_change"]["P"] == 0
        stream = [int(observation["state"])]
        rewards = []
        terminations = []
        for step, action in enumerate(ACTIONS):
            observation, reward, ended, truncated, _diagnostic_info = env.step(action)
            assert observation["env_change"]["P"] == 0
            assert observation["delta_change"]["P"] == 0
            assert int(observation["relative_time"]) == step + 1
            assert float(reward) in (-1.,0.,1.)
            stream.append(int(observation["state"]))
            rewards.append(float(reward))
            terminations.append(bool(ended or truncated))
            if ended or truncated:
                break
        return {"states": stream, "rewards": rewards, "terminals": terminations,
                "steps": len(rewards)}
    finally:
        env.close()


def mechanical():
    pairs = []
    for seed in MECHANICAL_SEEDS:
        stationary = rollout(seed, False)
        changed = rollout(seed, True)
        assert stationary == rollout(seed, False), "Stationary mismatch"
        assert changed == rollout(seed, True), "Shifted mismatch"
        assert stationary["steps"] == changed["steps"] == len(ACTIONS)
        assert stationary["states"][:4] == changed["states"][:4]
        assert stationary["states"][4] != changed["states"][4]
        assert stationary["rewards"][-1] == 0.0
        assert changed["rewards"][-1] == -1.0
        assert stationary["terminals"][-1] is False
        assert changed["terminals"][-1] is True
        pairs.append({"seed": seed,"stationary": stationary, "changed": changed})
    digest=hashlib.sha256(json.dumps(pairs,sort_keys=True,
                                  separators=(",",":")).encode()).hexdigest()
    return {
        "schema": "yggdrasil.contrib.aai08p.bridge-source-mechanical.v1",
        "source_commit": UPSTREAM,
        "environment": "ns_gym/Bridge-v0",
        "upstream_wrapper":"NSBridgeWrapper",
        "mechanical_worlds":len(pairs),
        "same_action_data_before_change":True,
        "official_transition_change_affects_real_reward":True,
        "notifications_to_agent":False,
        "official_info_field_ground_truth_not_exposed_to_agent":True,
        "source_seed_reproducibility_with_one_hot_transition_distributions":True,
        "stochastic_seed_reproducibility": "UNVERIFIED: original Bridge.step uses global numpy.random.choice",
        "scientific_primary_consumed":False,
        "native_model_changed":False,
        "trace_sha256":digest
    }


if __name__=="__main__":
    print(json.dumps(mechanical(),indent=2,sort_keys=True))

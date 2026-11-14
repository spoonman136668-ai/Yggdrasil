"""AAI-08P stochastic RNG custody, external NS-Gym Bridge source unmodified.

Upstream Bridge.step uses np.random.choice on the process-global RNG. A
scoped seed-and-restore guard makes one exact seeded experimental rollout
reproducible without leaking or corrupting other process-global consumers.
Only reserved mechanical seeds; no science primary, learned agent or model.
"""
import hashlib
import json

import gymnasium as gym
import ns_gym
import numpy as np
from ns_gym.schedulers import DiscreteScheduler
from ns_gym.update_functions import DistributionStepWiseUpdate
from ns_gym.wrappers import NSBridgeWrapper

UPSTREAM_COMMIT = "127df4b714fe4fcf680721d8e9278a96090acd7e"
SEEDS = tuple(range(996100, 996116))
ACTIONS = (2, 0, 2, 2, 2, 0, 2, 0)
INITIAL = (1.0, 0.0, 0.0)
STOCHASTIC = (0.15, 0.70, 0.15)


def rng_state_equal(first, second):
    return (first[0] == second[0]
            and np.array_equal(first[1], second[1])
            and first[2:] == second[2:])


def rollout(seed, change):
    """Everything stochastic is enclosed in one restored global-RNG guard."""
    saved = np.random.get_state()
    env = None
    try:
        np.random.seed(seed)
        upstream = gym.make("ns_gym/Bridge-v0")
        scheduler = DiscreteScheduler({3} if change else {999})
        updater = DistributionStepWiseUpdate(scheduler,[list(STOCHASTIC)])
        env = NSBridgeWrapper(
            upstream, tunable_params={"P": updater},
            initial_prob_dist=list(INITIAL), change_notification=False,
            delta_change_notification=False, scalar_reward=True)
        obs, _diagnostic = env.reset(seed=seed)
        assert int(obs["state"]) >= 0
        assert obs["env_change"]["P"] == 0
        assert obs["delta_change"]["P"] == 0
        trace = [{"state": int(obs["state"]), "reward": 0.0, "done": False}]
        for action in ACTIONS:
            obs, reward, terminal, truncated, _diagnostic = env.step(action)
            assert obs["env_change"]["P"] == 0
            assert obs["delta_change"]["P"] == 0
            assert np.isfinite(float(reward))
            trace.append({"state": int(obs["state"]),
                          "reward": float(reward),
                          "done": bool(terminal or truncated)})
            if terminal or truncated:
                break
        return trace
    finally:
        if env is not None:
            env.close()
        np.random.set_state(saved)
        assert rng_state_equal(saved, np.random.get_state())


def main():
    cases = []
    for seed in SEEDS:
        unchanged = rollout(seed, False)
        shifted = rollout(seed, True)
        assert unchanged == rollout(seed, False), ("stationary", seed)
        assert shifted == rollout(seed, True), ("stochastic-shift", seed)
        assert unchanged[:4] == shifted[:4], ("prefix drift", seed)
        assert len(shifted) >= 5 and len(unchanged) >= 5
        cases.append({"seed": seed, "stationary": unchanged, "shifted": shifted})
    assert len({json.dumps(x["shifted"], sort_keys=True) for x in cases}) >= 3, (
        "Stochastic variations were not observed across distinct reserved seeds")
    effects = sum(x["stationary"] != x["shifted"] for x in cases)
    assert effects >= 8, ("Shift effect underpowered in reserved mechanical seeds",effects)
    receipt = hashlib.sha256(json.dumps(cases,sort_keys=True,
        separators=(",",":")).encode("utf-8")).hexdigest()
    return {
        "schema":"yggdrasil.contrib.aai08p.stochastic-rng-custody.v1",
        "official_source_commit":UPSTREAM_COMMIT,
        "number_of_reserved_mechanical_cases":len(cases),
        "stochastic_shift_changes_executed_outcome_cases":effects,
        "replay_identical_when_scoped_seed_reapplied":True,
        "global_numpy_rng_original_state_restored":True,
        "same_actions_and_states_before_shift":True,
        "nontrivial_stochastic_outcomes":True,
        "official_source_edited":False,
        "hidden_transition_data_to_learner":False,
        "scientific_primary_consumed":False,
        "agent_model_trained":False,
        "limitation":"We qualify a scoped experiment harness with legacy NumPy RNG, not native env.reset stochastic custody. No randomized-science training/evaluation yet.",
        "trace_sha256":receipt,
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, indent=2))

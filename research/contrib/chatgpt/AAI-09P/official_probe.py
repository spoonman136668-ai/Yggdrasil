"""AAI-09P: one-hot reserved-seed official NS-Gym Bridge mechanics only.

No future scientific seeds and no learned model. Uses only public observation
and actual upstream env.step outcomes. Upstream git SHA pinned by workflow.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from headroom import MAP, ACTIONS, source_basis, deterministic_bytes

MECHANICAL_SEEDS=(887900,887901,887902,887903)
BASIS=((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))

def official_case(seed,action,law):
    import gymnasium as gym
    import ns_gym
    import numpy as np
    from ns_gym.schedulers import DiscreteScheduler
    from ns_gym.update_functions import DistributionStepWiseUpdate
    from ns_gym.wrappers import NSBridgeWrapper
    saved=np.random.get_state()
    env=None
    try:
        np.random.seed(seed)
        env=NSBridgeWrapper(
            gym.make("ns_gym/Bridge-v0"),
            tunable_params={"P":DistributionStepWiseUpdate(DiscreteScheduler({3}),[list(law)])},
            initial_prob_dist=[1.,0.,0.],
            change_notification=False,delta_change_notification=False,
            scalar_reward=True,persistent_params=False)
        observation,_discarded_info=env.reset(seed=seed)
        assert int(observation["state"])==20
        for expected,command in zip((21,20,21),(2,0,2)):
            observation,reward,ended,truncated,_discarded_info=env.step(command)
            assert int(observation["state"])==expected
            assert float(reward)==0 and not ended and not truncated
            assert observation["env_change"]["P"]==0
            assert observation["delta_change"]["P"]==0
        prior_state=int(observation["state"])
        observation,reward,ended,truncated,_discarded_info=env.step(action)
        assert prior_state==21
        assert observation["env_change"]["P"]==0
        assert observation["delta_change"]["P"]==0
        assert int(observation["relative_time"])==4
        return {
            "after_state":int(observation["state"]),
            "reward":float(reward),
            "terminal":bool(ended or truncated),
        }
    finally:
        if env is not None:
            env.close()
        np.random.set_state(saved)
        restored=np.random.get_state()
        assert saved[0]==restored[0] and np.array_equal(saved[1],restored[1]) and saved[2:]==restored[2:]

def run():
    basis=source_basis()
    rows=[]
    for seed in MECHANICAL_SEEDS:
        outcome={"seed":seed}
        for name,action in ACTIONS.items():
            cases=[official_case(seed,action,law) for law in BASIS]
            for i,row in enumerate(cases):
                assert row["after_state"]==basis[name]["states"][i],(name,i,row,basis)
                assert row["reward"]==basis[name]["rewards"][i],(name,i,row,basis)
                assert row["terminal"] is (row["reward"]!=0)
                assert official_case(seed,action,BASIS[i])==row
            outcome[name]=cases
        rows.append(outcome)
    canonical=deterministic_bytes(rows)
    return {
        "schema":"yggdrasil.contrib.aai09p.official-mechanical.v1",
        "source_repo":"scope-lab-vu/ns_gym",
        "source_git_sha":"127df4b714fe4fcf680721d8e9278a96090acd7e",
        "seeds":list(MECHANICAL_SEEDS),
        "worlds_per_onehot_case":len(MECHANICAL_SEEDS),
        "cases":len(MECHANICAL_SEEDS)*len(ACTIONS)*len(BASIS),
        "all_basis_rewards_and_states_source_agree":True,
        "no_scientific_first_use":True,
        "trace_sha256":hashlib.sha256(canonical).hexdigest(),
        "results":rows,
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))

"""Exploratory source-free repeated episode retention and action-custody stress.
Does not import the third-party causal_gym source or execute a real MDP.
"""
import hashlib
import importlib.util
import random
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
PARENT = HERE.parent/'CVH-01'
if not PARENT.is_dir():
    PARENT = HERE.parent/'cvh01'/'CVH-01'
sys.path.insert(0,str(PARENT))
from public_policy import PublicEarnedPolicy
from strong_conventional import batch_public_returns

SOURCE=HERE.parent/'FKP-24'/'native_public_mdp.py'
BLOB='4424eadef179996ff491911efadfbe4e07761062'
raw=SOURCE.read_bytes()
assert hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\x00'+raw).hexdigest()==BLOB
spec=importlib.util.spec_from_file_location('cvh02_fkp24_retention',SOURCE)
adapter=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=adapter
spec.loader.exec_module(adapter)

class NoInfo:
    def __getattribute__(self,k):
        raise AssertionError('CVH02_SOURCE_PRIVATE_ACCESSED')

class MockEpisode:
    def __init__(self, idx):
        self.idx=idx
        self.state=idx%2
        self.actions=[]
        self.closed=False
        self.length=1+((idx*13+7)%30)

    def reset(self, *, seed):
        assert seed in adapter.MECHANICAL_PUBLIC_SEEDS
        self.state=self.idx%2
        return self.state,NoInfo()

    def do(self, fn):
        action=fn(self.state)
        assert type(action) is int and action in (0,1)
        self.actions.append(action)
        # Two-step public earned consequence; exact reward only after action.
        reward=self.actions[-3] if len(self.actions)>=3 else 0
        self.state=(self.state ^ action ^ (self.idx%2))
        ended=len(self.actions)>=self.length
        return self.state,reward,ended,False,NoInfo()

    def close(self): self.closed=True

class CVH02RetentionStress(unittest.TestCase):
    def test_240_completed_mock_episodes_source_blind_and_cold(self):
        policy=PublicEarnedPolicy(min_support=2)
        uninterrupted=PublicEarnedPolicy(min_support=2)
        seen=[]
        total=0
        peak=0
        for idx in range(240):
            env=MockEpisode(idx)
            record=adapter.public_mechanical_episode(lambda:env,policy,seed=996100,max_actions=32)
            self.assertTrue(record['ended_by_source'])
            self.assertTrue(env.closed)
            self.assertEqual(record['physical_do_actions'],env.length)
            self.assertEqual(record['budget_exhausted'],False)
            self.assertEqual(record['forbidden_info_passed_to_policy'],False)
            self.assertEqual(record['counterfactuals_used'],False)
            reference_env=MockEpisode(idx)
            ref=adapter.public_mechanical_episode(lambda:reference_env,uninterrupted,seed=996100,max_actions=32)
            self.assertEqual(record['public_transitions_sha256'],ref['public_transitions_sha256'])
            self.assertEqual(policy.snapshot(),uninterrupted.snapshot())
            events=[adapter.PublicConsequence(**r) for r in record['public_transitions']]
            seen.extend(events)
            total+=len(events)
            if idx%12==0 or idx==239:
                counts,returns=batch_public_returns(seen)
                self.assertEqual(policy.memory.count,counts)
                self.assertEqual(policy.memory.total,returns)
            blob=policy.snapshot()
            peak=max(peak,len(blob))
            reloaded=PublicEarnedPolicy.restore(blob)
            self.assertEqual(reloaded.snapshot(),blob)
            policy=reloaded
        self.assertEqual(total,3720)
        self.assertEqual(policy.memory.seen,total)
        self.assertEqual(sum(policy.attempts),total)
        self.assertEqual(policy.memory.pending,[])
        print('CVH02_STRESS_TOTAL_PER_POLICY',total,'TWO_POLICIES_SOURCE_FREE_CALLBACKS',2*total,'PEAK_SNAPSHOT_BYTES',peak)

if __name__=='__main__': unittest.main()

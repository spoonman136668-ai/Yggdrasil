"""Run inherited byte-pinned FKP24 adapter against MOCK environment, never CausalGym."""
from __future__ import annotations
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
FKP=HERE.parent/'FKP-24'/'native_public_mdp.py'
if not FKP.exists():
    FKP=HERE.parent/'cvh01'/'FKP-24'/'native_public_mdp.py'
BLOB='4424eadef179996ff491911efadfbe4e07761062'


def _git_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest()


class TestInheritedExactAdapter(unittest.TestCase):
    def test_exact_fkp24_real_adapter_mock_source_only(self):
        self.assertTrue(FKP.is_file(), 'Exact inherited FKP24 adapter is required; do not skip')
        self.assertEqual(_git_blob(FKP.read_bytes()), BLOB, 'Exact inherited FKP24 adapter Git blob drift')
        spec=importlib.util.spec_from_file_location('cvh02_exact_original_fkp24_adapter',FKP)
        adapter=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=adapter
        spec.loader.exec_module(adapter)
        from public_policy import PublicEarnedPolicy
        class Forbidden:
            def __getattribute__(self,name):
                raise AssertionError('SOURCE_PRIVATE_METADATA_READ')
        class OnlyMock:
            def __init__(self):
                self.state=0
                self.calls=0
                self.closed=False
            def reset(self,*,seed):
                self.state=0
                self.calls=0
                return 0,Forbidden()
            def do(self,callback):
                self.calls+=1
                chosen=callback(self.state)
                self.state=(self.state+int(chosen)+1)%2
                return self.state,int(chosen==1),False,self.calls==5,Forbidden()
            def close(self):self.closed=True
        policy=PublicEarnedPolicy(min_support=2)
        env=OnlyMock()
        receipt=adapter.public_mechanical_episode(lambda:env,policy,seed=996100)
        self.assertEqual(receipt['physical_do_actions'],5)
        self.assertFalse(receipt['counterfactuals_used'])
        self.assertFalse(receipt['forbidden_info_passed_to_policy'])
        self.assertEqual(env.calls,5)
        self.assertTrue(env.closed)
        self.assertEqual(policy.memory.seen,5)
        env2=OnlyMock()
        receipt2=adapter.public_mechanical_episode(lambda:env2,policy,seed=996101)
        self.assertEqual(receipt2['physical_do_actions'],5)
        self.assertEqual(policy.memory.seen,10)
        self.assertEqual(policy.episode_history,[])

if __name__=='__main__':unittest.main()

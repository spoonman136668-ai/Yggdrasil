"""Independent surface checks for frozen CKAD19 sidecar."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

spec=importlib.util.spec_from_file_location('ckad19_campaign',Path(__file__).with_name('campaign.py'))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class CKAD19Checks(unittest.TestCase):
    def test_rule_marginals_action_effect_and_family_set(self):
        self.assertEqual(len(mod.RULES),12)
        for rule in mod.RULES:
            self.assertEqual(sum(mod.oracle(rule,x) for x in range(16)),8)
            for ctx in range(8):
                self.assertEqual(mod.oracle(rule,ctx)+mod.oracle(rule,ctx|8),1)

    def test_frozen_source_never_uses_held_rule(self):
        for seed in mod.SEEDS:
            for fam in (0,1):
                for held in range(6):
                    withheld=mod.RULES[6*fam+held]
                    calls=[]
                    underlying=mod.oracle
                    def observed(rule,x):
                        calls.append((rule,x))
                        return underlying(rule,x)
                    with mock.patch.object(mod,'oracle',side_effect=observed):
                        tasks=mod.train_case(seed,fam,held)
                    self.assertNotIn(withheld,{r for r,x in calls})
                    self.assertEqual(len(tasks),4)
                    self.assertTrue(all(len(t)==5 and len({x for x,y in t})==5 for t in tasks))
                    self.assertEqual(tasks,mod.train_case(seed,fam,held))

    def test_checkpoint_is_public_evidence_only_and_tamper_denied(self):
        tasks=mod.train_case(101,0,0)
        raw=mod.encode_state(tasks)
        body=json.loads(raw)
        self.assertEqual(set(body),{'schema','tasks','prior','accepted_native','scientific_pass'})
        self.assertEqual((tasks,mod.infer_family(tasks)),mod.restore_state(raw,mod.digest(raw)))
        for candidate in (raw[:-1]+b'!',raw+b' '):
            with self.assertRaises(ValueError):
                mod.restore_state(candidate,mod.digest(raw))

    def test_exact_bayesian_control_and_intervention_replay(self):
        tasks=mod.train_case(202,1,3)
        p=mod.infer_family(tasks)
        obs=[]
        for _ in range(4):
            for x in range(16):
                self.assertAlmostEqual(mod.forecast(p,obs,x),mod.exact_control(p,obs,x),places=12)
            x=mod.select(p,obs,seed=202,random_query=False)
            self.assertNotIn(x,[a for a,_ in obs])
            obs.append([x,mod.oracle(mod.RULES[9],x)])
        self.assertEqual(len({x for x,_ in obs}),4)

if __name__=='__main__':unittest.main()

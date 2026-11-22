"""Toy-only independent reference tests; no CKAD26 primary held worlds."""
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ckad26_toy_audit',HERE/'independent_audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def events(count=16):
    # Public witness bits, deliberately non-primary, deterministic toy identities.
    return [[audit.sha(audit.canonical(['ckad26-toy',index])),
             [[index%2,0],[index%2,1]],index%2,(index//2)%2,
             (index//4)%2,(index//8)%2] for index in range(count)]


class RefreshReferenceTests(unittest.TestCase):
    def test_share_floor_normalization_and_zero_share(self):
        prefix = events()
        old = audit.Mixture(prefix,novel=True)
        share = audit.RefreshMixture(prefix)
        zero = audit.RefreshMixture(prefix,rate=Fraction())
        event = events(17)[-1]
        old.add(event); share.add(event); zero.add(event)
        prior = audit.prior_weights(share)
        self.assertEqual(zero.weights,old.weights)
        self.assertEqual(sum(share.weights),1)
        self.assertEqual(share.weights,[(31*w+p)/32 for w,p in zip(old.weights,prior)])
        self.assertTrue(all(w>=p/32 for w,p in zip(share.weights,prior)))
        self.assertEqual(share.models[-1].events,[event])

    def test_prior_only_still_learns_new_member(self):
        mixture = audit.RefreshMixture(events(),rate=Fraction(1))
        before = audit.sha(audit.canonical(mixture.models[-1].events))
        mixture.add(events(17)[-1])
        self.assertEqual(mixture.weights,audit.prior_weights(mixture))
        self.assertNotEqual(before,audit.sha(audit.canonical(mixture.models[-1].events)))

    def test_activation_preserves_predictive_state_and_prequential_score(self):
        monitor = audit.previous.Monitor(events())
        monitor.add(events(17)[-1])
        before = copy.deepcopy(monitor.mixture.info())
        score = monitor.score
        audit.activate(monitor)
        self.assertEqual(before,monitor.mixture.info())
        self.assertEqual(score,monitor.score)
        event = events(18)[-1]
        _,(view,_),first,state,second,reward = event
        p = monitor.mixture.forecast(view,first)
        q = monitor.mixture.forecast(view,first,state,second)
        likelihood = (p if state else 1-p)*(q if reward else 1-q)
        expected = max(Fraction(1),score/(4*likelihood))
        monitor.add(event)
        self.assertEqual(expected,monitor.score)
        self.assertEqual(monitor.refresh_start,17)

    def test_checkpoint_v5_and_legacy_retention(self):
        ledger = events()
        replay = audit.previous.previous.previous.prior.prior.replay(ledger,True)
        monitor = audit.previous.Monitor(ledger)
        parent = {'legacy':'untouched','experience_ascii':'unused'}
        old = audit.stream_checkpoint(replay,parent,monitor)
        self.assertEqual(json.loads(json.loads(old)['experience_ascii'])['schema'],
                         'yggdrasil.ckad.native-episode-experience.v4')
        audit.activate(monitor)
        raw = audit.stream_checkpoint(replay,parent,monitor)
        decoded = json.loads(raw)
        packet = json.loads(decoded['experience_ascii'])
        self.assertEqual(decoded['legacy'],'untouched')
        self.assertEqual(packet['refresh_start'],16)
        self.assertEqual(packet['refresh_rate'],[1,32])
        self.assertEqual(packet['episodes'],ledger)
        self.assertNotEqual(raw,old)
        self.assertEqual(raw,audit.stream_checkpoint(replay,parent,copy.deepcopy(monitor)))

    def test_alarm_reopening_preserves_refresh_rule(self):
        monitor = audit.activate(audit.previous.Monitor(events()))
        # Synthetic score injection exercises control flow only, no primary tuning.
        for event in events(24)[16:23]:
            monitor.add(event)
        monitor.score = Fraction(10**8)
        monitor.add(events(24)[23])
        self.assertTrue(monitor.detections)
        self.assertEqual(monitor.mixture.rate,Fraction(1,32))
        self.assertEqual(monitor.refresh_start,16)
        self.assertEqual(monitor.score,1)
        frozen_alarm = audit.activate(audit.previous.Monitor(events()),alarm=False)
        frozen_alarm.score = Fraction(10**8)
        for event in events(24)[16:]:
            frozen_alarm.add(event)
        self.assertEqual(frozen_alarm.detections,[])
        self.assertEqual(frozen_alarm.mixture.start,16)

    def test_exact_thresholds_and_resealed_gate_tamper(self):
        cases = []
        for seed in (101,202,303):
            rows = []
            for count in range(0,193,16):
                cells = {arm:{'episodes':100,'reward_sum':80,'pooled_brier':[1,5]} for arm in audit.ARMS}
                cells['native_refresh']['reward_sum']=85
                cells['exact_refresh']['reward_sum']=85
                rows.append({'count':count,'evaluation':cells})
            cases.append({'seed':seed,'stream':rows})
        gates,metrics = audit.development(cases)
        self.assertEqual(len(gates),9)
        self.assertTrue(all(gates.values()))
        result = {'seeds':cases,'development_gates':gates,'development_metrics':metrics,
                  'development_pass':True,'classification':'DEVELOPMENT_GO'}
        audit.verify_gates(result)
        result['development_gates']['seed101_gain_vs_product']=False
        with self.assertRaisesRegex(RuntimeError,'FROZEN_METRICS_GATES'):
            audit.verify_gates(result)
        cases[0]['stream'][0]['evaluation']['native_refresh']['reward_sum']=84
        gates,_ = audit.development(cases)
        self.assertFalse(gates['seed101_gain_vs_product'])
        self.assertTrue(gates['per_seed_whole_curve_no_loss'])

    def test_stable_keeps_scientific_parameters_and_native_import_fence(self):
        self.assertEqual(audit.stable({'refresh_rate':[1,32],'whole_wall_seconds':2,
                                     'resource_accounting':{'cpu_seconds':2}}),{'refresh_rate':[1,32]})
        # Discovery imports sibling native tests into this interpreter. Check the
        # auditor's own import boundary in a clean process, as qualification does.
        code = ("import importlib.util,sys; "
                "spec=importlib.util.spec_from_file_location('isolated_audit',sys.argv[1]); "
                "module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); "
                "assert not any(n=='yggdrasil' or n.startswith('yggdrasil.') for n in sys.modules)")
        subprocess.run([sys.executable,'-B','-c',code,str(HERE/'independent_audit.py')],check=True)


if __name__=='__main__':
    unittest.main()

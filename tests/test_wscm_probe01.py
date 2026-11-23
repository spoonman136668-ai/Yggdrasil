"""Non-scored, source-free probe contract tests on previously investigated cell."""
import hashlib
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from fractions import Fraction
import json
import unittest

from yggdrasil.native_episode_experience import NativeEpisodeExperience

ROOT = Path(__file__).resolve().parents[1]
VER_PATH = ROOT/'research/contrib/chatgpt/WSCM-VERSIONED-02/versioned_transition.py'
PROBE_PATH = ROOT/'research/contrib/chatgpt/WSCM-PROBE-01/probe.py'

def loaded(name,path):
    spec=spec_from_file_location(name,path)
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

versioned=loaded('wscm_v2_probe_test',VER_PATH)
probe=loaded('wscm_probe',PROBE_PATH)


def episode(i, ctx, state, action=0):
    return (hashlib.sha256(f'old-synthetic-repair/{i}'.encode()).hexdigest(),
            ((ctx,0),(ctx,1)),
            {'s1':ctx,'x1':action,'s2':state,'x2':0,'y':0})


def fixture():
    obj=versioned.VersionedNativeTransition(NativeEpisodeExperience())
    for i in range(48):
        obj=obj.observe(*episode(i,i%2,i%2))
    for i in range(48,51):
        obj=obj.observe(*episode(i,0,1))
    assert len(obj.versions())==1
    return obj, obj.versions()[0]['version_id']


class EvidenceProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source,cls.eid=fixture()

    def fresh(self):
        return probe.WitnessCausalProbe(self.source,self.eid)

    def test_old_and_reset_are_exact_original_counts(self):
        obj=self.fresh()
        self.assertEqual(obj.hypotheses((0,0),0),(Fraction(1,26),Fraction(4,5)))
        self.assertEqual(obj.read_prob if hasattr(obj,'read_prob') else obj.forecast((0,0),0),Fraction(109,260))
        self.assertEqual(obj.posterior_old,Fraction(1,2))

    def test_probe_action_uses_observable_contrast_only(self):
        obj=self.fresh()
        self.assertEqual(obj.choose((0,0)),(0,True))
        self.assertEqual(obj.choose((1,0)),(0,False))
        self.assertEqual(obj.hypotheses((0,0),1)[0],obj.hypotheses((0,0),1)[1])
        self.assertEqual(obj.hypotheses((1,0),0)[0],obj.hypotheses((1,0),0)[1])

    def test_evidence_updates_without_stage_inputs(self):
        obj=self.fresh()
        before=obj.forecast((0,0),0)
        result=obj.witness(*episode(51,0,1))
        self.assertLess(result.posterior_old,obj.posterior_old)
        self.assertGreater(result.forecast((0,0),0),before)
        self.assertEqual(result.counts,(1,0))
        self.assertEqual(obj.counts,(0,0))

    def test_unidentifiable_context_abstains_without_updating_weights(self):
        obj=self.fresh()
        result=obj.witness(*episode(51,1,1))
        self.assertEqual(result.posterior_old,obj.posterior_old)
        self.assertEqual(result.counts,(0,1))
        self.assertEqual(result.choose((1,0)),(0,False))

    def test_action_mismatch_fails_before_training(self):
        obj=self.fresh()
        before=obj.original_native.checkpoint()
        with self.assertRaisesRegex(ValueError,'PROBE_ACTION_OR_ROW'):
            obj.witness(*episode(51,0,1,action=1))
        self.assertEqual(obj.original_native.checkpoint(),before)

    def test_same_event_id_replay_rejected_by_probe(self):
        obj=self.fresh().witness(*episode(51,0,1))
        with self.assertRaisesRegex(ValueError,'PROBE_NO_NEW_WITNESS'):
            obj.witness(*episode(51,0,1))

    def test_conflicting_event_rejected_by_native(self):
        obj=self.fresh().witness(*episode(51,0,1))
        with self.assertRaises(ValueError):
            obj.witness(*episode(51,0,0))

    def test_checkpoint_cold_parity(self):
        obj=self.fresh().witness(*episode(51,0,0))
        raw=obj.checkpoint()
        recovered=probe.WitnessCausalProbe.restore(*raw,versioned.VersionedNativeTransition,
                                                  expected_state_sha256=hashlib.sha256(raw[2]).hexdigest())
        self.assertEqual(recovered.checkpoint(),raw)
        self.assertEqual(recovered.posterior_old,obj.posterior_old)
        self.assertEqual(recovered.choose((0,0)),obj.choose((0,0)))
        self.assertEqual(recovered.forecast((0,0),0),obj.forecast((0,0),0))
        self.assertEqual(recovered.counts,obj.counts)

    def test_tampered_posterior_checkpoint_rejected(self):
        obj=self.fresh()
        raw,man,st=obj.checkpoint()
        value=json.loads(st)
        value['posterior_old']=[3,4]
        with self.assertRaisesRegex(ValueError,'PROBE_COLD_INPUT_OR_PIN'):
            probe.WitnessCausalProbe.restore(raw,man,probe.canonical(value),versioned.VersionedNativeTransition,
                                                 expected_state_sha256=hashlib.sha256(st).hexdigest())

    def test_cold_source_binding_rejects_wrong_native(self):
        obj=self.fresh()
        raw,man,st=obj.checkpoint()
        with self.assertRaisesRegex(ValueError,'PROBE_COLD_CUSTODY'):
            probe.WitnessCausalProbe.restore(raw+b'x',man,st,versioned.VersionedNativeTransition,
                                                 expected_state_sha256=hashlib.sha256(st).hexdigest())

    def test_prohibits_invalid_view_and_bits(self):
        obj=self.fresh()
        for bad in ((2,0), [0,0], (0,0,0), (True,0)):
            with self.assertRaises(ValueError):
                obj.choose(bad)
        with self.assertRaises(ValueError):
            obj.forecast((0,0),True)

    def test_original_state_unmutated_by_reads(self):
        obj=self.fresh()
        state=obj.original_native.checkpoint()
        for _ in range(10):
            obj.forecast((0,0),0)
            obj.hypotheses((1,0),0)
            obj.choose((1,0))
        self.assertEqual(obj.original_native.checkpoint(),state)


if __name__ == '__main__': unittest.main()

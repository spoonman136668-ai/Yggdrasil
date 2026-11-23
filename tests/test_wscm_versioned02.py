"""Source-free qualifying tests for real native code with copy-on-write versions."""
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import unittest
from fractions import Fraction

from yggdrasil.native_episode_experience import NativeEpisodeExperience

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/contrib/chatgpt/WSCM-VERSIONED-02/versioned_transition.py'
spec = spec_from_file_location('wscm_versioned_transition', SOURCE)
api = module_from_spec(spec)
spec.loader.exec_module(api)


def episode(i, *, context, state, action=0):
    identifier = hashlib.sha256(f'wscm-v2/{i}'.encode()).hexdigest()
    return identifier, ((context, 0), (context, 1)), {
        's1': context, 'x1': action, 's2': state, 'x2': 0, 'y': context}


def build(recovery=0):
    obj = api.VersionedNativeTransition(NativeEpisodeExperience())
    for i in range(48):
        obj = obj.observe(*episode(i, context=i%2, state=i%2))
    before = obj.checkpoint()
    for i in range(48, 51):
        obj = obj.observe(*episode(i, context=0, state=1))
    repair_id = episode(50, context=0, state=1)[0]
    after = obj.checkpoint()
    for i in range(51, 51 + recovery):
        obj = obj.observe(*episode(i, context=0, state=0))
    return obj, repair_id, before, after


class VersionedTransitionTests(unittest.TestCase):
    def test_original_destructive_repair_now_has_immutable_old_branch(self):
        obj, eid, before, after = build()
        self.assertEqual(obj.original_native._transition._counts[0][0], [0,3])
        self.assertEqual(len(obj.versions()), 1)
        self.assertEqual(obj.versions()[0]['old_counts'], [24,0])
        self.assertEqual(obj.versions()[0]['reset_counts'], [0,3])
        self.assertEqual(obj.read_transition((0,0),0,version_id=eid), Fraction(1,26))
        self.assertEqual(obj.read_transition((0,0),0), Fraction(4,5))
        self.assertNotEqual(before, after)

    def test_immutable_historical_function_survives_eight_old_pattern_events(self):
        obj, eid, _, _ = build(8)
        self.assertEqual(obj.read_transition((0,0),0,version_id=eid), Fraction(1,26))
        self.assertEqual(obj.read_transition((0,0),0), Fraction(4,13))
        self.assertEqual(obj.versions()[0]['old_counts'], [24,0])
        self.assertEqual(len(obj.versions()), 1)

    def test_native_cold_and_sidecar_cold_restore_byte_identity(self):
        obj,eid,_,_=build(8)
        raw, manifest = obj.checkpoint()
        cold = api.VersionedNativeTransition.restore(raw,manifest)
        self.assertEqual(cold.checkpoint(), (raw,manifest))
        self.assertEqual(cold.read_transition((0,0),0,version_id=eid), Fraction(1,26))
        self.assertEqual(cold.read_transition((0,0),0), Fraction(4,13))
        self.assertEqual(cold.consolidate().checkpoint(), (raw,manifest))

    def test_normal_native_default_remains_unchanged(self):
        obj,eid,_,_=build()
        native = obj.original_native
        self.assertEqual(obj.read_transition((0,0),0), native.forecast((0,0),0,full=True))
        before=native.checkpoint()
        for _ in range(5):
            obj.read_transition((0,0),0,version_id=eid)
            obj.versions()
            obj.manifest()
        self.assertEqual(native.checkpoint(),before)

    def test_version_access_requires_real_last_witness_and_public_address(self):
        obj,eid,_,_=build()
        for bad,kwargs,error in [
            ("wrong id",{'version_id':'0'*64},'VERSIONED_WITNESS_OR_ADDRESS_NOT_FOUND'),
            ("wrong slot",{'version_id':eid,'public_view':(1,0)},'VERSIONED_WITNESS_OR_ADDRESS_NOT_FOUND'),
            ("wrong action",{'version_id':eid,'first_action':1},'VERSIONED_WITNESS_OR_ADDRESS_NOT_FOUND'),
            ("invalid id",{'version_id':'not-id'},'VERSIONED_ID_INVALID'),
        ]:
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,error):
                obj.read_transition(kwargs.pop('public_view',(0,0)), kwargs.pop('first_action',0),**kwargs)

    def test_native_idempotent_same_witness_never_creates_second_version(self):
        obj,eid,_,_=build()
        replay=obj.observe(*episode(50,context=0,state=1))
        self.assertIs(replay,obj)
        self.assertEqual(replay.versions(),obj.versions())

    def test_replayed_witness_with_conflicting_outcome_is_rejected(self):
        obj,eid,_,_=build()
        with self.assertRaises(ValueError):
            obj.observe(*episode(50,context=0,state=0))

    def test_restore_tamper_wrong_checksum_refused(self):
        obj,eid,_,_=build()
        raw,man=obj.checkpoint()
        forged=json.loads(man)
        forged['native_checkpoint_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'VERSIONED_MANIFEST_CUSTODY'):
            api.VersionedNativeTransition.restore(raw,api._canonical(forged))

    def test_restore_tamper_historical_counts_refused(self):
        obj,eid,_,_=build()
        raw,man=obj.checkpoint()
        forged=json.loads(man)
        forged['versions'][0]['old_counts']=[22,2]
        with self.assertRaisesRegex(ValueError,'VERSIONED_REPAIR_HISTORY_MISMATCH'):
            api.VersionedNativeTransition.restore(raw,api._canonical(forged))

    def test_restore_rejects_noncanonical_or_corrupt_native_bytes(self):
        obj,eid,_,_=build()
        raw,man=obj.checkpoint()
        with self.assertRaisesRegex(ValueError,'VERSIONED_MANIFEST_CUSTODY'):
            api.VersionedNativeTransition.restore(raw,man+b' ')
        with self.assertRaisesRegex(ValueError,'VERSIONED_MANIFEST_CUSTODY'):
            api.VersionedNativeTransition.restore(raw+b'x',man)

    def test_caller_cannot_mutate_original_frozen_version_by_reading(self):
        obj,eid,_,_=build()
        views=obj.versions(); views[0]['old_counts'][0]=0
        self.assertEqual(obj.read_transition((0,0),0,version_id=eid),Fraction(1,26))

    def test_unlearned_projection_fails_closed(self):
        model=api.VersionedNativeTransition(NativeEpisodeExperience())
        with self.assertRaisesRegex(ValueError,'VERSIONED_PROJECTION_UNLEARNED'):
            model.read_transition((0,0),0)

    def test_no_repair_does_not_fabricate_memory(self):
        obj=api.VersionedNativeTransition(NativeEpisodeExperience(repair=False))
        for i in range(51):
            ctx=i%2 if i<48 else 0
            state=ctx if i<48 else 1
            obj=obj.observe(*episode(i,context=ctx,state=state))
        self.assertEqual(obj.versions(),[])
        with self.assertRaisesRegex(ValueError,'VERSIONED_WITNESS_OR_ADDRESS_NOT_FOUND'):
            obj.read_transition((0,0),0,version_id=episode(50,context=0,state=1)[0])

    def test_authentic_archived_native_has_no_versions(self):
        import os
        from pathlib import Path
        path=os.environ.get('WSCM_ARCHIVED_JOINT_PATH')
        if not path:
            self.skipTest('Explicit original archived fixture absent; do not claim PASS')
        raw=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8')
        joint=json.loads(raw)
        node=json.loads(joint['native_ascii'])
        episode_raw=node['experience_ascii'].encode('ascii')
        original=NativeEpisodeExperience.restore(episode_raw,hashlib.sha256(episode_raw).hexdigest())
        self.assertEqual(len(original._ledger),1025)
        obj=api.VersionedNativeTransition(original)
        self.assertEqual(obj.versions(),[])
        ckpt,manifest=obj.checkpoint()
        self.assertEqual(api.VersionedNativeTransition.restore(ckpt,manifest).versions(),[])

if __name__=='__main__':
    unittest.main()

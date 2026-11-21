"""G41 source-free migration controls. No original-world action or science claim."""
from hashlib import sha256
import json
import os
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import (
    NativeEpisodeExperience, SCHEMA, GROWTH_SCHEMA, EXTENDED_SCHEMA,
    MAX_EPISODES, GROWN_MAX_EPISODES, EXTENDED_MAX_EPISODES,
    MAX_CHECKPOINT_BYTES, EXTENDED_MAX_CHECKPOINT_BYTES,
)


def dev_event(i):
    identifier = sha256(("g41-source-free-%06d" % i).encode("ascii")).hexdigest()
    return (identifier, ((0, 0), (0, 0)), 0, 0, 0, 0)


def saturated_legacy():
    obj=NativeEpisodeExperience()
    for i in range(MAX_EPISODES):
        obj._append(dev_event(i))
    return obj.begin_stream().enable_context_refresh()


class G41NativeCapacityTests(unittest.TestCase):
    def test_v1_checkpoint_byte_compatibility_and_unsaturated_reject(self):
        old=NativeEpisodeExperience()
        raw=old.checkpoint()
        self.assertEqual(json.loads(raw)['schema'],SCHEMA)
        self.assertEqual(NativeEpisodeExperience.restore(raw,digest(raw)).checkpoint(),raw)
        with self.assertRaisesRegex(ValueError,'EPISODE_GROWTH_PARENT'):
            old.extend_witness_capacity()

    def test_v6_saturation_to_v7_and_cold_replay(self):
        obj=saturated_legacy().extend_witness_capacity()
        raw_v6=obj.checkpoint()
        self.assertEqual(json.loads(raw_v6)['schema'],GROWTH_SCHEMA)
        self.assertEqual(NativeEpisodeExperience.restore(raw_v6,digest(raw_v6)).checkpoint(),raw_v6)
        with self.assertRaisesRegex(ValueError,'EPISODE_GROWTH_PARENT'):
            obj.extend_witness_capacity()
        for i in range(MAX_EPISODES,GROWN_MAX_EPISODES):
            obj._accept(dev_event(i))
        with self.assertRaisesRegex(ValueError,'EPISODE_CAPACITY'):
            obj.observe(dev_event(GROWN_MAX_EPISODES)[0],((0,0),(0,0)),
                        {'s1':0,'x1':0,'s2':0,'x2':0,'y':0})
        ext=obj.extend_witness_capacity()
        self.assertEqual(len(ext._ledger),GROWN_MAX_EPISODES)
        self.assertEqual(ext._episode_limit,EXTENDED_MAX_EPISODES)
        raw=ext.checkpoint()
        self.assertEqual(json.loads(raw)['schema'],EXTENDED_SCHEMA)
        self.assertLessEqual(len(raw),EXTENDED_MAX_CHECKPOINT_BYTES)
        self.assertEqual(ext.consolidate().checkpoint(),raw)
        restored=NativeEpisodeExperience.restore(raw,digest(raw))
        self.assertEqual(restored.checkpoint(),raw)
        self.assertEqual(restored._ledger,ext._ledger)
        tampered=json.loads(raw)
        tampered['episode_limit']=GROWN_MAX_EPISODES
        altered=canonical(tampered)
        with self.assertRaisesRegex(ValueError,'CKAD_NATIVE_EPISODE_CHECKPOINT_REJECTED'):
            NativeEpisodeExperience.restore(altered,digest(altered))
        tampered=json.loads(raw)
        tampered['episodes'][0][0]='f'*64
        altered=canonical(tampered)
        with self.assertRaisesRegex(ValueError,'CKAD_NATIVE_EPISODE_CHECKPOINT_REJECTED'):
            NativeEpisodeExperience.restore(altered,digest(altered))

    def test_detached_novel_v8_cold_replay_and_v1_immutable(self):
        native = NativeEpisodeExperience()
        old = native.checkpoint()
        expanded = native._extend_novel_capacity()
        self.assertEqual(native.checkpoint(), old)
        self.assertEqual(json.loads(expanded.checkpoint())['schema'],
                         'yggdrasil.ckad.native-episode-experience.v8')
        raw = expanded.checkpoint()
        self.assertEqual(NativeEpisodeExperience.restore(raw, digest(raw)).checkpoint(), raw)
        self.assertEqual(expanded.consolidate().checkpoint(), raw)
        with self.assertRaisesRegex(ValueError, 'EPISODE_NOVEL_GROWTH_PARENT'):
            expanded._extend_novel_capacity()

    @unittest.skipUnless(os.getenv('YGG_G41_FULL_2048') == '1',
                         'full 2048-row DEV stress requires separate bounded budget')
    def test_full_2048_roundtrip_and_2049_hard_reject(self):
        obj=saturated_legacy().extend_witness_capacity()
        for i in range(MAX_EPISODES,GROWN_MAX_EPISODES):
            obj._accept(dev_event(i))
        obj=obj.extend_witness_capacity()
        for i in range(GROWN_MAX_EPISODES,EXTENDED_MAX_EPISODES):
            obj._accept(dev_event(i))
        self.assertEqual(len(obj._ledger),EXTENDED_MAX_EPISODES)
        raw=obj.checkpoint()
        self.assertLessEqual(len(raw),EXTENDED_MAX_CHECKPOINT_BYTES)
        self.assertEqual(obj.consolidate().checkpoint(),raw)
        self.assertEqual(NativeEpisodeExperience.restore(raw,digest(raw)).checkpoint(),raw)
        with self.assertRaisesRegex(ValueError,'EPISODE_CAPACITY'):
            obj.observe(dev_event(EXTENDED_MAX_EPISODES)[0],((0,0),(0,0)),
                        {'s1':0,'x1':0,'s2':0,'x2':0,'y':0})


if __name__ == '__main__':
    unittest.main()

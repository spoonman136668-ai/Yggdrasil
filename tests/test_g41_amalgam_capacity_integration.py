"""Source-free G41 native capacity contract; not protected-world learning."""
from hashlib import sha256
import json
import unittest
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam, SCHEMA, EXTENDED_SCHEMA
from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist, STEPS as DS, MAX_EPISODES as DM
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist, STEPS as TS, MAX_EPISODES as TM

def event(i):
    return (sha256(("g41-dev-%06d" % i).encode()).hexdigest(), ((0, 0), (0, 0)), 0, 0, 0, 0)

class StubNative:
    def __init__(self, cap=1152):
        self._reader = type("Reader", (), {"_ledger": tuple(range(1152)), "_episode_limit": cap})()
    def _episode_reader(self):
        return self._reader
    def extend_experience_capacity(self):
        if self._reader._episode_limit != 1152:
            raise ValueError("STUB_BAD_PARENT")
        return StubNative(2048)
    def checkpoint(self):
        return canonical({"episode_limit": self._reader._episode_limit})

class G41CapacityIntegrationTests(unittest.TestCase):
    def test_unchanged_v1_head_limits_and_explicit_v2_extension(self):
        for cls, cap in ((ActionLatentSpecialist, DM*DS), (TemporalLatentSpecialist, TM*TS)):
            original = cls("transition")
            original.steps = cap
            old_data = original.as_data() if hasattr(original, "as_data") else original.data()
            extended = original.enable_extended_training()
            self.assertEqual(original.steps, cap)
            extended.steps += 3
            extended.clone()._validate()
            self.assertEqual(original.as_data() if hasattr(original, "as_data") else original.data(), old_data)
            with self.assertRaisesRegex(ValueError, "JEPA"):
                cls.from_data(extended.as_data() if hasattr(extended, "as_data")
                              else extended.data(), "transition")

    def test_amalgam_root_migration_explicit_no_v1_mutation(self):
        heads = (ActionLatentSpecialist("transition"), ActionLatentSpecialist("reward"),
                 TemporalLatentSpecialist("transition"), TemporalLatentSpecialist("reward"))
        root = NativeCausalAmalgam(StubNative(), heads, "a"*64, "b"*64)
        old = root.checkpoint()
        self.assertEqual(json.loads(old)["schema"], SCHEMA)
        extended = root.extend_capacity()
        self.assertEqual(root.checkpoint(), old)
        self.assertEqual(json.loads(extended.checkpoint())["schema"], EXTENDED_SCHEMA)
        self.assertEqual(extended.native._episode_reader()._episode_limit, 2048)
        with self.assertRaisesRegex(ValueError, "AMALGAM_GROWTH_PARENT"):
            extended.extend_capacity()

    def test_original_context_891_nested_migrates_without_weight_reset(self):
        parent = NativeEpisodeExperience()
        for i in range(891):
            parent._append(event(i))
        parent = parent.begin_stream().enable_context_refresh()
        for i in range(891,1024):
            parent._accept(event(i))
        parent = parent.extend_witness_capacity()
        for i in range(1024,1152):
            parent._accept(event(i))
        self.assertEqual(parent._context_start, 891)
        old = parent.checkpoint()
        weights = parent._context_weights
        novel = parent._context_models[-1][3]
        self.assertEqual(novel._episode_limit, 1024)
        extended = parent.extend_witness_capacity()
        self.assertEqual(parent.checkpoint(), old)
        self.assertEqual(extended._context_weights, weights)
        self.assertEqual(extended._context_models[-1][3]._ledger, novel._ledger)
        self.assertEqual(extended._context_models[-1][3]._episode_limit, 2048)
        raw = extended.checkpoint()
        self.assertEqual(NativeEpisodeExperience.restore(raw, digest(raw)).checkpoint(), raw)

if __name__ == "__main__":
    unittest.main()

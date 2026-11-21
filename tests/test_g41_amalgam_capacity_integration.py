"""Source-free G41 native capacity contract; not protected-world learning."""
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam, SCHEMA, EXTENDED_SCHEMA
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE
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

    def test_v8_detached_1153_row_cold_restore_boundary(self):
        """Source-free v8 must NOT invoke stream/refresh growth at outer 1152."""
        original = NativeEpisodeExperience()
        for i in range(1024):
            original._append(event(i))
        old_checkpoint = original.checkpoint()
        with self.assertRaisesRegex(ValueError, "EPISODE_CAPACITY"):
            identifier, views, first, next_state, second, reward = event(1024)
            original.observe(identifier, views, {"s1": 0, "x1": first,
                                               "s2": next_state, "x2": second,
                                               "y": reward})
        bank = original._extend_novel_capacity()
        for i in range(1024, 1153):
            identifier, views, first, next_state, second, reward = event(i)
            bank = bank.observe(identifier, views, {"s1": 0, "x1": first,
                                                  "s2": next_state, "x2": second,
                                                  "y": reward})
        self.assertEqual(original.checkpoint(), old_checkpoint)
        self.assertEqual(len(bank._ledger), 1153)
        raw = bank.checkpoint()
        self.assertEqual(json.loads(raw)["schema"],
                         "yggdrasil.ckad.native-episode-experience.v8")
        self.assertEqual(NativeEpisodeExperience.restore(raw, digest(raw)).checkpoint(), raw)
        self.assertEqual(bank.consolidate().checkpoint(), raw)
        with self.assertRaisesRegex(ValueError, "EPISODE_NOVEL_GROWTH_PARENT"):
            bank._extend_novel_capacity()

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

    @unittest.skipUnless(__import__("os").environ.get("YGG_G41_FULL_2048") == "1",
                         "2048 native/no-reset stress requires separate bounded budget")
    def test_opt_in_context891_crosses_original_nested_limit_and_2049_rejects(self):
        """DEV-only 891-start full evidence continuation; no source actor."""
        original = NativeEpisodeExperience()
        for i in range(891):
            original._append(event(i))
        original = original.begin_stream().enable_context_refresh()
        for i in range(891, 1024):
            original._accept(event(i))
        original = original.extend_witness_capacity()
        for i in range(1024, 1152):
            original._accept(event(i))
        original = original.extend_witness_capacity()
        for i in range(1152, 2048):
            identifier, views, first, next_state, second, reward = event(i)
            original = original.observe(identifier, views, {"s1": 0, "x1": first,
                                                            "s2": next_state, "x2": second,
                                                            "y": reward})
            self.assertEqual(original._context_start, 891,
                             "synthetic no-reset control drifted")
            if i == 1915:
                self.assertEqual(len(original._context_models[-1][3]._ledger), 1025)
        self.assertEqual(len(original._ledger), 2048)
        raw = original.checkpoint()
        self.assertEqual(NativeEpisodeExperience.restore(raw, digest(raw)).checkpoint(), raw)
        self.assertEqual(original.consolidate().checkpoint(), raw)
        identifier, views, first, next_state, second, reward = event(2048)
        with self.assertRaisesRegex(ValueError, "EPISODE_CAPACITY"):
            original.observe(identifier, views, {"s1": 0, "x1": first,
                                                "s2": next_state, "x2": second,
                                                "y": reward})
        self.assertEqual(original.checkpoint(), raw)

    @unittest.skipUnless(__import__("os").environ.get("YGG_G41_EARLY_1033") == "1",
                         "bounded source-free 8-start public 1033/1152 native stress is opt-in")
    def test_early_stream_public_1033_and_later_upgrade_roundtrip(self):
        """The legal eight-witness stream must not exhaust its inner bank at 1033."""
        def admit(state, i):
            identifier, views, first, next_state, second, reward = event(i)
            return state.observe(identifier, views, {
                "s1": 0, "x1": first, "s2": next_state, "x2": second, "y": reward,
            })

        state = NativeEpisodeExperience()
        for i in range(8):
            state = admit(state, i)
        state = state.begin_stream().enable_context_refresh()
        for i in range(8, 1032):
            if len(state._ledger) == 1024:
                state = state.extend_witness_capacity()
            state = admit(state, i)
            self.assertEqual(state._context_start, 8,
                             "no forced context reset is allowed")
        old_raw = state.checkpoint()
        old_novel = state._context_models[-1][3]
        self.assertEqual(len(state._ledger), 1032)
        self.assertEqual(len(old_novel._ledger), 1024)
        self.assertEqual(old_novel._episode_limit, 1024)

        state = admit(state, 1032)
        self.assertEqual(len(state._ledger), 1033)
        novel = state._context_models[-1][3]
        self.assertEqual(novel._episode_limit, 2048)
        self.assertEqual(novel._ledger[:1024], old_novel._ledger)
        self.assertEqual(state._context_start, 8)
        raw = state.checkpoint()
        self.assertEqual(NativeEpisodeExperience.restore(raw, digest(raw)).checkpoint(), raw)
        self.assertEqual(NativeEpisodeExperience.restore(old_raw, digest(old_raw)).checkpoint(), old_raw)

        for i in range(1033, 1152):
            state = admit(state, i)
            self.assertEqual(state._context_start, 8)
        old_at_1152 = state.checkpoint()
        grown = state.extend_witness_capacity()
        self.assertEqual(state.checkpoint(), old_at_1152)
        self.assertEqual(grown._context_models[-1][3]._episode_limit, 2048)
        raw = grown.checkpoint()
        self.assertEqual(NativeEpisodeExperience.restore(raw, digest(raw)).checkpoint(), raw)
        self.assertEqual(grown.consolidate().checkpoint(), raw)

    @unittest.skipUnless(os.environ.get("YGG_G41_TRAINED_1153") == "1",
                         "original archived four-head state requires pinned engineering artifacts")
    def test_original_trained_root_four_heads_1153(self):
        """Archive-authenticated native 1025 + four trained heads through the v2 boundary."""
        archive = Path(os.environ["YGG_G41_ORIGINAL_DIR"])
        joint = (archive / "g41-original" / "amalgam-joint-state.json").read_bytes()
        native_parent = (archive / "g41-original-native-parent"
                         / "seed-101-refresh-native.json").read_bytes()
        donor_package = json.loads((archive / "g41-original-donor-parent"
                                    / "seed-14071-state.json").read_bytes())
        donor_parent = donor_package["state_ascii"].encode("ascii")
        native_pin = "a00119c73a6431172c19b39ec67a1d94b470897a32c55c1c946071793f37dcc4"
        donor_pin = "ae83529696b566a12765f16749c258d9ed6addf111da41ef76dc1027938910da"
        joint_pin = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
        self.assertEqual(digest(native_parent), native_pin)
        self.assertEqual(digest(donor_parent), donor_pin)
        self.assertEqual(digest(joint), joint_pin)
        self.assertEqual(donor_package["state_sha256"], donor_pin)
        parents = dict(native_parent=native_parent, native_pin=native_pin,
                       donor_parent=donor_parent, donor_pin=donor_pin)
        original = NativeCausalAmalgam.restore(joint, joint_pin, **parents)
        self.assertEqual(original.checkpoint(), joint)
        self.assertEqual(len(original.native._episode_reader()._ledger), 1025)
        old_native = original.native.checkpoint()
        old_heads = tuple(head.as_data() if index < 2 else head.data()
                          for index, head in enumerate(original._heads))
        self.assertEqual(tuple(head.steps for head in original._heads), (2109,) * 4)

        views = ((0, 0), (0, 0))
        row = {"s1": 0, "x1": 0, "s2": 0, "x2": 0, "y": 0}
        learner = original
        for i in range(1025, 1152):
            identifier = sha256(("g41-original-source-free-%06d" % i).encode()).hexdigest()
            former_steps = tuple(head.steps for head in learner._heads)
            learner = learner.observe_experience(
                identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
                packet_sha256=digest(canonical([identifier, views, row])))
            self.assertEqual(tuple(head.steps for head in learner._heads),
                             tuple(value + 3 for value in former_steps))
        self.assertEqual(len(learner.native._episode_reader()._ledger), 1152)
        self.assertEqual(tuple(head.steps for head in learner._heads), (2490,) * 4)
        before_upgrade = learner.checkpoint()
        upgraded = learner.extend_capacity()
        self.assertEqual(learner.checkpoint(), before_upgrade)
        self.assertEqual(tuple(head.steps for head in upgraded._heads), (2490,) * 4)
        self.assertEqual(len(upgraded.native._episode_reader()._ledger), 1152)
        self.assertEqual(upgraded.native._episode_reader()._episode_limit, 2048)

        identifier = sha256(b"g41-original-source-free-001152").hexdigest()
        next_state = upgraded.observe_experience(
            identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
            packet_sha256=digest(canonical([identifier, views, row])))
        self.assertEqual(len(next_state.native._episode_reader()._ledger), 1153)
        self.assertEqual(tuple(head.steps for head in next_state._heads), (2493,) * 4)
        grown_checkpoint = next_state.checkpoint()
        recovered = NativeCausalAmalgam.restore(
            grown_checkpoint, digest(grown_checkpoint), **parents)
        self.assertEqual(recovered.checkpoint(), grown_checkpoint)
        self.assertEqual(tuple(head.steps for head in recovered._heads), (2493,) * 4)
        self.assertEqual(recovered.plan(views[0]), next_state.plan(views[0]))
        self.assertEqual(original.native.checkpoint(), old_native)
        self.assertEqual(tuple(head.as_data() if index < 2 else head.data()
                               for index, head in enumerate(original._heads)), old_heads)
        self.assertEqual(original.checkpoint(), joint)

    @unittest.skipUnless(os.environ.get("YGG_G41_TRAINED_2048") == "1",
                         "full original-trained 2048 growth requires exact archive and bounded CI")
    def test_original_trained_root_four_heads_2048_cold_replay_and_2049_veto(self):
        """Continue authentic 1025 trained native + all four heads through the hard 2048 cap."""
        archive = Path(os.environ["YGG_G41_ORIGINAL_DIR"])
        joint = (archive / "g41-original" / "amalgam-joint-state.json").read_bytes()
        native_parent = (archive / "g41-original-native-parent"
                         / "seed-101-refresh-native.json").read_bytes()
        donor_package = json.loads((archive / "g41-original-donor-parent"
                                    / "seed-14071-state.json").read_bytes())
        donor_parent = donor_package["state_ascii"].encode("ascii")
        native_pin = "a00119c73a6431172c19b39ec67a1d94b470897a32c55c1c946071793f37dcc4"
        donor_pin = "ae83529696b566a12765f16749c258d9ed6addf111da41ef76dc1027938910da"
        joint_pin = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
        self.assertEqual(digest(native_parent), native_pin)
        self.assertEqual(digest(donor_parent), donor_pin)
        self.assertEqual(donor_package["state_sha256"], donor_pin)
        self.assertEqual(digest(joint), joint_pin)
        parents = dict(native_parent=native_parent, native_pin=native_pin,
                       donor_parent=donor_parent, donor_pin=donor_pin)
        original = NativeCausalAmalgam.restore(joint, joint_pin, **parents)
        self.assertEqual(original.checkpoint(), joint)
        source_ledger = original.native._episode_reader()._ledger
        self.assertEqual(len(source_ledger), 1025)
        self.assertEqual(tuple(h.steps for h in original._heads), (2109,) * 4)

        views = ((0, 0), (0, 0))
        row = {"s1": 0, "x1": 0, "s2": 0, "x2": 0, "y": 0}
        def accept(system, i):
            identifier = sha256(("g41-original-source-free-%06d" % i).encode()).hexdigest()
            return system.observe_experience(
                identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
                packet_sha256=digest(canonical([identifier, views, row])))

        learner = original
        for i in range(1025, 1152):
            learner = accept(learner, i)
        self.assertEqual(tuple(h.steps for h in learner._heads), (2490,) * 4)
        pre_growth = learner.checkpoint()
        learner = learner.extend_capacity()
        self.assertEqual(learner.native._episode_reader()._episode_limit, 2048)
        self.assertEqual(tuple(h.steps for h in learner._heads), (2490,) * 4)
        self.assertEqual(len(learner.native._episode_reader()._ledger), 1152)
        self.assertEqual(digest(pre_growth), digest(
            NativeCausalAmalgam.restore(pre_growth, digest(pre_growth),
                                         **parents).checkpoint()))

        for i in range(1152, 2048):
            prior_steps = tuple(h.steps for h in learner._heads)
            learner = accept(learner, i)
            self.assertEqual(tuple(h.steps for h in learner._heads),
                             tuple(n + 3 for n in prior_steps))
        self.assertEqual(tuple(h.steps for h in learner._heads), (5178,) * 4)
        self.assertEqual(len(learner.native._episode_reader()._ledger), 2048)
        self.assertEqual(learner.native._episode_reader()._episode_limit, 2048)
        self.assertEqual(learner.native._episode_reader()._ledger[:1025], source_ledger)
        snapshot = learner.checkpoint()
        expected = digest(snapshot)
        self.assertEqual(learner.native.consolidate_experience().checkpoint(), learner.native.checkpoint())
        with self.assertRaisesRegex(ValueError, "EPISODE_CAPACITY"):
            accept(learner, 2048)
        self.assertEqual(learner.checkpoint(), snapshot)
        cold = NativeCausalAmalgam.restore(snapshot, expected, **parents)
        self.assertEqual(cold.checkpoint(), snapshot)
        self.assertEqual(tuple(h.steps for h in cold._heads), (5178,) * 4)
        self.assertEqual(cold.plan(views[0]), learner.plan(views[0]))
        self.assertEqual(cold.specialist_forecasts(views, 0),
                         learner.specialist_forecasts(views, 0))
        self.assertEqual(cold.specialist_forecasts(views, 0, 0, 0),
                         learner.specialist_forecasts(views, 0, 0, 0))
        self.assertEqual(original.checkpoint(), joint)

if __name__ == "__main__":
    unittest.main()

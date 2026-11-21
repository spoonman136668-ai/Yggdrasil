"""Source-free G41 native capacity contract; not protected-world learning."""
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
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
        if os.environ.get("YGG_G41_RETENTION_2048") == "1":
            # Frozen before result in PR #1329 issuecomment-7065308241:
            # existing retrospective audit, original 1025 old rows, unchanged +.02 bound.
            research = (Path(__file__).resolve().parents[1]
                        / "research/contrib/chatgpt/CAUSAL-AMALGAM")
            frozen = json.loads((research / "retention_probe.json").read_bytes())
            windows = {"earliest": [0, 32], "midpoint": [496, 528],
                       "latest_pre_fixture": [992, 1024]}
            self.assertEqual(frozen["anchor_sha256"], joint_pin)
            self.assertEqual(frozen["windows"], windows)
            self.assertEqual(frozen["max_brier_drift"], "1/50")
            def import_readonly(name):
                path = research / (name + ".py")
                specification = spec_from_file_location("g41_r9_" + name, path)
                self.assertIsNotNone(specification)
                module = module_from_spec(specification)
                specification.loader.exec_module(module)
                return module
            head_module = import_readonly("four_head_retention")
            native_module = import_readonly("retention_guard")
            head_report = head_module.audit_old_heads(original, learner, cold)
            native_report = native_module.evaluate(
                original, learner, {name: tuple(indices)
                                    for name, indices in windows.items()},
                max_brier_drift=Fraction(1, 50))
            self.assertEqual(head_report["old_witness_count"], 1025)
            self.assertEqual(head_report["continuation_witness_count"], 1023)
            self.assertEqual(head_report["anchor_checkpoint_sha256"], joint_pin)
            self.assertEqual(head_report["descendant_checkpoint_sha256"], expected)
            self.assertEqual(head_report["restored_checkpoint_sha256"], expected)
            self.assertEqual(tuple(head_report["heads"]), head_module.HEAD_NAMES)
            self.assertEqual(native_report["anchor_count"], 1025)
            self.assertEqual(native_report["candidate_count"], 2048)
            self.assertEqual(tuple(native_report["windows"]), tuple(windows))
            self.assertFalse(head_report["scientific_pass"])
            self.assertEqual(original.checkpoint(), joint)
            self.assertEqual(learner.checkpoint(), snapshot)
            self.assertEqual(cold.checkpoint(), snapshot)
            print("G41_R9_ORIGINAL_TRAINED_RETENTION_DIAGNOSTIC="
                  + json.dumps({"schema": "yggdrasil.g41.retrospective-2048.v1",
                                "old_joint_sha256": joint_pin,
                                "continued_joint_sha256": expected,
                                "old_public_witnesses": 1025,
                                "synthetic_continuation_witnesses": 1023,
                                "four_heads": head_report,
                                "native_windows": native_report,
                                "historical_only": True,
                                "held_evaluation": False,
                                "scientific_pass": False,
                                "owner_accepted": False}, sort_keys=True))
            if os.environ.get("YGG_G41_ATTRIBUTION_2048") == "1":
                # Frozen R10: PR #1329 issuecomment-7066576697, no training or mutation.
                earlier = original.native._episode_reader()
                later = learner.native._episode_reader()
                self.assertIsNotNone(earlier._context_start)
                self.assertEqual(earlier._context_start, later._context_start)
                old_weights = tuple(earlier._context_weights)
                new_weights = tuple(later._context_weights)
                old_models = tuple(earlier._context_models)
                new_models = tuple(later._context_models)
                self.assertTrue(old_weights)
                self.assertEqual(len(old_weights), len(new_weights))
                self.assertEqual(len(old_weights), len(old_models))
                self.assertEqual(len(old_weights), len(new_models))
                self.assertEqual(sum(old_weights), Fraction(1))
                self.assertEqual(sum(new_weights), Fraction(1))
                for index, (old, new) in enumerate(zip(old_models, new_models, strict=True)):
                    self.assertEqual(old[0], new[0])
                    if index != len(old_models) - 1:
                        self.assertEqual(old[1:3], new[1:3])

                def readonly_mix(weights, blocks, view, first, state=None, second=None):
                    self.assertEqual(len(weights), len(blocks))
                    self.assertEqual(sum(weights), Fraction(1))
                    predictions = tuple(block[-1].forecast(view, first, state, second)
                                        for block in blocks)
                    if state is not None:
                        transitions = tuple(block[-1].forecast(view, first)
                                            for block in blocks)
                        supports = tuple(weight * (prob if state else 1-prob)
                                         for weight, prob in zip(weights, transitions, strict=True))
                        total = sum(supports)
                        self.assertGreater(total, 0)
                        weights = tuple(weight / total for weight in supports)
                    return sum((weight * prob for weight, prob
                                in zip(weights, predictions, strict=True)), Fraction(0))

                old_row = source_ledger[0]
                with self.assertRaises(AssertionError):
                    readonly_mix(tuple(2 * w for w in old_weights), old_models,
                                 old_row[1][0], old_row[2])
                with self.assertRaises(AssertionError):
                    readonly_mix(old_weights + (Fraction(0),), old_models,
                                 old_row[1][0], old_row[2])

                scale = 1_000_000
                diagnostics = {}
                for window_name, (start, stop) in windows.items():
                    per_target = {}
                    for kind in ("transition", "reward"):
                        squared = [0, 0, 0, 0]
                        for _, row_views, first, state, second, reward in source_ledger[start:stop]:
                            view = row_views[0]
                            label = state if kind == "transition" else reward
                            tail = (None, None) if kind == "transition" else (state, second)
                            arms = (
                                readonly_mix(old_weights, old_models, view, first, *tail),
                                readonly_mix(new_weights, old_models, view, first, *tail),
                                readonly_mix(old_weights, new_models, view, first, *tail),
                                readonly_mix(new_weights, new_models, view, first, *tail),
                            )
                            self.assertEqual(arms[0], earlier.context_forecast(view, first, *tail))
                            self.assertEqual(arms[3], later.context_forecast(view, first, *tail))
                            self.assertEqual(arms[0], readonly_mix(
                                tuple(old_weights), tuple(old_models), view, first, *tail))
                            for i, arm in enumerate(arms):
                                squared[i] += (round(scale * arm) - scale * label) ** 2
                        n = stop - start
                        losses = tuple(Fraction(value, n * scale**2) for value in squared)
                        A, B, C, D = losses
                        weights_effect = (B - A + D - C) / 2
                        experts_effect = (C - A + D - B) / 2
                        interaction = D - B - C + A
                        self.assertEqual(weights_effect + experts_effect, D - A)
                        prior = native_report["windows"][window_name]
                        position = 0 if kind == "transition" else 1
                        self.assertEqual(float(A), prior["anchor_brier"][position])
                        self.assertEqual(float(D), prior["candidate_brier"][position])
                        self.assertEqual(float(D - A), prior["delta_brier"][position])
                        per_target[kind] = {
                            "brier_old_weights_old_experts": float(A),
                            "brier_new_weights_old_experts": float(B),
                            "brier_old_weights_new_experts": float(C),
                            "brier_new_weights_new_experts": float(D),
                            "old_task_drift": float(D - A),
                            "weight_effect": float(weights_effect),
                            "expert_effect": float(experts_effect),
                            "interaction": float(interaction),
                            "predeclared_native_retention_within_0p02": float(D - A) <= .02,
                        }
                    diagnostics[window_name] = per_target
                changed_models = sum(a[-1].checkpoint() != b[-1].checkpoint()
                                     for a, b in zip(old_models, new_models, strict=True))
                tv = sum((abs(a - b) for a, b in zip(old_weights, new_weights,
                                                  strict=True)), Fraction(0)) / 2
                self.assertGreaterEqual(tv, 0)
                self.assertLessEqual(tv, 1)
                self.assertEqual(original.checkpoint(), joint)
                self.assertEqual(learner.checkpoint(), snapshot)
                self.assertEqual(cold.checkpoint(), snapshot)
                print("G41_R10_WEIGHT_VS_EXPERT_ATTRIBUTION="
                      + json.dumps({
                          "schema": "yggdrasil.g41.r10.retrospective-weight-expert-v1",
                          "anchor_checkpoint_sha256": joint_pin,
                          "descendant_checkpoint_sha256": expected,
                          "old_witness_count": 1025,
                          "synthetic_new_witness_count": 1023,
                          "expert_count": len(old_models),
                          "expert_checkpoint_change_count": changed_models,
                          "mixture_weight_total_variation": float(tv),
                          "old_newest_expert_weight": float(old_weights[-1]),
                          "new_newest_expert_weight": float(new_weights[-1]),
                          "windows": diagnostics,
                          "frozen_before_readout": True,
                          "counterfactual_is_read_only": True,
                          "historical_not_held": True,
                          "scientific_gain_verified": False,
                          "owner_accepted": False,
                      }, sort_keys=True))

if __name__ == "__main__":
    unittest.main()

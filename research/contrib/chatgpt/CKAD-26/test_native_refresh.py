"""Toy update proofs and read-only compatibility; no CKAD26 held worlds."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_episode_experience import (
    NativeEpisodeExperience, REFRESH_SCHEMA, SCHEMA, CONTEXT_SCHEMA,
    NOVEL_CONTEXT_SCHEMA, STREAM_SCHEMA,
)


def episode(index, opposite=False):
    context, first, second = index & 1, (index // 2) & 1, (index // 4) & 1
    state = first ^ context ^ int(opposite)
    reward = second ^ state ^ int(opposite)
    return (digest(canonical(["ckad26-refresh-unit", index])),
            ((context, 0), (context, 1)),
            {"s1": context, "x1": first, "s2": state, "x2": second, "y": reward})


def witness(model, index, opposite=False):
    return model.observe(*episode(index, opposite))


def initial():
    model = NativeEpisodeExperience()
    for index in range(64):
        model = witness(model, index, index >= 32)
    return model


def stream():
    model = initial().begin_stream()
    for index in range(64, 69):
        model = witness(model, index)
    return model


class NativeRefreshRegression(unittest.TestCase):
    def test_activation_is_immutable_and_preserves_current_predictions(self):
        old = stream()
        raw = old.checkpoint()
        active = old.enable_context_refresh()
        self.assertEqual(old.checkpoint(), raw)
        self.assertEqual(active._context_weights, old._context_weights)
        self.assertEqual(active._stream_score, old._stream_score)
        self.assertEqual(active._context_models, old._context_models)
        self.assertEqual(active.info()["refresh"], {"refresh_start": 69, "rate": [1, 32]})
        self.assertNotIn("refresh", old.info())
        self.assertNotEqual(active.info()["state_sha256"], old.info()["state_sha256"])
        for view in ((0, 0), (1, 1)):
            for first in (0, 1):
                self.assertEqual(active.context_forecast(view, first), old.context_forecast(view, first))
                for state in (0, 1):
                    for second in (0, 1):
                        self.assertEqual(active.context_forecast(view, first, state, second),
                                         old.context_forecast(view, first, state, second))
        packet = active.checkpoint()
        self.assertEqual(json.loads(packet)["schema"], REFRESH_SCHEMA)
        self.assertEqual(NativeEpisodeExperience.restore(packet, digest(packet)).checkpoint(), packet)
        self.assertEqual(active.consolidate().checkpoint(), packet)

    def test_exact_share_uses_pretraining_joint_likelihood_and_existing_prior(self):
        old = stream()
        active = old.enable_context_refresh()
        _, views, row = episode(69)
        first, state, second, reward = (row[name] for name in ("x1", "s2", "x2", "y"))
        products = []
        for weight, (_, _, _, model) in zip(old._context_weights, old._context_models):
            transition = model.forecast(views[0], first)
            terminal = model.forecast(views[0], first, state, second)
            products.append(weight * (transition if state else 1 - transition)
                            * (terminal if reward else 1 - terminal))
        normalizer = sum(products, Fraction(0))
        posterior = tuple(value / normalizer for value in products)
        prior = (Fraction(7, 16), Fraction(7, 16), Fraction(1, 8))
        expected = tuple(Fraction(31, 32) * value + Fraction(1, 32) * base
                         for value, base in zip(posterior, prior))
        learned = witness(active, 69)
        self.assertEqual(learned._context_weights, expected)
        self.assertEqual(sum(expected), 1)
        self.assertNotEqual(expected, posterior)
        self.assertEqual(witness(old, 69)._context_weights, posterior)
        self.assertEqual(len(learned._context_models[-1][3]._ledger),
                         len(old._context_models[-1][3]._ledger) + 1)
        self.assertEqual(learned._context_models[:-1], old._context_models[:-1])
        p = old.context_forecast(views[0], first)
        q = old.context_forecast(views[0], first, state, second)
        likelihood = (p if state else 1 - p) * (q if reward else 1 - q)
        self.assertEqual(learned._stream_score, max(Fraction(1), old._stream_score / (4 * likelihood)))

    def test_cold_process_actual_toy_update_and_replay_after_activation(self):
        active = stream().enable_context_refresh()
        for index in range(69, 77):
            active = witness(active, index)
        raw = active.checkpoint()
        identifier, views, row = episode(77)
        script = (
            "import json,sys; from yggdrasil.native_context_basis import digest; "
            "from yggdrasil.native_episode_experience import NativeEpisodeExperience; "
            "raw=sys.stdin.buffer.read(); model=NativeEpisodeExperience.restore(raw,digest(raw)); "
            "event=json.loads(sys.argv[1]); pair=tuple(tuple(v) for v in event[1]); "
            "sys.stdout.buffer.write(model.observe(event[0],pair,event[2]).checkpoint())"
        )
        cold = subprocess.check_output([sys.executable, "-B", "-c", script,
                                        json.dumps([identifier, views, row])], input=raw)
        warm = witness(active, 77)
        self.assertEqual(cold, warm.checkpoint())
        restored = NativeEpisodeExperience.restore(cold, digest(cold))
        for index in range(78, 91):
            warm = witness(warm, index)
            restored = witness(restored, index)
        self.assertEqual(warm.checkpoint(), restored.checkpoint())
        self.assertEqual(warm.consolidate().checkpoint(), warm.checkpoint())

    def test_refresh_survives_automatic_context_reopening(self):
        model = initial().begin_stream().enable_context_refresh()
        before = len(model._stream_detections)
        for index in range(64, 192):
            # A toy counterexample always reveals the least likely joint
            # consequence under the current public-history forecast.
            identifier = digest(canonical(["ckad26-refresh-alarm-unit", index]))
            transition = model.context_forecast((0, 0), 0)
            consequences = []
            for state in (0, 1):
                terminal = model.context_forecast((0, 0), 0, state, 0)
                for reward in (0, 1):
                    likelihood = (transition if state else 1 - transition) * (terminal if reward else 1 - terminal)
                    consequences.append((likelihood, state, reward))
            _, state, reward = min(consequences)
            model = model.observe(identifier, ((0, 0), (0, 1)),
                                  {"s1": 0, "x1": 0, "s2": state, "x2": 0, "y": reward})
        self.assertGreater(len(model._stream_detections), before)
        self.assertEqual(model.info()["refresh"], {"refresh_start": 64, "rate": [1, 32]})
        self.assertEqual(model.consolidate().checkpoint(), model.checkpoint())
        raw = model.checkpoint()
        self.assertEqual(NativeEpisodeExperience.restore(raw, digest(raw)).checkpoint(), raw)

    def test_activation_and_parser_reject_invalid_mode_contracts(self):
        for model in (NativeEpisodeExperience(), initial(), initial().begin_context(novel=True)):
            with self.assertRaises(ValueError):
                model.enable_context_refresh()
        active = stream().enable_context_refresh()
        with self.assertRaises(ValueError):
            active.enable_context_refresh()
        data = json.loads(active.checkpoint())
        for key, value in (("refresh_start", True), ("refresh_start", 63),
                           ("refresh_start", 70), ("refresh_start", 68),
                           ("refresh_rate", [1, 16]), ("refresh_rate", [True, 32]),
                           ("refresh_rate", [1, 32, 0]), ("novel", False),
                           ("schema", STREAM_SCHEMA), ("unexpected", 1)):
            changed = dict(data, **{key: value})
            raw = canonical(changed)
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                NativeEpisodeExperience.restore(raw, digest(raw))
        for key in ("refresh_start", "refresh_rate", "stream_start"):
            changed = data.copy()
            del changed[key]
            raw = canonical(changed)
            with self.subTest(missing=key), self.assertRaises(ValueError):
                NativeEpisodeExperience.restore(raw, digest(raw))

    def test_all_old_schema_shapes_remain_exact_without_opt_in(self):
        base = initial()
        models = (base, base.begin_context(), base.begin_context(novel=True), base.begin_stream())
        for schema, model in zip((SCHEMA, CONTEXT_SCHEMA, NOVEL_CONTEXT_SCHEMA, STREAM_SCHEMA), models):
            raw = model.checkpoint()
            self.assertEqual(json.loads(raw)["schema"], schema)
            self.assertNotIn("refresh", model.info())
            restored = NativeEpisodeExperience.restore(raw, digest(raw))
            self.assertEqual(restored.checkpoint(), raw)
            self.assertEqual(restored.consolidate().checkpoint(), raw)

    def test_qualified_832_and_1024_parent_bytes_are_unchanged(self):
        root = Path(__file__).resolve().parents[1]
        prereg = json.loads(Path(__file__).with_name("prereg.json").read_text())
        for seed in prereg["seeds"]:
            for stage, suffix, count, pins in (
                    (24, "coverage", 832, prereg["initial_pins"]),
                    (25, "capacity", 1024, prereg["receipt_state_pins"])):
                with self.subTest(stage=stage, seed=seed):
                    path = root / f"CKAD-{stage}" / f"seed-{seed}-{suffix}-native.json"
                    raw = path.read_bytes()
                    self.assertEqual(digest(raw), pins[str(seed)])
                    model = NativeCumulativeLearner.restore(raw, digest(raw))
                    self.assertEqual(model.checkpoint(), raw)
                    self.assertEqual(model.info()["episode_experience"]["count"], count)
                    self.assertNotIn("refresh", model.info()["episode_experience"])
                    # Activation alone never trains on these historical rows.
                    active = model.enable_experience_refresh()
                    self.assertEqual(active._experience._context_weights, model._experience._context_weights)
                    self.assertEqual(model.checkpoint(), raw)
                    packet = active.checkpoint()
                    restored = NativeCumulativeLearner.restore(packet, digest(packet))
                    self.assertEqual(restored.checkpoint(), packet)
                    self.assertEqual(active.consolidate_experience().checkpoint(), packet)
                    if count == 1024:
                        with self.assertRaisesRegex(ValueError, "EPISODE_CAPACITY"):
                            active._experience.observe(*episode(2000))
                        self.assertEqual(active.checkpoint(), packet)


if __name__ == "__main__":
    unittest.main()

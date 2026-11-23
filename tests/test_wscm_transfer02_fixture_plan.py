"""WSCM fixture-only planner gate; no protected seed or first-use.

Pure adapter tests and original NativeEpisodeExperience integration tests are
separate: a passing adapter alone is not native/CI/scientific qualification.
"""
import hashlib
import importlib.util
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/WSCM-TRANSFER-02/fixture_only_plan.py")
SPEC = importlib.util.spec_from_file_location("wscm_fixture_only_plan", SOURCE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
choose = MOD.fixture_only_plan


class ReadoutStub:
    def __init__(self, values):
        self.values = values
        self.calls = []

    def observed_external_fixture_value(self, view, action):
        self.calls.append((view, action))
        return self.values.get((view, action))


class FixturePlannerPureTests(unittest.TestCase):
    def test_opposite_outcomes_same_public_view(self):
        model = ReadoutStub({((0, 0), 100): 0, ((0, 0), 200): 1})
        self.assertEqual(choose(model, (0, 0), (200, 100), 0), 100)
        self.assertEqual(choose(model, (0, 0), (100, 200), 1), 200)

    def test_unknown_id_abstains_instead_of_optimistic_choice(self):
        model = ReadoutStub({((0, 0), 100): 0})
        self.assertIsNone(choose(model, (0, 0), (100, 90017), 0))
        self.assertIsNone(choose(model, (0, 0), (100,), 1))

    def test_invalid_types_and_duplicate_ids_refused_before_read(self):
        model = ReadoutStub({})
        for view in ((True, 0), (2, 0), [0, 0], (0,)):
            with self.subTest(view=view), self.assertRaisesRegex(ValueError, "WSCM_PLAN_VIEW"):
                choose(model, view, (1,), 0)
        for target in (True, 2, "1"):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "WSCM_PLAN_TARGET"):
                choose(model, (0, 0), (1,), target)
        for ids in ((), [1], (1, 1), (True,), (-1,), (2**31,), tuple(range(33))):
            with self.subTest(ids=ids), self.assertRaisesRegex(ValueError, "WSCM_PLAN_ACTIONS"):
                choose(model, (0, 0), ids, 0)
        self.assertEqual(model.calls, [])

    def test_bad_native_result_rejected(self):
        for invalid in (True, 0.5, "0"):
            model = ReadoutStub({((0, 0), 1): invalid})
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                    ValueError, "WSCM_PLAN_INVALID_READOUT"):
                choose(model, (0, 0), (1,), 0)

    def test_tie_break_is_independent_of_candidate_order(self):
        model = ReadoutStub({((1, 1), 5): 1, ((1, 1), 3): 1, ((1, 1), 9): 0})
        self.assertEqual(choose(model, (1, 1), (9, 5, 3), 1), 3)
        self.assertEqual(choose(model, (1, 1), (3, 9, 5), 1), 3)


class NativeEpisodeFixturePlannerTests(unittest.TestCase):
    """Original native class; fixture outcomes are authored test data, not new world evidence."""

    @staticmethod
    def add(native, action, values, begin, order=(0, 1, 2, 3)):
        from yggdrasil.native_external_action_identity import (
            RECEIPT_SCHEMA, SOURCE_MODE, STATES, _canonical)
        for index in order:
            document = {"schema": RECEIPT_SCHEMA, "source_mode": SOURCE_MODE,
                        "source_id": f"{begin+index:064x}",
                        "public_view": list(STATES[index]),
                        "external_action_id": action, "outcome": values[index]}
            raw = _canonical(document)
            native = native.observe_external_fixture(
                {"public_view": list(STATES[index]), "external_action_id": action},
                raw, hashlib.sha256(raw).hexdigest())
        return native

    def test_distinct_ids_same_binary_view_native_forecast_and_cold_choice(self):
        from yggdrasil.native_episode_experience import NativeEpisodeExperience
        from yggdrasil.native_context_basis import digest
        base = NativeEpisodeExperience()
        unchanged_binary = (base.forecast((0, 0), 0), base.propose((0, 0)))
        model = self.add(base, 1301, (0, 0, 1, 1), 100)
        model = self.add(model, 90017, (1, 1, 0, 0), 200, (3, 2, 1, 0))
        self.assertEqual(model.observed_external_fixture_value((0, 0), 1301), 0)
        self.assertEqual(model.observed_external_fixture_value((0, 0), 90017), 1)
        self.assertEqual(choose(model, (0, 0), (90017, 1301), 0), 1301)
        self.assertEqual(choose(model, (0, 0), (90017, 1301), 1), 90017)
        self.assertEqual((model.forecast((0, 0), 0), model.propose((0, 0))),
                         unchanged_binary)
        self.assertEqual(base.checkpoint(), NativeEpisodeExperience().checkpoint())
        raw = model.checkpoint()
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(choose(cold, (0, 0), (90017, 1301), 1), 90017)
        self.assertEqual(choose(cold, (0, 0), (90017, 1301), 0), 1301)

    def test_partially_witnessed_external_id_cannot_be_used(self):
        from yggdrasil.native_episode_experience import NativeEpisodeExperience
        model = self.add(NativeEpisodeExperience(), 1301, (0, 0, 1, 1), 100)
        model = self.add(model, 90017, (1, 1, 0, 0), 200, (0, 1, 2))
        self.assertIsNone(choose(model, (0, 0), (1301, 90017), 0))
        self.assertIsNone(model.observed_external_fixture_value((0, 0), 90017))

    def test_contradictory_witness_forces_abstention_even_after_full_table(self):
        from yggdrasil.native_episode_experience import NativeEpisodeExperience
        from yggdrasil.native_external_action_identity import (
            RECEIPT_SCHEMA, SOURCE_MODE, _canonical)
        model = self.add(NativeEpisodeExperience(), 1301, (0, 0, 1, 1), 100)
        raw = _canonical({"schema": RECEIPT_SCHEMA, "source_mode": SOURCE_MODE,
                          "source_id": f"{900:064x}", "public_view": [0, 0],
                          "external_action_id": 1301, "outcome": 1})
        model = model.observe_external_fixture(
            {"public_view": [0, 0], "external_action_id": 1301},
            raw, hashlib.sha256(raw).hexdigest())
        self.assertIsNone(choose(model, (0, 0), (1301,), 1))

    def test_unwitnessed_renamed_id_stays_unbound_after_cold_restore(self):
        from yggdrasil.native_episode_experience import NativeEpisodeExperience
        from yggdrasil.native_context_basis import digest
        model = self.add(NativeEpisodeExperience(), 1301, (0, 0, 1, 1), 100)
        cold_raw = model.checkpoint()
        cold = NativeEpisodeExperience.restore(cold_raw, digest(cold_raw))
        self.assertIsNone(choose(cold, (0, 0), (1301, 90017), 0))
        self.assertIsNone(cold.observed_external_fixture_value((0, 0), 90017))


if __name__ == "__main__":
    unittest.main()

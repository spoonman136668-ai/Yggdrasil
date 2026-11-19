"""CKAD39 development qualification. No pilot or primary seeds are run."""
import importlib.util
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from yggdrasil.native_context_basis import digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from readout import evidence_forecast
spec = importlib.util.spec_from_file_location("ckad39_dev_campaign", HERE / "campaign.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


class FrozenSource:
    def __init__(self, transition, terminal):
        self.p, self.q = Fraction(transition), Fraction(terminal)

    def forecast(self, view, first, next_state=None, second=None):
        return self.p if next_state is None else self.q


class FrozenFixture:
    def __init__(self):
        self._context_start = 48
        self._stream_start = 48
        self._stream_detections = (("witnessed-only", 15, Fraction(16)),)
        self._ledger = tuple((str(t), ((1, 0), (1, 1)), 1, 1, 1, 1)
                             for t in range(32))
        self._context_models = (
            (0, 32, "archived0", FrozenSource(Fraction(4, 5), Fraction(4, 5))),
            (32, 48, "archived1", FrozenSource(Fraction(1, 5), Fraction(1, 5))),
        )

    def context_forecast(self, view, first, next_state=None, second=None):
        return Fraction(1, 2)

    def forecast(self, view, first, next_state=None, second=None):
        return Fraction(1, 2)


class CKAD39Tests(unittest.TestCase):
    def test_seed_boundaries_and_preregistration(self):
        self.assertEqual(C.DEV, (38911, 38912))
        self.assertEqual(C.PILOT, (39181, 39182))
        self.assertEqual(C.PRIMARY, (49181, 49182, 49183))
        self.assertEqual(C.PREREG, "d210f6d0259bb4dc27fe6a5155eeef0ffdcb776a")
        self.assertNotIn("native_recall", C.ARMS)
        self.assertIn("native_evidence", C.ARMS)
        for seed in (*C.DEV, *C.PRIMARY, 14181, 14182, 14071, 14072):
            with self.assertRaisesRegex(ValueError, "CKAD39_ONLY_REGISTERED_PILOT"):
                C.score(seed)

    def test_archive_likelihood_is_witness_only_and_read_only(self):
        model = FrozenFixture()
        before = repr((model._ledger, model._context_models, model._stream_detections))
        p = evidence_forecast(model, (1, 0), 1)
        q = evidence_forecast(model, (1, 0), 1, 1, 1)
        self.assertGreater(p, 0.60)
        self.assertGreater(q, 0.60)
        self.assertLess(p, 0.65 + 1e-5)
        self.assertEqual(before, repr((model._ledger, model._context_models,
                                       model._stream_detections)))

    def test_no_detection_and_stale_detection_fall_back(self):
        model = FrozenFixture()
        model._stream_detections = ()
        self.assertEqual(evidence_forecast(model, (1, 0), 1), Fraction(1, 2))
        model._stream_detections = (("old", -100, Fraction(16)),)
        self.assertEqual(evidence_forecast(model, (1, 0), 1), Fraction(1, 2))
        model._context_models = (
            (0, 32, "a", FrozenSource(Fraction(1, 2), Fraction(1, 2))),
            (32, 48, "b", FrozenSource(Fraction(1, 2), Fraction(1, 2))),
        )
        model._stream_detections = (("now", 25, Fraction(16)),)
        self.assertEqual(evidence_forecast(model, (1, 0), 1), Fraction(1, 2))

    def test_original_native_training_and_cold_exact(self):
        model = NativeEpisodeExperience(repair=True)
        events, _ = C.generator(C.DEV[0], 0)
        for t, (identifier, views, row, _) in enumerate(events[:80]):
            if t == 48:
                model = model.begin_stream()
            if t >= 48:
                before = model.checkpoint()
                for action in (0, 1):
                    _ = evidence_forecast(model, views[0], action)
                    _ = evidence_forecast(model, views[0], action, 0, 1)
                self.assertEqual(model.checkpoint(), before)
            model = model.observe(identifier, views, row)
        saved = model.checkpoint()
        restored = NativeEpisodeExperience.restore(saved, digest(saved))
        self.assertEqual(saved, restored.checkpoint())
        self.assertEqual(evidence_forecast(model, (1, 0), 1),
                         evidence_forecast(restored, (1, 0), 1))

    def test_source_only_identical_actions_and_conventional_fitting(self):
        for seed in C.DEV:
            for world in C.WORLDS:
                events, private = C.generator(seed, world)
                self.assertEqual(len(events), len(set(x[0] for x in events)))
                self.assertEqual(events[48][3], "stable_A")
                self.assertEqual(events[private["boundary_A_to_B"]][3], "early_B")
        fitted = C.Conventional()
        row = {"s1": 1, "x1": 1, "s2": 1, "x2": 1, "y": 0}
        fitted.observe(row, {arm: .25 for arm in C.CONVENTIONAL})
        self.assertAlmostEqual(fitted.p("beta_full", "transition", 1, 1), 2/3)
        self.assertAlmostEqual(fitted.p("beta_full", "terminal", 1, 1, 1, 1), 1/3)

    def test_full_source_only_dev_pipeline_without_first_use(self):
        case = C._dev_or_pilot(C.DEV[0])
        self.assertEqual(case["world_count"], 2)
        self.assertEqual(case["total_authentic_episodes"] * 2,
                         case["total_authentic_consequences"])
        for world in case["worlds"]:
            for key in ("old_source_preserved", "retrieval_pure_read",
                        "duplicate_idempotent", "conflict_atomic",
                        "consolidated_exact", "cold_exact"):
                self.assertIs(world[key], True)
        pooled = case["metric_groups"]["pooled_late_shift_and_return"]
        self.assertEqual(set(pooled), set(C.ARMS))

    def test_pilot_go_is_not_scientific_pass(self):
        def fixture(seed, evidence=.10, baseline=.15, control=.18):
            phases = (*C.PHASES, "pooled_late_shift_and_return")
            metrics = {phase: {arm: {"brier": .2, "episodes": 24}
                               for arm in C.ARMS} for phase in phases}
            for phase in ("pooled_late_shift_and_return", "early_B",
                          "late_return_A"):
                metrics[phase]["native_evidence"]["brier"] = evidence
                metrics[phase]["native_stream"]["brier"] = baseline
            for arm in (*C.CONVENTIONAL, "beta_hedge"):
                metrics["pooled_late_shift_and_return"][arm]["brier"] = control
            return {"seed": seed, "metric_groups": metrics,
                    "worlds": [{"old_source_preserved": True,
                      "duplicate_idempotent": True, "conflict_atomic": True,
                      "consolidated_exact": True, "cold_exact": True,
                      "retrieval_pure_read": True}]}
        first, second = (fixture(seed) for seed in C.PILOT)
        self.assertEqual(C.classify([first, second])["decision"], "ENGINEERING_FEASIBLE")
        self.assertFalse(C.classify([first, second])["scientific_pass"])
        self.assertEqual(C.classify([first, fixture(C.PILOT[1], control=.11)])["decision"],
                         "SCREEN_NO_GO")


if __name__ == "__main__":
    unittest.main()

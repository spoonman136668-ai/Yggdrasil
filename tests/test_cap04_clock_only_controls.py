"""CAP04 prospective fixture-only clock/identity controls and source leakage.

Never generate registered DEV/pilot/primary seeds or call scientific scoring.
"""
import hashlib
import importlib.util
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import digest

ROOT = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/YGG-CAP04"


def load(name):
    spec = importlib.util.spec_from_file_location("cap04_" + name, ROOT / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


clock = load("clock_controls.py")
source = load("prospective_source.py")
ClockOnlyControls = clock.ClockOnlyControls
ARMS = clock.ARMS



def public_witness_id(identity, t):
    # Independent reconstruction of a witness ID from known fixture identity.
    raw = f"YGG-CAP04/public-witness-v1/{identity}/{t}/observed"
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


class ClockOnlyQualifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tapes = {ident: source.engineering_fixture(ident)
                     for ident in source.ENGINEERING_FIXTURES}

    def test_five_fully_fitted_prequential_clock_and_action_arms(self):
        self.assertEqual(len(ARMS), 5)
        self.assertEqual(source.SCHEMA, "yggdrasil.cap04.prospective-source.v1")
        for identity, tape in self.tapes.items():
            with self.subTest(identity=identity):
                proof = clock.fixture_prequential_scores(tape)
                self.assertEqual(proof["classification"], "ENGINEERING_FIXTURE_ONLY")
                self.assertEqual(proof["rows_verified"], 96)
                self.assertEqual(set(proof["means"]), set(ARMS))
                self.assertEqual(len(proof["checkpoint_sha256"]), 64)
                for metrics in proof["means"].values():
                    self.assertEqual(set(metrics), {"novel", "cold_return", "pooled"})
                    self.assertTrue(all(0 <= x <= 1 for x in metrics.values()))
                self.assertEqual(proof, clock.fixture_prequential_scores(tape))

    def test_forecast_has_no_previous_event_feature_and_clock_is_enforced(self):
        model = ClockOnlyControls()
        tape = next(iter(self.tapes.values()))
        first = tape[0]
        before = model.checkpoint()
        for stage, sensor in (("transition", None), ("residual", first["s2"])):
            probs = model.forecast(first["views"], first["action"], stage,
                                   sensor, step=0)
            self.assertEqual(set(probs), set(ARMS))
            self.assertTrue(all(p == .5 for p in probs.values()))
            self.assertEqual(model.checkpoint(), before)
        for bad in (True, -1, 1, "0", None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                model.forecast(first["views"], first["action"],
                               "transition", step=bad)
        with self.assertRaisesRegex(ValueError, "FUTURE_SENSOR"):
            model.forecast(first["views"], first["action"],
                           "transition", first["s2"], step=0)
        with self.assertRaisesRegex(ValueError, "BIT"):
            model.forecast(first["views"], first["action"], "residual", step=0)
        with self.assertRaises(TypeError):
            model.forecast(first["views"], first["action"], "transition",
                           step=0, previous_action=(0, 1))
        with self.assertRaisesRegex(ValueError, "CLOCK"):
            model.observe(first["id"], first["views"], first["action"],
                          first["s2"], first["y"], first["post"], step=1)
        self.assertEqual(model.checkpoint(), before)

    def test_cold_full_public_history_and_tampered_source_rejected(self):
        tape = next(iter(self.tapes.values()))
        model = ClockOnlyControls()
        for t, row in enumerate(tape):
            model.observe(row["id"], row["views"], row["action"],
                          row["s2"], row["y"], row["post"], step=t)
        raw = model.checkpoint()
        cold = ClockOnlyControls.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold.count, 96)
        with self.assertRaisesRegex(ValueError, "COLD_HASH"):
            ClockOnlyControls.restore(raw+b"!", digest(raw))
        for step in (-1, 95, "96"):
            with self.assertRaisesRegex(ValueError, "CLOCK"):
                cold.forecast(tape[-1]["views"], tape[-1]["action"],
                              "transition", step=step)
        with self.assertRaisesRegex(ValueError, "SOURCE_ID"):
            cold.observe(tape[0]["id"], tape[0]["views"], tape[0]["action"],
                         tape[0]["s2"], tape[0]["y"], tape[0]["post"], step=96)

    def test_clock_current_action_ambiguity_cross_fixture(self):
        left, right = tuple(self.tapes.values())
        collisions = [t for t in range(32, 72)
                      if left[t]["action"] == right[t]["action"] and
                      left[t - 1]["action"] != right[t - 1]["action"]]
        self.assertGreaterEqual(len(collisions), 1)
        # Current action/time cannot universally recover previous intervention.
        # Source-key knowledge CAN; tested separately as an oracle leakage risk.

    def test_source_identity_leak_is_an_oracle_not_a_fair_baseline(self):
        # User-visible witness IDs are a public SHA256 of a SMALL known set of
        # source identities. An adversarial code-aware evaluator can enumerate
        # both source keys from the first ID, and then exactly derive the
        # exogenous predecessor action without using witnessed prior actions.
        # This intentionally proves a leak on ENGINEERING FIXTURES only.
        labels = tuple(self.tapes)
        for identity, tape in self.tapes.items():
            guessed = [guess for guess in labels
                       if public_witness_id(guess, 0) == tape[0]["id"]]
            self.assertEqual(guessed, [identity])
            self.assertEqual(tape[0]["id"], public_witness_id(identity, 0))
            for t in range(1, 96):
                self.assertEqual(source.exogenous_action(identity, t-1),
                                 tape[t-1]["action"])
        # The source-key oracle uses nonpublic identity; it is deliberately
        # NOT inserted among the five matched-information clock controls.
        self.assertFalse(any("identity" in name or "oracle" in name for name in ARMS))

    def test_registered_first_use_and_non_fixture_shapes_fail_closed(self):
        for seed in source.REGISTERED:
            with self.subTest(seed=seed), self.assertRaisesRegex(
                    ValueError, "REGISTERED_FIRST_USE_FORBIDDEN"):
                source.generate_registered(seed)
        tape = next(iter(self.tapes.values()))
        with self.assertRaisesRegex(ValueError, "FIXTURE_ONLY_BUDGET"):
            clock.fixture_prequential_scores(tape[:95])
        with self.assertRaisesRegex(ValueError, "ROW_FIELDS"):
            clock.fixture_prequential_scores((dict(tape[0], private_phase="B"),)
                                             + tape[1:])
        with self.assertRaisesRegex(ValueError, "SOURCE_ID"):
            model = ClockOnlyControls()
            model.observe("badid", tape[0]["views"], tape[0]["action"],
                          tape[0]["s2"], tape[0]["y"], tape[0]["post"], step=0)


if __name__ == "__main__":
    unittest.main()

"""WSP80 developer-only paid-world numeric baseline validation, NOT science."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
import acquisition
import source
from controls import SparsePublicControl
from numerical_controls import FixedSparseNumeric, MAX_SNAPSHOT_BYTES
from structural_weights import ACTIONS, STATES


class NumericControlEngineering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Unregistered developer fixture only. No WSP80 science source used.
        world = source.World(9001, "quartic_positive",
                             tuple(range(6)), tuple(range(6)))
        session = world.training_session()
        policy = acquisition.InterventionPolicy()
        for i in range(384):
            action = (acquisition.stage_a_action(9001, i) if i < 144
                      else policy.choose(session.current))
            event = session.step(action)
            policy.observe(event)
        cls.ledger = tuple(session.ledger)

    def test_degree3_and_always_degree4_numeric_cold_parity(self):
        for mode in ("fixed_degree3", "always_degree4"):
            symbolic = SparsePublicControl(self.ledger, mode=mode)
            trained = FixedSparseNumeric(mode)
            stats = trained.fit(self.ledger)
            self.assertEqual(stats["charged_actions"], 384)
            self.assertEqual(stats["gradient_steps"], 0)
            self.assertEqual(stats["numerical_relu_features"],
                             252 if mode == "fixed_degree3" else 342)
            saved = trained.snapshot()
            self.assertLess(len(saved), MAX_SNAPSHOT_BYTES)
            restored = FixedSparseNumeric.restore(saved)
            self.assertEqual(restored.snapshot(), saved)
            self.assertIsNone(restored._training_summary)
            for state in STATES:
                for action in ACTIONS:
                    self.assertEqual(restored.predict(state, action),
                                     symbolic.predict(state, action))
                    self.assertEqual(restored.predict(state, action, force=True),
                                     symbolic.predict(state, action, force=True))

    def test_stage_a_replay_uses_only_first_144_charges(self):
        for mode in ("fixed_degree3", "always_degree4"):
            symbolic = SparsePublicControl(self.ledger, mode=mode, stage_a_only=True)
            model = FixedSparseNumeric(mode)
            diag = model.fit(self.ledger[:144])
            self.assertEqual(diag["charged_actions"], 144)
            restored = FixedSparseNumeric.restore(model.snapshot())
            self.assertEqual(restored.paid_actions, 144)
            for state in STATES:
                for action in ACTIONS:
                    self.assertEqual(restored.predict(state, action),
                                     symbolic.predict(state, action))

    def test_invalid_continuity_tamper_and_compiled_refit_rejected(self):
        model = FixedSparseNumeric("fixed_degree3")
        with self.assertRaises(ValueError):
            model.fit(self.ledger[:-1])
        model.fit(self.ledger)
        with self.assertRaises(ValueError):
            model.fit(self.ledger)
        saved = model.snapshot()
        with self.assertRaises(ValueError):
            FixedSparseNumeric.restore(saved.replace("fixed_degree3",
                                                    "always_degree4", 1))
        with self.assertRaises(ValueError):
            FixedSparseNumeric.restore(saved[:-7])
        with self.assertRaises(ValueError):
            FixedSparseNumeric("invalid")
        with self.assertRaises(ValueError):
            model.predict((0,) * 6, 0, force=1)

    def test_numerical_controls_never_import_private_source_or_training_solver_at_cold_inference(self):
        path = Path(__file__).with_name("numerical_controls.py")
        body = path.read_text("utf-8")
        for forbidden in ("from source import", "import source", "_step_oracle",
                          "import structural_weights", "from structural_weights"):
            self.assertNotIn(forbidden, body)
        # Solver is used during fit only; restored model stores numerical arrays.
        self.assertEqual(FixedSparseNumeric("fixed_degree3")._payload, None)


if __name__ == "__main__":
    unittest.main()

"""Source-free interface and negative controls; not original-world science."""
from fractions import Fraction as F
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import unittest

PATH = Path(__file__).with_name("factorized_context_readout.py")
spec = spec_from_file_location("fcr01_factorized_context", PATH)
module = module_from_spec(spec)
spec.loader.exec_module(module)


class Expert:
    def __init__(self, transition, reward):
        self.t, self.r = F(transition), F(reward)

    def forecast(self, view, first, state=None, second=None):
        return self.t if state is None else self.r


class FakeNative:
    def __init__(self, experts, ledger=(), *, weights=None, refresh=None):
        self._ledger = tuple(ledger)
        self._context_start = 64
        self._context_novel = False
        self._refresh_start = refresh
        self._context_models = tuple((i * 32, (i + 1) * 32, str(i) * 64, model)
                                     for i, model in enumerate(experts))
        self._context_weights = (tuple(weights) if weights is not None
                                 else (F(1, len(experts)),) * len(experts))

    def _context_prior(self):
        return (F(1, len(self._context_models)),) * len(self._context_models)

    def _context_predictions(self, view, first, state, second):
        return tuple(expert.forecast(view, first, state, second)
                     for _, _, _, expert in self._context_models)

    def checkpoint(self):
        return module.canonical({"rows": self._ledger,
            "weights": [[x.numerator, x.denominator] for x in self._context_weights],
            "experts": [[x[3].t.numerator, x[3].t.denominator,
                         x[3].r.numerator, x[3].r.denominator]
                        for x in self._context_models]})


def witness(i, state=1, reward=0):
    return (format(i, "064x"), ((0, 0), (0, 1)), 0, state, 1, reward)


def sample(*, t=(F(9, 10), F(1, 10)), r=(F(1, 10), F(9, 10))):
    return FakeNative([Expert(a, b) for a, b in zip(t, r)])


class FactorizedReadoutTests(unittest.TestCase):
    def test_independently_recall_terminal_without_wrong_transition(self):
        native = sample()
        root = module.FactorizedContextReadout(native)
        later = FakeNative([e[3] for e in native._context_models], (witness(1, 1, 1),))
        updated = root.advance(later)
        self.assertEqual(updated._transition, (F(9, 10), F(1, 10)))
        self.assertEqual(updated._reward, (F(1, 10), F(9, 10)))
        self.assertEqual(updated.transition((0, 0), 0), F(41, 50))
        self.assertEqual(updated.reward((0, 0), 0, 1, 1), F(41, 50))
        self.assertEqual(root.transition((0, 0), 0), F(1, 2))
        self.assertEqual(root.reward((0, 0), 0, 1, 1), F(1, 2))

    def test_transition_only_evidence_does_not_override_terminal_weights(self):
        n = sample(t=(F(9, 10), F(1, 10)), r=(F(1, 2), F(1, 2)))
        a = module.FactorizedContextReadout(n)
        b = a.advance(FakeNative([x[3] for x in n._context_models], (witness(2, 1, 0),)))
        self.assertEqual(b._transition, (F(9, 10), F(1, 10)))
        self.assertEqual(b._reward, (F(1, 2), F(1, 2)))

    def test_recombined_stage_forecasts_use_different_old_experts(self):
        n = sample()
        a = module.FactorizedContextReadout(n)
        b = a.advance(FakeNative([x[3] for x in n._context_models], (witness(3, 1, 1),)))
        self.assertGreater(b.transition((0, 0), 0), F(4, 5))
        self.assertGreater(b.reward((0, 0), 0, 1, 1), F(4, 5))
        # Single full-context bank cannot select both disagreeing experts.
        self.assertEqual(n._context_models[0][3].r, F(1, 10))
        self.assertEqual(n._context_models[1][3].t, F(1, 10))

    def test_unseen_context_without_new_expert_does_not_claim_discovery(self):
        n = sample()
        a = module.FactorizedContextReadout(n)
        # Both existing expert predictions are misspecified on each stage;
        # the adapter cannot fabricate a new expert or a causal observation.
        b = a.advance(FakeNative([x[3] for x in n._context_models], (witness(4, 0, 0),)))
        self.assertEqual(len(b._transition), 2)
        self.assertEqual(len(b._reward), 2)
        self.assertEqual(n.checkpoint(), module.FactorizedContextReadout(n)._native.checkpoint())

    def test_wrong_order_replay_and_invented_observation_rejected(self):
        n = sample()
        a = module.FactorizedContextReadout(n)
        for malformed in (n, FakeNative([e[3] for e in n._context_models], (witness(7), witness(8))),
                          FakeNative([e[3] for e in n._context_models], (witness(9, 1, True),))):
            with self.assertRaises(ValueError):
                a.advance(malformed)
        n2 = FakeNative([e[3] for e in n._context_models], (witness(3),), weights=(F(1), F(0)))
        advanced = a.advance(n2)
        with self.assertRaisesRegex(ValueError, "REPLAY"):
            advanced.advance(n2)

    def test_unsupported_expert_replacement_rejected(self):
        n = sample()
        a = module.FactorizedContextReadout(n)
        substitute = FakeNative([e[3] for e in n._context_models] + [Expert(F(1, 2), F(1, 2))],
                                (witness(5),))
        with self.assertRaisesRegex(ValueError, "EXPERT_SET_DRIFT"):
            a.advance(substitute)

    def test_exact_cold_policy_parity_and_wrong_parent_rejected(self):
        n = sample()
        r = module.FactorizedContextReadout(n)
        raw = r.checkpoint()
        cold = module.FactorizedContextReadout.restore(n, raw, module.digest(raw))
        self.assertEqual(raw, cold.checkpoint())
        self.assertEqual(r.transition((0, 0), 0), cold.transition((0, 0), 0))
        self.assertEqual(r.reward((0, 0), 0, 1, 0), cold.reward((0, 0), 0, 1, 0))
        altered_native = FakeNative([e[3] for e in n._context_models], (witness(10),))
        with self.assertRaises(ValueError):
            module.FactorizedContextReadout.restore(altered_native, raw, module.digest(raw))
        data = json.loads(raw)
        data["scientific_pass"] = True
        damaged = module.canonical(data)
        with self.assertRaises(ValueError):
            module.FactorizedContextReadout.restore(n, damaged, module.digest(damaged))
        data = json.loads(raw)
        data["reward_weights"][0][0] = 100
        damaged = module.canonical(data)
        with self.assertRaises(ValueError):
            module.FactorizedContextReadout.restore(n, damaged, module.digest(damaged))

    def test_correlated_joint_law_is_explicit_nonidentifiable_limit(self):
        # Marginal stage probabilities are insufficient to represent an
        # unobserved joint mechanism: no claimed success on that case.
        n = sample(t=(F(1, 2), F(1, 2)), r=(F(1, 2), F(1, 2)))
        r = module.FactorizedContextReadout(n)
        self.assertEqual(r.transition((0, 0), 0), F(1, 2))
        self.assertEqual(r.reward((0, 0), 0, 1, 1), F(1, 2))
        self.assertNotEqual(r.transition((0, 0), 0) * r.reward((0, 0), 0, 1, 1),
                            F(1, 2))  # possible actual correlated joint P(1,1)

    def test_no_live_calls_and_immutable_original(self):
        n = sample()
        old = n.checkpoint()
        a = module.FactorizedContextReadout(n)
        for i in range(2):
            a.transition((0, 0), i)
            a.reward((0, 0), i, 1, 0)
        self.assertEqual(n.checkpoint(), old)
        self.assertFalse(json.loads(a.checkpoint())["accepted_native"])
        self.assertFalse(json.loads(a.checkpoint())["scientific_pass"])
        for invalid in (True, -1, 2):
            with self.assertRaisesRegex(ValueError, "PUBLIC_BIT"):
                a.transition((0, 0), invalid)

    def test_native_expert_drift_detection(self):
        n = sample()
        a = module.FactorizedContextReadout(n)
        n._context_models = ()
        with self.assertRaisesRegex(ValueError, "NATIVE_SOURCE_DRIFT"):
            a.checkpoint()

    def test_refresh_policy_matches_existing_preregistered_rate(self):
        n = sample()
        n._refresh_start = 64
        a = module.FactorizedContextReadout(n)
        next_ = FakeNative([x[3] for x in n._context_models], (witness(11, 1, 1),), refresh=64)
        b = a.advance(next_)
        self.assertEqual(b._transition[0], F(31, 32) * F(9, 10) + F(1, 64))
        self.assertEqual(b._reward[1], F(31, 32) * F(9, 10) + F(1, 64))


if __name__ == "__main__":
    unittest.main()

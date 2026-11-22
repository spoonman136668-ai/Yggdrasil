"""Check witnessed action transformations without a simulator or learned checkpoint."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

PATH = (Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
        / "causal_templates.py")
SPEC = spec_from_file_location("amalgam_causal_templates_for_tests", PATH)
TEMPLATES = module_from_spec(SPEC)
SPEC.loader.exec_module(TEMPLATES)


def prior(view, action):
    return (0.15, 0.85)[action]


class CausalTemplateTests(unittest.TestCase):
    def test_pure_swap_can_be_inferred_from_witnesses(self):
        model = TEMPLATES.CausalTemplates(prior)
        for i in range(16):
            action = i % 2
            model.advance((0, 0), action, 1-action)
        self.assertGreater(model.marginal((0, 0), 0), 0.8)
        self.assertLess(model.marginal((0, 0), 1), 0.2)
        self.assertAlmostEqual(sum(model.mass), 1)

    def test_intervention_changes_only_hypotheses_that_predict_it(self):
        model = TEMPLATES.CausalTemplates(prior)
        model.advance((0, 0), 0, 1)
        weights = dict(zip(TEMPLATES.TEMPLATES, model.mass, strict=True))
        self.assertGreater(weights[(1, 0)], weights[(0, 0)])
        self.assertAlmostEqual(weights[(1, 1)], weights[(0, 1)])
        with self.assertRaises(ValueError):
            model.advance((0, 0), 0, True)

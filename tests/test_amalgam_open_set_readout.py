"""Witness chronology and evidence-only fallback for the open-set readout."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch
import unittest

RESEARCH = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"


def read_module(name, file):
    spec = spec_from_file_location(name, RESEARCH / file)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


templates = read_module("causal_templates", "causal_templates.py")
with patch.dict("sys.modules", {"causal_templates": templates}):
    OPEN_SET = read_module("amalgam_open_set_for_tests", "open_set_readout.py")


class EvidenceControl:
    def __init__(self):
        self.events = []

    def update(self, key, outcome):
        self.events.append((key, outcome))

    def forecast(self, key):
        return 0.5, 0.95


class OpenSetReadoutTests(unittest.TestCase):
    def test_prior_witnesses_and_current_observations_use_previous_action(self):
        adaptive = EvidenceControl()
        view = (0, 1)
        reader = OPEN_SET.OpenSetReadout(lambda _, a: 0.1, [(view, 1, 1)], adaptive)
        options = reader.evidence_predictions(view, 1)
        self.assertEqual(adaptive.events, [((0, 1, 0), 1)])
        self.assertEqual(reader.weights, [0.5, 0.25, 0.25])
        reader.observe(view, 1, 0, options)
        reader.observe(view, 0, 1, reader.evidence_predictions(view, 0))
        self.assertEqual(adaptive.events[-2:], [((0, 1, 0), 0), ((0, 0, 1), 1)])

    def test_unsupported_evidence_can_select_fallback(self):
        adaptive = EvidenceControl()
        reader = OPEN_SET.OpenSetReadout(lambda _, a: 0.1, [], adaptive)
        view = (0, 0)
        self.assertIsNone(reader.forecast(reader.evidence_predictions(view, 1))[1])
        for _ in range(5):
            reader.observe(view, 1, 1, reader.evidence_predictions(view, 1))
        self.assertEqual(reader.forecast(reader.evidence_predictions(view, 1)), (0.95, 2))

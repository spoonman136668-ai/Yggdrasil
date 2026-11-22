"""Require each forecast to precede its target and one immutable witness append."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

FILE = (Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
        / "staged_public_readout.py")
SPEC = spec_from_file_location("amalgam_staged_readout_for_tests", FILE)
READOUT = module_from_spec(SPEC)
SPEC.loader.exec_module(READOUT)
VIEWS = ((0, 0), (0, 1))


def fixture():
    calls = []
    def forecast(view, *features):
        calls.append(("native", features))
        return 0.625

    def specialists(views, *features):
        calls.append(("specialists", features))
        return 0.25, 0.75

    def admit(identifier, views, row, **pins):
        calls.append(("append", identifier, views, row, pins))
        return "updated"

    model = SimpleNamespace(native=SimpleNamespace(experience_context_forecast=forecast),
                            specialist_forecasts=specialists, observe_experience=admit)
    return READOUT.StagedPublicReadout(model,"a"*64,VIEWS), calls


class StagedReadoutTests(unittest.TestCase):
    def test_staged_forecasts_only_access_previous_public_data(self):
        sequence, calls = fixture()
        self.assertEqual(sequence.first_action(0),(0.625,0.25,0.75))
        sequence.observe_transition(1)
        self.assertEqual(sequence.second_action(0),(0.625,0.25,0.75))
        self.assertEqual(calls,[("native",(0,)),("specialists",(0,)),
                                ("native",(0,1,0)),("specialists",(0,1,0))])
        self.assertEqual(sequence.observe_reward(1),"updated")
        row = {"s1":0,"x1":0,"s2":1,"x2":0,"y":1}
        self.assertEqual(calls[-1],("append","a"*64,VIEWS,row,
                                    {"source_sha256":EXPERIENCE_SOURCE,
                                     "packet_sha256":digest(canonical(["a"*64,VIEWS,row]))}))

    def test_out_of_order_or_duplicate_receipts_do_not_update(self):
        item, calls = fixture()
        for method in (item.observe_transition,item.second_action,item.observe_reward):
            with self.assertRaises(ValueError):
                method(0)
        item.first_action(0)
        with self.assertRaises(ValueError):
            item.first_action(1)
        item.observe_transition(0)
        item.second_action(1)
        item.observe_reward(1)
        with self.assertRaises(ValueError):
            item.observe_reward(1)
        self.assertEqual(sum(call[0]=="append" for call in calls),1)

    def test_malformed_observation_cannot_enter_readout(self):
        sequence, calls = fixture()
        sequence.first_action(0)
        with self.assertRaises(ValueError):
            sequence.observe_transition(True)
        with self.assertRaises(ValueError):
            sequence.second_action(1)
        self.assertEqual(len(calls),2)

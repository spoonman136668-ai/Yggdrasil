"""V29 independent finite synthetic information-sufficiency invariants."""
import itertools
import unittest

from research.itd02_v29_observational_equivalence_audit import (
    ALL_CASES, law, preferred_action, selected_map,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS, PUBLIC_CUES


class V29ObservationalEquivalenceTests(unittest.TestCase):
    def test_twelve_selected_public_rewards_equivalent(self):
        observed,mapping=selected_map()
        self.assertEqual(len(observed),12)
        self.assertEqual(len(set(observed)),12)
        for case in observed:
            self.assertEqual(law("A",case,mapping),law("B",case,mapping))
            self.assertEqual(law("A",case,mapping),law("B0",case,mapping))
        for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
            selected=mapping[(cue,first)]
            self.assertNotEqual(preferred_action(selected),selected)
            self.assertNotEqual(preferred_action(selected),ACTIONS[2])

    def test_alternative_action_optima_are_different(self):
        observed,mapping=selected_map()
        self.assertEqual(len(ALL_CASES),36)
        for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
            values={k:[law(k,(cue,first,a),mapping) for a in ACTIONS]
                    for k in ("A","B","B0")}
            argmax=lambda v:ACTIONS[max(range(3),key=lambda i:v[i])]
            self.assertEqual(argmax(values["A"]),ACTIONS[2])
            self.assertEqual(argmax(values["B0"]),ACTIONS[2])
            self.assertNotEqual(argmax(values["A"]),argmax(values["B"]))
            self.assertEqual(max(values["B"]),4.0)

    def test_one_new_selected_action_can_disambiguate(self):
        observed,mapping=selected_map()
        cue,first,selected=observed[0]
        probe=(cue,first,preferred_action(selected))
        self.assertNotIn(probe,observed)
        self.assertNotEqual(law("A",probe,mapping),law("B",probe,mapping))
        self.assertEqual(law("A",probe,mapping),law("B0",probe,mapping))
        with self.assertRaises(ValueError):
            law("hidden_oracle_world",probe,mapping)


if __name__=="__main__":
    unittest.main()

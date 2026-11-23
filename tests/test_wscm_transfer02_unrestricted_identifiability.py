"""Exhaustive unrestricted-wiring impossibility check; source-free, no seed.

This is a finite proof about a four-state public input, four-state intermediate
mapping and a witnessed nonconstant second-stage function. It is NOT a scored
world intervention, model training, or evidence of superior generalization.
"""
import itertools
import unittest

STATES = ((0, 0), (0, 1), (1, 0), (1, 1))
FIRST = (0, 1, 1, 0)
SECOND = (0, 0, 1, 1)


def disclosed_wiring(state):
    index = STATES.index(state)
    return (state[1], FIRST[index])  # fixed-grammar y_then_output


def supported_maps(observed):
    return tuple(
        wiring for wiring in itertools.product(STATES, repeat=4)
        if all(wiring[STATES.index(state)] == disclosed_wiring(state)
               for state in observed)
    )


def bit(wiring, state):
    middle = wiring[STATES.index(state)]
    return SECOND[2 * middle[0] + middle[1]]


class UnrestrictedIdentifiability(unittest.TestCase):
    def test_all_unrestricted_wirings_count_256(self):
        self.assertEqual(len(supported_maps(())), 256)

    def test_each_distinct_public_trace_only_removes_factor_four(self):
        for observed_count, expected_count in enumerate((256, 64, 16, 4, 1)):
            with self.subTest(observed_count=observed_count):
                self.assertEqual(len(supported_maps(STATES[:observed_count])),
                                 expected_count)

    def test_every_unobserved_start_remains_output_ambiguous(self):
        for observed_count in range(4):
            observed = STATES[:observed_count]
            compatible = supported_maps(observed)
            for unknown in STATES[observed_count:]:
                with self.subTest(observed_count=observed_count, unknown=unknown):
                    self.assertEqual({bit(m, unknown) for m in compatible}, {0, 1})

    def test_original_two_witnesses_are_balanced_on_unseen_query(self):
        compatible = supported_maps((STATES[1], STATES[2]))
        bit_counts = {v: sum(bit(m, STATES[3]) == v for m in compatible)
                      for v in (0, 1)}
        self.assertEqual((len(compatible), bit_counts),
                         (16, {0: 8, 1: 8}))

    def test_fixed_grammar_forecast_fails_unrestricted_counterexample(self):
        query = STATES[3]
        true_fixed = disclosed_wiring(query)
        fixed_prediction = SECOND[2 * true_fixed[0] + true_fixed[1]]
        compatible = supported_maps((STATES[1], STATES[2]))
        counterexample = next(m for m in compatible
                              if bit(m, query) != fixed_prediction)
        for known in (STATES[1], STATES[2]):
            self.assertEqual(counterexample[STATES.index(known)],
                             disclosed_wiring(known))
        self.assertNotEqual(bit(counterexample, query), fixed_prediction)

    def test_fully_identified_mapping_has_no_unwitnessed_input(self):
        compatible = supported_maps(STATES)
        self.assertEqual(len(compatible), 1)
        self.assertEqual(compatible[0], tuple(map(disclosed_wiring, STATES)))
        self.assertEqual(set(STATES) - set(STATES), set())


if __name__ == '__main__':
    unittest.main()

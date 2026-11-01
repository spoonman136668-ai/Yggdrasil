"""Independent conventional-control qualification; no scientific first use."""
import itertools
from fractions import Fraction
import unittest
from yggdrasil.public_causal_cells import PublicCausalCells

def oracle(observations):
    def choice(arms):
        if any(not arm for arm in arms):
            return None
        rates = [Fraction(sum(arm), len(arm)) for arm in arms]
        return None if rates[0] == rates[1] else int(rates[1] > rates[0])
    decisions = {choice(observations)}
    for arm in range(2):
        for index in range(len(observations[arm])):
            omitted = [list(x) for x in observations]
            del omitted[arm][index]
            decisions.add(choice(omitted))
    return decisions.pop() if len(decisions) == 1 and None not in decisions else None

class LeaveOneOutControlTests(unittest.TestCase):
    def test_exhaustive_independent_fraction_oracle_and_memory_invariance(self):
        for f0,s0,f1,s1 in itertools.product(range(5), repeat=4):
            cells=PublicCausalCells()
            arms=([0]*f0+[1]*s0, [0]*f1+[1]*s1)
            for action,observations in enumerate(arms):
                for outcome in observations:
                    cells.observe(0,action,outcome)
            before=cells.snapshot()
            self.assertEqual(cells.choose_loo_stable(0),oracle(arms),(f0,s0,f1,s1))
            self.assertEqual(cells.snapshot(),before)
            restored=PublicCausalCells.restore(before)
            self.assertEqual(restored.choose_loo_stable(0),oracle(arms))

    def test_fragile_preference_abstains(self):
        cells=PublicCausalCells()
        for outcome in (1,1,0): cells.observe(0,0,outcome)
        for outcome in (1,0): cells.observe(0,1,outcome)
        self.assertEqual(cells.choose(0),0)
        self.assertIsNone(cells.choose_loo_stable(0))

    def test_locality_and_fixed_memory_on_saturated_counts(self):
        cells=PublicCausalCells()
        cells._counts[0]=[[0,65535],[65535,0]]
        cells._counts[7]=[[65535,0],[0,65535]]
        before=cells.snapshot()
        self.assertEqual(cells.choose_loo_stable(0),0)
        self.assertEqual(cells.choose_loo_stable(0,retained=True),1)
        self.assertIsNone(cells.choose_loo_stable(1))
        self.assertEqual(cells.snapshot(),before)
        self.assertEqual(len(before),164)
        self.assertEqual(cells.LEARNED_BYTES,128)

    def test_invalid_inputs_preserve_memory(self):
        cells=PublicCausalCells(); before=cells.snapshot()
        for address,retained in [(-1,False),(7,False),(9,True),(True,False),(0,1)]:
            with self.assertRaises(ValueError):
                cells.choose_loo_stable(address,retained=retained)
            self.assertEqual(cells.snapshot(),before)

if __name__=='__main__': unittest.main()

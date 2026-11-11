import copy
import unittest
from capacity_proof import produce,verify,brute_depth_two


class WSP23Tests(unittest.TestCase):
    def test_independent_verifier_matches_both_full_small_closures(self):
        for mode in ('connected','allow_disconnected'):
            proof=produce(mode,2);r=verify(proof)
            self.assertTrue(r['verified']);self.assertEqual(set(proof['outputs'][-1]),brute_depth_two(mode))

    def test_missing_frontier_state_is_rejected(self):
        proof=produce('connected',2);proof['layers'][2].pop()
        with self.assertRaises(ValueError):verify(proof)

    def test_added_output_and_fake_null_output_rejected(self):
        for level in (0,2):
            proof=produce('allow_disconnected',2)
            value=next(v for v in range(64) if v not in proof['outputs'][level])
            proof['outputs'][level].append(value);proof['outputs'][level].sort()
            with self.assertRaises(ValueError):verify(proof)

    def test_changed_root_and_schema_rejected(self):
        proof=produce('connected',2);proof['layers'][0]=[0]
        with self.assertRaises(ValueError):verify(proof)
        proof=produce('connected',2);proof['schema']='other'
        with self.assertRaises(ValueError):verify(proof)

    def test_wrong_accounting_or_duplicate_layer_rejected(self):
        proof=produce('connected',2);proof['transitions']+=1
        with self.assertRaises(ValueError):verify(proof)
        proof=produce('connected',2);proof['layers'][1].append(proof['layers'][1][0])
        with self.assertRaises(ValueError):verify(proof)

    def test_invalid_capacity_and_nondeterministic_fields_rejected(self):
        with self.assertRaises(ValueError):produce('connected',7)
        proof=produce('connected',2);proof['max_sites']=True
        with self.assertRaises(ValueError):verify(proof)
        self.assertEqual(produce('connected',2),produce('connected',2))


if __name__=='__main__':unittest.main()

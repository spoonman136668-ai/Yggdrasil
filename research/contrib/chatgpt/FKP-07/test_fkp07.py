"""FKP-07 source boundary, intervention, associative prior and retention tests."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import source
import model


class FKP07(unittest.TestCase):
    def test_public_source_scope_and_paid_budget(self):
        actions=source.history_actions(30000)
        self.assertEqual(len(set(actions)),64)
        w=source.World(30000,'history',actions)
        self.assertIn(w.observe(actions[0]),(0,1))
        with self.assertRaises(ValueError):w.observe(actions[0])
        with self.assertRaises(ValueError):w.observe((1<<32)-1)
        with self.assertRaises(ValueError):source.history_actions(1800)
        with self.assertRaises(ValueError):source.World(1800,'new',(0,1))
        with self.assertRaises(ValueError):source.World(2800,'negative',(0,1))

    def test_historical_observation_without_parent_labels(self):
        act=source.history_actions(30000)
        w=source.World(30000,'history',act)
        observations=tuple((x,w.observe(x)) for x in act)
        self.assertEqual(w.charged,64)
        self.assertEqual(len(observations),64)
        self.assertEqual(set(map(len, observations)),{2})
        with self.assertRaises(ValueError):w.observe(act[0])
        self.assertFalse(hasattr(w,'law'))  # No parent label on public interface

    def test_numeric_prior_pair_inventory_and_shift_negative(self):
        pairs=tuple(model.PAIR_INDEX[p] for p in ((1,6),(3,10),(8,17),(20,29)))
        shifted=model.scrambled_pairs(pairs)
        self.assertEqual(len(set(shifted)),4)
        self.assertNotEqual(set(pairs),set(shifted))
        grammar=model.fkp06_module().laws()
        a=model.priority_mask(grammar,pairs)
        b=model.priority_mask(grammar,shifted)
        self.assertEqual(a.bit_count(),6)
        self.assertEqual(b.bit_count(),6)
        self.assertEqual(model.mass(3,0),2)
        self.assertEqual(model.mass(3,3),2+200000)

    def test_cold_retention_and_tamper_boundary(self):
        contexts={(800,1):{'alive':23,'prediction':(0,1,1)},
                  (800,2):{'alive':12,'prediction':(1,0,0)}}
        blob,digest,restored=model.checkpoint(contexts,'digest',(2,4,6,8))
        self.assertEqual(len(digest),64)
        self.assertEqual(len(restored['versions']),2)
        self.assertNotEqual(restored['versions'][0]['predicted_bits'],
                            restored['versions'][1]['predicted_bits'])
        self.assertEqual(restored['schema'],'fkp07.versioned-causal-memory.v1')
        self.assertNotEqual(blob,b'')

    def test_unknown_law_abstains(self):
        p,confidence=model.predicted(0,0,(0,1,2))
        self.assertIsNone(p)
        self.assertEqual(confidence,0.0)
        self.assertEqual(model.paired_ci((0.0,0.0)),[0,0])


if __name__=='__main__':
    unittest.main()

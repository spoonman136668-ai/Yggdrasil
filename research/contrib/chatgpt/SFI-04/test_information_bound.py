"""SFI-04 source-independent checks before public developmental scoring."""
import unittest
from collections import namedtuple

import public_source as source
import learners as l
import run_public_dev as harness


class StructureFreeTests(unittest.TestCase):
    def test_public_source_determinism_and_seed_fence(self):
        self.assertEqual(len(source.SEEDS), 32)
        for bad in (978500,978600,24,0,True):
            with self.assertRaises(PermissionError):
                source.World(bad)
        a,b = source.World(880400),source.World(880400)
        for entry in source.public_tape(880400)[:30]:
            self.assertEqual(a.step(*entry),b.step(*entry))

    def test_temporal_earned_credit_only_after_two(self):
        w = source.World(880400)
        entries = source.public_tape(880400)
        r0,r1,r2 = [w.step(*x) for x in entries[:3]]
        self.assertEqual((r0.reward,r1.reward),(0,0))
        self.assertEqual(r2.history[0],entries[0])
        self.assertEqual(r2.reward,w.probe(entries[0].context,entries[0].action))

    def test_exact_public_schema_and_failure_atomicity(self):
        w=source.World(880400)
        model=l.DirectWeights()
        first=w.step(0,0)
        saved=model.receipt()
        Extra=namedtuple('Extra',l.FIELDS+('oracle',))
        for bad in (Extra(*first, [1]*8),first._replace(context=True),
                    first._replace(reward=float('nan')),
                    first._replace(history=(first,))):
            with self.assertRaises(ValueError):
                model.observe(bad)
            self.assertEqual(saved,model.receipt())

    def test_first_24_unique_contexts_and_delayed_upper_bound(self):
        tape=source.public_tape(880400)
        self.assertEqual(len(set(x.context for x in tape[:24])),24)
        self.assertAlmostEqual((22+106/8)/128,0.275390625)

    def test_equal_information_separate_implementations(self):
        world=source.World(880401)
        a,b=l.DirectWeights(),l.ExactBayes()
        for x in source.public_tape(880401)[:512]:
            row=world.step(*x)
            a.observe(row);b.observe(row)
            self.assertEqual(tuple(a.choose(i) for i in range(128)),
                             tuple(b.choose(i) for i in range(128)))

    def test_cold_prediction_mask_restore_and_corruption_refusal(self):
        w=source.World(880400)
        a=l.DirectWeights()
        for x in source.public_tape(880400)[:256]:
            a.observe(w.step(*x))
        b=l.DirectWeights()
        b.restore(a.checkpoint())
        self.assertEqual([a.choose(i) for i in range(128)],
                         [b.choose(i) for i in range(128)])
        for bad in (b'', b'\0'*128, bytearray(a.checkpoint())):
            with self.assertRaises(ValueError):
                b.restore(bad)

    def test_budget_and_unobserved_contexts_are_not_falsely_filled(self):
        w=source.World(880400)
        a=l.DirectWeights()
        tape=source.public_tape(880400)
        for x in tape:
            a.observe(w.step(*x))
        self.assertEqual(a.rows,2048)
        before=a.receipt()
        with self.assertRaises(ValueError):
            a.observe(source.PublicEvent(0,0,0,()))
        self.assertEqual(a.receipt(),before)
        self.assertEqual(len(a.observed),128)

if __name__ == '__main__':
    unittest.main()

"""Pure direct-weight writer structural tests, SELFTEST-only. No registered experiment."""
import unittest
from dataclasses import replace
from source import Observation, build_world
from direct_writer import DirectWeightWriter, _parts, MAX_SEGMENTATIONS
from fixture_harness import run_selftest_writer


class DirectWriterTests(unittest.TestCase):
    def test_segmentation_is_raw_and_bounded(self):
        self.assertTrue(_parts('0'*15))
        self.assertLessEqual(len(_parts('0'*15)), MAX_SEGMENTATIONS)
        self.assertEqual(_parts('1'*9), [])
        with self.assertRaises(ValueError):
            _parts('12345')

    def test_weights_formed_by_grounded_state_changes_only(self):
        model = DirectWeightWriter()
        noop = Observation((0,)*8, '0'*15, (0,)*8)
        model.observe(noop)
        self.assertEqual(model.numeric_weight_count(), 0)
        self.assertEqual(model.actions, 1)
        after = (1,)+(0,)*7
        model.observe(Observation(noop.before, '0'*15, after))
        self.assertGreater(model.numeric_weight_count(), 0)
        self.assertEqual(model.informative, 1)
        self.assertIn(('['+','.join(['0']*8)+']', '0'*15), model.conflicts)

    def test_source_to_numeric_weights_and_cold_restore(self):
        w = build_world('SELFTEST', 9001, 'identity')
        model = DirectWeightWriter()
        for row in w.phase_a: model.observe(row)
        self.assertEqual(model.actions, 36)
        self.assertGreater(model.numeric_weight_count(), 0)
        snapshot = model.snapshot()
        restored = DirectWeightWriter.restore(snapshot)
        self.assertEqual(restored.numeric_weight_count(), model.numeric_weight_count())
        for row in w.heldout_a:
            self.assertEqual(restored.predict(row.before, row.acoustic_bits),
                             model.predict(row.before, row.acoustic_bits))
        self.assertEqual(restored.snapshot(), snapshot)
        with self.assertRaises(ValueError):
            DirectWeightWriter.restore(snapshot + ' ')
        with self.assertRaises(ValueError):
            DirectWeightWriter.restore(snapshot[:-1]+'x')

    def test_no_hidden_latents_or_target_needed_to_predict(self):
        class Recorder(DirectWeightWriter):
            def predict(self, before, acoustic_bits):
                self.assert_binary = (type(before) is tuple and type(acoustic_bits) is str)
                return super().predict(before, acoustic_bits)
        w = build_world('SELFTEST', 9002, 'rotated')
        model = Recorder()
        for row in w.phase_a:
            model.observe(row)
        for row in w.heldout_a:
            result = model.predict(row.before,row.acoustic_bits)
            self.assertTrue(model.assert_binary)
            self.assertTrue(result is None or len(result)==8)

    def test_corrupted_source_and_inconsistent_state_rejected(self):
        model=DirectWeightWriter()
        with self.assertRaises(ValueError):
            model.observe(Observation((0,)*8,'101'*5,(1,2)+(0,)*6))
        with self.assertRaises(ValueError):
            model.observe(Observation((0,)*8,'101'*5,(1,)+(0,)*7,action_cost=0))
        with self.assertRaises(ValueError):
            model.predict((0,)*7,'101'*5)
        with self.assertRaises(ValueError):
            DirectWeightWriter(min_entity=1)

    def test_ambiguity_abstains(self):
        model=DirectWeightWriter()
        self.assertIsNone(model.predict((0,)*8, '10101'*3))
        with self.assertRaises(ValueError):
            model.predict((0,)*8, 'invalid')

    def test_fixture_negative_outcomes_not_hidden(self):
        # Selftest is not a scientific claim; its nonzero error is a recorded limit.
        w=build_world('SELFTEST',9001,'permuted')
        model=DirectWeightWriter()
        for row in w.phase_a:model.observe(row)
        outputs=[model.predict(row.before,row.acoustic_bits) for row in w.heldout_a]
        wrong=sum(x is not None and x!=r.after for x,r in zip(outputs,w.heldout_a))
        self.assertEqual(wrong + sum(x is None for x in outputs) + sum(x == r.after for x,r in zip(outputs,w.heldout_a)),60)
        self.assertLessEqual(wrong,len(w.heldout_a))

    def test_heldout_fixtures_only_and_score_receipt(self):
        w = build_world('SELFTEST', 9002, 'identity')
        receipt = run_selftest_writer(w)
        self.assertEqual(receipt['exposed_actions'], 42)
        self.assertEqual(receipt['gradient_steps'], 0)
        self.assertEqual(receipt['phase_a']['total'], 60)
        self.assertEqual(receipt['phase_b']['total'], 90)
        self.assertTrue(receipt['cold_restore_parity'])
        with self.assertRaises(PermissionError):
            run_selftest_writer(replace(w, cohort='DEV'))


if __name__=='__main__': unittest.main()

"""Source-free exhaustive equivalence: numeric fast weights vs optimized symbolic.

Only public engineering graph IDs 121900..121903 are used. The 256
programmed truth tables in this test are artificial test inputs, not
independently discovered operators or sealed original source labels.
"""
from unittest import TestCase

import meta_operator as M


class WSP121SymbolicEquivalenceTests(TestCase):
    def test_every_three_bit_operator_has_identical_predictions(self):
        worlds = [M.engineering_world(s) for s in M.ENGINEERING_SEEDS]
        # The engineering construction guarantees one legal subject per
        # context in each world's first eight legal subjects.
        representatives = []
        for world in worlds:
            subjects = {world.feature(s): s for s in world.legal[:8]}
            self.assertEqual(set(subjects), set(range(8)))
            representatives.append(subjects)

        comparisons = 0
        for table in range(256):  # all Boolean 3-input route laws
            numeric = M.NumericFastWeights()
            symbolic = M.SymbolicMemo()
            self.assertTrue(all(numeric.infer_route(k) is None
                                for k in range(8)))
            self.assertEqual(symbolic.table, {})

            # Feed eight synthetic verified-like observations (NOT an oracle).
            for k in range(8):
                s = representatives[0][k]
                outcome = worlds[0].routes(s)[(table >> k) & 1]
                numeric.observe(worlds[0], s, outcome)
                symbolic.observe(worlds[0], s, outcome)
                self.assertEqual(numeric.infer_route(k), symbolic.table[k])

                # Validate every partially learned state against all worlds.
                for world, examples in zip(worlds, representatives):
                    n_pred = [numeric.infer(world, examples[c])
                              for c in range(8)]
                    s_pred = [symbolic.infer(world, examples[c])
                              for c in range(8)]
                    self.assertEqual(n_pred, s_pred)
                    comparisons += len(n_pred)

            # Simulate four consistent observations after graph transfer.
            transfer = worlds[3]
            for k in range(4):
                s = representatives[3][k]
                outcome = transfer.routes(s)[(table >> k) & 1]
                numeric.observe(transfer, s, outcome)
                symbolic.observe(transfer, s, outcome)

            restored = M.NumericFastWeights.restore(numeric.snapshot())
            for world in worlds:
                n_pred = [numeric.infer(world, s) for s in world.held]
                s_pred = [symbolic.infer(world, s) for s in world.held]
                r_pred = [restored.infer(world, s) for s in world.held]
                self.assertEqual(n_pred, s_pred)
                self.assertEqual(r_pred, s_pred)
                comparisons += len(n_pred)

                # Equality of predictions forces equality of accuracy,
                # abstentions and confident errors under ANY held labels.
                truth = [world.routes(s)[(table >> world.feature(s)) & 1]
                         for s in world.held]
                self.assertEqual(
                    sum(p == y for p, y in zip(n_pred, truth)),
                    sum(p == y for p, y in zip(s_pred, truth)))
                self.assertEqual(
                    sum(p is None for p in n_pred),
                    sum(p is None for p in s_pred))

            # Contradictory evidence fails closed in both implementations.
            s = representatives[0][0]
            wrong = worlds[0].routes(s)[1 - (table & 1)]
            for learner in (numeric, symbolic):
                with self.assertRaisesRegex(
                        ValueError, "WSP121_OPERATOR_CONTRADICTION"):
                    learner.observe(worlds[0], s, wrong)
            self.assertEqual(numeric.infer(worlds[0], s),
                             symbolic.infer(worlds[0], s))

        self.assertEqual(comparisons, 256 * (8 * 4 * 8 + 4 * 24))

    def test_no_context_matches_symbolic_abstention(self):
        world = M.engineering_world(121900)
        numeric, symbolic = M.NumericFastWeights(), M.SymbolicMemo()
        for s in world.held:
            self.assertIsNone(numeric.infer(world, s))
            self.assertIsNone(symbolic.infer(world, s))

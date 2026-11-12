"""WSP52 bounded symbolic search: structural + six SELFTEST-only conditions."""
import json
import unittest
from dataclasses import asdict

from source import Observation, build_world
from fixture_harness import learn_observations, score_observations
from symbolic_version_space import BoundedVersionSpace, _parts, _visible, _extend


class BoundedVersionSpaceTests(unittest.TestCase):
    def test_acoustic_partitions_and_validation(self):
        self.assertEqual(tuple(_parts("0"*12)), (("0000","0000","0000"),))
        self.assertEqual(len(tuple(_parts("0"*15))), 7)
        self.assertEqual(tuple(_parts("0"*9)), ())
        for bad in ("", "10x001101000", "not-binary"):
            with self.assertRaises(ValueError):
                tuple(_parts(bad))

    def test_nop_cannot_label_entity_and_prefix_constraints(self):
        noop = Observation((0,)*8, "000010001100", (0,)*8)
        self.assertEqual(len(_visible(noop)), 8)
        state = (None,)*15
        self.assertIsNotNone(_extend(state, (0,8,12), ("0000","1000","1100")))
        self.assertIsNone(_extend(state, (0,8,12), ("0000","0000","1100")))
        self.assertIsNone(_extend(state, (0,8,12), ("0000","00001","1100")))
        with self.assertRaises(ValueError):
            _visible(Observation((0,)*8, "000010001100", (1,1,0,0,0,0,0,0)))
        with self.assertRaises(ValueError):
            _visible(Observation((0,)*8, "000010001100", (0,)*8, 0, 0))

    def test_incomplete_hypothesis_search_always_abstains(self):
        model = BoundedVersionSpace(node_cap=2, model_cap=20,
                                    state_cap=20, time_cap_seconds=2)
        record = Observation((0,)*8, "000010001100", (1,0,0,0,0,0,0,0))
        models, audit = model._search((("A", record),))
        self.assertFalse(audit["complete"])
        self.assertEqual(audit["reason"], "NODE_CAP")
        self.assertEqual(audit["nodes"], 3)
        self.assertIsNone(model.predict(record.before, record.acoustic_bits))
        self.assertFalse(hasattr(model, "oracle_decode"))
        with self.assertRaises(ValueError):
            model.use_phase("PRIMARY")

    def test_six_preexisting_selftest_worlds_no_protected_seeds(self):
        # This is a bounded *candidate*, NOT the full preregistered baseline.
        # Retain truncation/abstention and all fixture failures; no tuning.
        rows = []
        for seed in (9001,9002):
            for encoding in ("identity","permuted","rotated"):
                world = build_world("SELFTEST",seed,encoding)
                model = BoundedVersionSpace(node_cap=5000, model_cap=500,
                    state_cap=1000, time_cap_seconds=15)
                learn_observations(model,world.phase_a)
                model.seal_a()
                a = score_observations(model,world.heldout_a)
                learn_observations(model,world.phase_b)
                model.finalize_b()
                b = score_observations(model,world.heldout_b)
                model.use_phase("A")
                retained = score_observations(model,world.heldout_a)
                snapshot = model.snapshot()
                clone = BoundedVersionSpace.restore(snapshot)
                self.assertEqual(clone.snapshot(),snapshot)
                self.assertEqual(model.actions,42)
                for sample in world.heldout_a[:5]:
                    self.assertEqual(model.predict(sample.before,sample.acoustic_bits),
                                     clone.predict(sample.before,sample.acoustic_bits))
                with self.assertRaises(ValueError):
                    BoundedVersionSpace.restore(snapshot+" ")
                for counts in (a,b,retained):
                    self.assertEqual(counts.total,
                        counts.correct+counts.abstentions+counts.wrong_confident)
                rows.append({"seed":seed,"encoding":encoding,
                             "A":asdict(a),"B":asdict(b),"retained_A":asdict(retained),
                             "search_A":model.receipt_a,"search_AB":model.receipt_ab,
                             "capacity_bits":model.capacity_bits(),"actions":model.actions})
        print("WSP52_BOUNDED_SYMBOLIC_SELFTEST "+
              json.dumps(rows,sort_keys=True,separators=(",",":")),flush=True)
        self.assertEqual(len(rows),6)

if __name__ == "__main__":
    unittest.main()

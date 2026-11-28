"""Capacity and retained-interference qualification on generated public worlds."""
import unittest
from specialization_scaling_audit import run, measure, families
from local_cell_specialization import SpecializedColony

class ScalingTests(unittest.TestCase):
    def test_seeded_families_are_independent_and_deterministic(self):
        self.assertEqual(families(3),families(3))
        self.assertNotEqual(families(3),families(17))
        self.assertEqual(len(set(x for x,_ in families(41))),16)
        for bits, target in families(41):
            self.assertEqual(target,sum(bits)%2==1)

    def test_all_observations_and_errors_are_accounted(self):
        report = run()
        self.assertEqual(len(report["runs"]),12)
        self.assertEqual(len(report["capacity_controls"]),4)
        for row in report["runs"]+report["capacity_controls"]:
            n=row["relationships"]
            self.assertEqual(row["actions"],2*n)
            self.assertEqual(row["table_accepted"],2*n)
            self.assertEqual(row["native_accepted"]+row["native_rejected"],2*n)
            self.assertTrue(row["cold_restore_exact"])
            self.assertLessEqual(row["native_checkpoint_bytes"],32768)
            for arm in ("native","table"):
                for portion,size in (("trained",n),("heldout",16-n)):
                    self.assertEqual(sum(row[arm+"_"+portion].values()),size)
            self.assertGreater(row["native_checkpoint_bytes"],0)
            self.assertGreater(row["table_bytes"],0)
            self.assertGreaterEqual(row["native_cpu_ns"],0)
            self.assertGreaterEqual(row["table_cpu_ns"],0)

    def test_capacity_limits_and_restoration(self):
        with self.assertRaises(ValueError):
            SpecializedColony(slots_per_cell=5)
        small=measure(3,8,1)
        big=measure(3,8,4)
        self.assertGreater(small["native_rejected"],0)
        self.assertEqual(big["native_rejected"],0)
        self.assertTrue(big["cold_restore_exact"])

    def test_generated_interference_is_preserved_as_negative_control(self):
        report=run()
        grouped={n:[] for n in (2,4,8,12)}
        for row in report["runs"]:
            grouped[row["relationships"]].append(row)
            self.assertEqual(row["native_rejected"],0)
        expected={2:(6,6),4:(3,12),8:(6,24),12:(3,36)}
        for n,(native_count,tabular_count) in expected.items():
            self.assertEqual(sum(x["native_trained"]["correct"] for x in grouped[n]),native_count)
            self.assertEqual(sum(x["table_trained"]["correct"] for x in grouped[n]),tabular_count)
        self.assertGreater(sum(row["native_heldout"]["wrong"]
                               for row in report["runs"]),0)
        self.assertEqual(sum(row["table_heldout"]["wrong"]
                             for row in report["runs"]),0)

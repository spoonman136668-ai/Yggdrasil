import importlib.util
from pathlib import Path
import sys
import unittest
p=Path(__file__).parent/"source_pilot.py"
s=importlib.util.spec_from_file_location("y_f49_preflight",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)

class PairNullF49(unittest.TestCase):
    def test_disjoint_fresh_cohorts(self):
        self.assertFalse(set(m.FIT)&set(m.DIAG))
        self.assertFalse(set(m.DIAG)&set(m.ORIGINAL))
        self.assertFalse(set(m.FAMILIES)&set(m.ORIGINAL_FAMILIES))
        for old in m.OLD_ORIGINALS:
            self.assertFalse(set(old)&set(m.DIAG))
    def test_reserved_source_not_accessible(self):
        for args in ((442000,664,0,2,0,97000),
                     (422000,660,0,2,0,97000),
                     (401100,660,0,2,0,97000),
                     (441100,660,0,0,0,97000)):
            with self.assertRaises(ValueError):
                m.base.parent.prior.source(*args)
    def test_equal_public_pairs_and_anchor_count(self):
        couples=m.base.parent.prior.public_pairs(441100,660,2,0)
        null=m.base.parent.prior.public_pairs(441100,660,2,1)
        self.assertEqual(len(couples),len(null))
        self.assertEqual(len(couples),12)
        self.assertEqual(len(m.base.parent.prior.flat(couples)),24)
        self.assertTrue(all(a[0]==b[0] for a,b in couples))
    def test_task_mapping_is_strict(self):
        for family in m.FAMILIES:
            for bits in ((0,1,1),(1,0,0),(1,1,1)):
                self.assertEqual(m.base.parent.prior.task(bits,family),
                  m.base.parent.old_task(bits,480+family-660))
    def test_two_sensor_paid_limit(self):
        port=m.base.parent.prior.Port((.1,.2,.3,.4))
        port.buy(0);port.buy(1)
        with self.assertRaises(ValueError):
            port.buy(2)

if __name__=="__main__":unittest.main()

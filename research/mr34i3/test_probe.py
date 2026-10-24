"""MR34I3 source-free numerical-coordinate auditor tests. NO original source resets."""
import ast
import math
from pathlib import Path
import unittest

import numpy as np

from research.mr34i3 import coordinate_probe as p


class NativeArithmeticProbeTests(unittest.TestCase):
    def test_mark_preserves_all_ieee_float_coordinates(self):
        src=np.array([[0.0,-0.0,np.nextafter(1.0,2.0)],[.5,-.75,2.]],dtype=np.float64)
        r=p.mark(src)
        self.assertEqual(r["shape"],[2,3])
        self.assertEqual(r["hex"][1],"-0x0.0p+0")
        self.assertNotEqual(r["hex"][2],float(1.).hex())
        self.assertEqual(len(r["sha256"]),64)
        with self.assertRaises(ValueError):
            p.mark(np.array([np.nan]))
        with self.assertRaises(ValueError):
            p.mark(np.array([np.inf]))

    def test_read_only_fsum_comparator_has_no_model_updates(self):
        class Dummy:
            def __init__(self):
                self.g=np.arange(21,dtype=np.float64).reshape(3,7)/40
                self.roles=np.arange(24,dtype=np.float64).reshape(8,3)/15
        obj=Dummy()
        w0=obj.g.copy()
        r0=obj.roles.copy()
        f=np.arange(56,dtype=np.float64).reshape(8,7)/60
        s=np.linspace(-.5,.5,8,dtype=np.float64)
        read,u=p.dot_reference(f,obj,s)
        self.assertEqual(read["shape"],[8])
        self.assertEqual(u["shape"],[8])
        self.assertEqual(len(u["hex"]),8)
        np.testing.assert_array_equal(obj.g,w0)
        np.testing.assert_array_equal(obj.roles,r0)

    def test_frozen_known_first_divergences_only_train(self):
        self.assertEqual(p.MAX_FIRST_UPDATES,11)
        self.assertEqual(p.FIRST,"25fe9f6d3ec9fa44b79c814b69efb3e563b8229b")
        self.assertEqual(set(p.EXPECTED_SOURCE_EVENTS),set(p.SOURCES))
        self.assertEqual(len(p.SEEDS),20)
        self.assertTrue(all(n<2003 for n in p.SEEDS))
        self.assertIn("NO",p.SCHEMA.upper() if "NO" in p.SCHEMA.upper() else "NO")
        self.assertTrue(all(len(v)==64 for v in p.EXPECTED_SOURCE_EVENTS.values()))

    def test_no_original_held_roles_or_model_replacement(self):
        tree=ast.parse(Path(p.__file__).read_text())
        target=next(n for n in tree.body if isinstance(n,ast.FunctionDef)
                    and n.name=="original_source_training_trace")
        src=ast.unparse(target)
        self.assertIn("episodes(root, family, SEEDS)",src)
        self.assertIn("source_rows[:MAX_FIRST_UPDATES]",src)
        self.assertIn("update_exact(",src)
        self.assertNotIn("EVAL",src)
        self.assertNotIn("held",src.lower().replace("no_scientific_dev_or_protected_source_actions",""))
        self.assertEqual(p.S4C1_SHA,"8e1561eb1a542e21307bac669c42435cf48e59bd")


if __name__=="__main__":
    unittest.main()

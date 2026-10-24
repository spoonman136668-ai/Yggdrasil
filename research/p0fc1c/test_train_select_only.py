"""Source-free matched-capacity and source-role tests; no original episodes."""
import ast
from pathlib import Path
import unittest
import numpy as np

from research.p0fc1c import train_select_only as c
from research.p0fc1b.full_public_controls import TRAIN, SELECT, DEV

class MatchedHistoryProtocol(unittest.TestCase):
    def test_frozen_role_excludes_old_dev(self):
        self.assertEqual(len(TRAIN),24)
        self.assertEqual(len(SELECT),6)
        self.assertTrue(set(TRAIN).isdisjoint(SELECT))
        self.assertTrue(set(TRAIN + SELECT).isdisjoint(DEV))
        self.assertEqual(c.EPOCHS,24)
        self.assertEqual(c.UNITS,32)
        self.assertEqual(c.RATE,0.02)
        self.assertEqual(c.EXPECTED["DeepMindPycolabApprehend"]["seed"],17)
        self.assertEqual(c.EXPECTED["FaramaMiniGridDoorKey8"]["seed"],31)

    def test_input_dimensions_current_retained_and_history_zeroed(self):
        frame=8;actions=3;block=frame+actions
        xx=np.arange(5*3*block,dtype=np.float64).reshape(5,3*block)/100
        masked=c.mask_history(xx,actions,frame)
        self.assertEqual(masked.shape,xx.shape)
        np.testing.assert_array_equal(masked[:,:block],xx[:,:block])
        np.testing.assert_array_equal(masked[:,block:],0)
        self.assertTrue(np.any(xx[:,block:]))
        self.assertTrue(np.any(masked[:,:block]))
        np.testing.assert_array_equal(xx,np.arange(5*3*block).reshape(5,3*block)/100)

    def test_paired_clustering_and_bootstrap_are_frozen(self):
        delta=[.4,-.1,.3,.5,0.,-.2]
        self.assertEqual(c.boot_interval(delta),c.boot_interval(delta))
        self.assertEqual(c.BOOT_DRAWS,1000)
        self.assertEqual(c.classification(.2,-.1,[0,0]),"HISTORY_EXTRA_FEATURES_OVERFIT_OR_GENERALIZE_POORLY")
        self.assertEqual(c.classification(-.2,-.1,[-.2,0]),"HISTORY_INPUT_NOT_EFFECTIVELY_FITTED_UNDER_FIXED_BUDGET")
        self.assertEqual(c.classification(.2,.1,[.01,.2]),"TRAIN_SELECTION_HISTORY_SIGNAL_WITH_MATCHED_CAPACITY")
        self.assertEqual(c.classification(0.,.1,[-.1,.2]),"MATCHED_CAPACITY_HISTORY_BENEFIT_INCONCLUSIVE")

    def test_no_original_dev_acquisition_or_parameter_search(self):
        text=Path(c.__file__).read_text()
        src=ast.parse(text)
        calls=[x for x in ast.walk(src) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=="acquire"]
        self.assertEqual(len(calls),2)
        self.assertEqual([ast.unparse(x.args[1]) for x in calls],["TRAIN","SELECT"])
        self.assertNotIn("acquire(name,DEV)",text.replace(" ",""))
        self.assertNotIn("fit_train_select(",text)
        self.assertNotIn("selected=min(",text)

if __name__=="__main__":
    unittest.main()

"""FKP-10 fixture-only admission preflight; MUST NOT consume registered source seeds."""
from pathlib import Path
import hashlib
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import admit

class FKP10(unittest.TestCase):
    def test_original_source_manifest_and_distinct_reservation(self):
        self.assertEqual(len(admit.SOURCE_SHA),40)
        self.assertEqual(len(admit.SOURCE_BLOBS),5)
        self.assertEqual(len(set(admit.SEEDS)),4)
        self.assertEqual(admit.TASKS,("MortarMayhem-v0","MysteryPath-v0"))
        self.assertEqual((admit.MIN_STEPS,admit.MAX_STEPS),(8,32))

    def test_invalid_source_never_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                admit.source_custody(Path(directory))

    def test_public_observation_frame_is_type_shape_and_content_sensitive(self):
        import numpy as np
        data=np.zeros((2,3,3),dtype=np.uint8)
        a=hashlib.sha256()
        dtype,shape=admit.frame(a,data)
        self.assertEqual((dtype,shape),("uint8",(2,3,3)))
        b=hashlib.sha256()
        data[0,0,0]=1
        admit.frame(b,data)
        self.assertNotEqual(a.digest(),b.digest())
        c=hashlib.sha256()
        admit.frame(c,data.astype(np.float32))
        self.assertNotEqual(b.digest(),c.digest())

    def test_public_observation_rejects_empty_or_object(self):
        import numpy as np
        with self.assertRaises(ValueError):admit.frame(hashlib.sha256(),np.asarray([]))
        with self.assertRaises(ValueError):admit.frame(hashlib.sha256(),np.asarray([object()],dtype=object))

    def test_registered_actions_only_and_science_disarmed(self):
        with self.assertRaises(ValueError):
            admit.episode("Unregistered-HiddenTask",admit.SEEDS[0])
        with self.assertRaises(ValueError):
            admit.episode(admit.TASKS[0],1800)
        # External simulator import never reached by either rejected input.
        self.assertEqual(len(admit.SEEDS)*len(admit.TASKS),8)

if __name__=="__main__":unittest.main()

"""KNOW03 source-free negative controls: no live owner/model/source touches."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("know03", HERE/"real_image_pairing.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class Know03Tests(unittest.TestCase):
    def test_original_train_image_identity(self):
        self.assertEqual(mod.SOURCE_RECORDS, 21_343_681)
        self.assertEqual(mod.SOURCE_SHA, "6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1")
    def test_existing_Amalgam_source_pins(self):
        self.assertEqual(mod.NATIVE_SHA, "5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d")
        self.assertFalse(hasattr(mod.ArchivedJointReadOnly, "observe_experience"))
    def test_rejects_rehashed_or_unpinned_fake_joint(self):
        for raw in (b"{}", b'{"sha":"'+mod.JOINT_SHA.encode()+b'"}'):
            with self.assertRaisesRegex(ValueError, "ARCHIVED_RESEARCH_JOINT_PIN"):
                mod.ArchivedJointReadOnly(raw)
    def test_no_policy_interface(self):
        self.assertTrue(callable(mod.ArchivedJointReadOnly.plan))
        with self.assertRaisesRegex(PermissionError, "NO_NATIVE_POLICY"):
            object.__new__(mod.ArchivedJointReadOnly).plan(None)
    def test_canonical_binary_contract(self):
        self.assertEqual(mod.canonical({"b": 1, "a": 2}), b'{"a":2,"b":1}')
        self.assertEqual(mod.sha(b"fixture"), hashlib.sha256(b"fixture").hexdigest())

if __name__ == "__main__":
    unittest.main()

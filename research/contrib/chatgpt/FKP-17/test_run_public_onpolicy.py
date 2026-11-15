"""FKP-17 source-safe diagnostic driver eligibility, not scientific DEV."""
from pathlib import Path
import unittest

import run_public_onpolicy as driver


class PublicTrainingDriverTests(unittest.TestCase):
    def test_frozen_train_only_source_seed(self):
        self.assertEqual(driver.TRAIN_SAFE_SEED, 978100)
        for forbidden in (978500, 978531, 978600, 978663,
                          976500, 979100, 978200, 978215):
            with self.subTest(seed=forbidden):
                with self.assertRaises(PermissionError):
                    driver.build_and_run_public_training("not-opened", forbidden)

    def test_driver_contains_no_science_or_owner_entrypoint(self):
        text = Path(driver.__file__).read_text("utf-8")
        self.assertIn("PUBLIC_TRAIN_DIAGNOSTIC_ONLY_NOT_SCIENCE", text)
        self.assertIn("public_training", text)
        self.assertNotIn("allow_dev=True", text)
        self.assertNotIn("open_dev", text)
        self.assertNotIn("reserved_transfer_opened=True", text)
        self.assertNotIn("native_promoted=True", text)

    def test_never_called_original_source_on_preflight(self):
        for wrong in (True, False, 978100.0, "978100"):
            with self.assertRaises((PermissionError, ValueError)):
                driver.build_and_run_public_training("not-opened", wrong)


if __name__ == "__main__":
    unittest.main()

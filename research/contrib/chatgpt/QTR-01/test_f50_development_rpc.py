"""F50 development bridge negative-only tests: never first-use target laws."""
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import f50_comparison_harness as harness
import f50_development_rpc as dev
import f50_worlds as world


def ticket():
    return {"candidate_sha": "a"*40, "ubuntu_pass": True,
            "windows_pass": True, "protocol_blob": world.PREREG_BLOB,
            "operator_first_use": True}


class DevelopmentAdmissionGuards(unittest.TestCase):
    def test_refuses_all_ungated_admissions_before_spawn(self):
        with patch.object(dev.subprocess, "Popen") as spawn:
            with self.assertRaisesRegex(dev.DevelopmentTransportRejected, "FIRST_USE_BLOCKED"):
                dev.DevelopmentEvaluatorClient(4096, 4013)
            with self.assertRaisesRegex(dev.DevelopmentTransportRejected, "OWNER_ADMISSION_REQUIRED"):
                dev.DevelopmentEvaluatorClient(4096, 4013, ticket())
            with self.assertRaisesRegex(dev.DevelopmentTransportRejected, "OWNER_ADMISSION_REQUIRED"):
                dev.DevelopmentEvaluatorClient(4096, 4013, ticket(),
                    verified_by_owner=lambda size, seed, release: False)
            for size, seed in ((1024,4127),(2048,4159),(4096,0),(0,4013),(True,4013)):
                with self.assertRaisesRegex(dev.DevelopmentTransportRejected, "FIRST_USE_BLOCKED"):
                    dev.DevelopmentEvaluatorClient(size, seed, ticket(),
                        verified_by_owner=lambda *args: True)
            broken=ticket()
            broken["protocol_blob"]="wrong"
            with self.assertRaisesRegex(dev.DevelopmentTransportRejected, "FIRST_USE_BLOCKED"):
                dev.DevelopmentEvaluatorClient(1024,4013,broken,
                    verified_by_owner=lambda *args: True)
            spawn.assert_not_called()
        self.assertNotIn("PrivateTargetEvaluator", dev.__dict__)

    def test_invalid_command_never_opens_dev_world(self):
        p = subprocess.run([sys.executable,str(Path(dev.__file__).resolve()),"--development"],
            capture_output=True, text=True, check=False, timeout=15)
        self.assertNotEqual(p.returncode,0)
        self.assertEqual(p.stdout,"")
        self.assertIn("FIRST_USE_BLOCKED",p.stderr)
        self.assertNotIn("Traceback",p.stderr)

    def test_fixture_cannot_be_promoted_to_dev(self):
        with self.assertRaisesRegex(harness.ComparisonRejected,"DEV_OWNER_ADMISSION_REQUIRED"):
            harness.run_development_arm(4096,4013,"native",object(),object(),None,
                                        expected_candidate_sha="a"*40)
        seen=[]
        def factory(*args):
            seen.append(args)
            raise AssertionError("no source admission")
        with self.assertRaisesRegex(harness.ComparisonRejected,"SOURCE_SIZE_ROLE_INCOMPLETE"):
            harness.run_admitted_development_nine_worlds(
                factory,factory,{},candidate_sha="a"*40)
        self.assertEqual(seen,[])


if __name__=="__main__":
    unittest.main()

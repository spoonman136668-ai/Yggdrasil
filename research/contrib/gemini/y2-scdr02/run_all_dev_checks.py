#!/usr/bin/env python3
"""
Single-command DEV verification runner for research/contrib/gemini/y2-scdr02.
Runs all unit tests across Sinkhorn v6, Hazard v7, CCE06 Adapter, VI3 Planner v8,
and PO Planner v9/v10 (including bit-exact cold-save/cold-restore checks).
Never touches locked y2-cce06 CAL seeds [13, 29, 53, 71, 97] or PRIMARY custody.
"""

from __future__ import annotations

import json
import platform
import sys
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main() -> int:
    t0 = time.time()
    loader = unittest.TestLoader()
    suite = loader.discover(str(HERE), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    summary = {
        "schema": "yggdrasil.y2_scdr02.dev_check_receipt.v1",
        "engineering_status": "PASS" if result.wasSuccessful() else "FAIL",
        "scientific_status": "UNVERIFIED",
        "deployment_status": "UNVERIFIED",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "runtime_sec": round(time.time() - t0, 3),
        "python": platform.python_version(),
        "locked_cal_seeds_untouched": [13, 29, 53, 71, 97],
    }
    print("\n=== Y2-SCDR02 DEV CHECK RECEIPT ===")
    print(json.dumps(summary, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

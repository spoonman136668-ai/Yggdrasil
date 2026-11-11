"""WSP-33 full exact-source qualification; regression and frozen DEV are separate."""
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

def run():
    receipt = {"schema": "wsp33.full-regression.v1",
               "sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
               "tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip(),
               "python": sys.version, "platform": platform.platform(),
               "steps": [], "unique_tests": 0}
    steps = [("original", [sys.executable, "-m", "unittest", "discover",
                           "-s", "tests", "-p", "test_*.py", "-v"])]
    for n in list(range(1, 18)) + list(range(19, 34)):
        folder = "research/contrib/chatgpt/WSP-%02d" % n
        steps.append(("WSP%02d-tests" % n,
                      [sys.executable, "-m", "unittest", "discover",
                       "-s", folder, "-p", "test_*.py", "-v"]))
    steps.append(("WSP33-DEV", [sys.executable,
                                "research/contrib/chatgpt/WSP-33/run_dev.py"]))
    steps.append(("permanent-atlas", [sys.executable,
                                      "scripts/build_code_atlas.py", "--check-if-present"]))
    steps.append(("clean-source", ["git", "diff", "--exit-code"]))
    started = time.perf_counter()
    for label, command in steps:
        tick = time.perf_counter()
        run = subprocess.run(command, capture_output=True, text=True,
                             encoding="utf-8", errors="replace",
                             env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        combined = run.stdout + run.stderr
        if label == "WSP33-DEV" and run.returncode == 0:
            dev = json.loads(run.stdout)
            receipt["scientific_dev"] = dev
            combined = json.dumps(dev, sort_keys=True, indent=2) + run.stderr
        print("\nWSP33_STEP " + label + "\n" + combined, flush=True)
        found = re.search(r"Ran (\d+) tests? in", combined)
        count = int(found.group(1)) if found else 0
        receipt["unique_tests"] += count
        receipt["steps"].append({
            "name": label, "seconds": round(time.perf_counter() - tick, 6),
            "exit_code": run.returncode, "tests": count,
            "output_sha256": hashlib.sha256(combined.encode()).hexdigest()
        })
        if run.returncode:
            receipt["status"] = "FAIL"
            print("WSP33_QUALIFICATION_RECEIPT " + json.dumps(receipt, sort_keys=True), flush=True)
            raise SystemExit(run.returncode)
    receipt["total_seconds"] = round(time.perf_counter() - started, 6)
    receipt["status"] = "PASS"
    print("WSP33_QUALIFICATION_RECEIPT " + json.dumps(receipt, sort_keys=True), flush=True)

if __name__ == "__main__":
    run()

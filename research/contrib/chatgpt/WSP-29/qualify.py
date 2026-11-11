"""Full source-pinned WSP29 regression receipt, isolated subprocess modules."""
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path


def run():
    receipt = {"schema": "wsp29.full-regression.v1", "sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
               "tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip(),
               "python": sys.version, "platform": platform.platform(), "steps": [], "unique_tests": 0}
    steps = [("original", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])]
    for n in list(range(1, 18))+[19,20,21,22,23,24,25,26,27,28,29]:
        folder = f"research/contrib/chatgpt/WSP-{n:02d}"
        steps.append((f"WSP{n:02d}-tests", [sys.executable, "-m", "unittest", "discover", "-s", folder, "-p", "test_*.py", "-v"]))
    for n in (29,):
        steps.append((f"WSP{n:02d}-DEV", [sys.executable, f"research/contrib/chatgpt/WSP-{n:02d}/run_dev.py"]))
    steps.append(("permanent-atlas", [sys.executable, "scripts/build_code_atlas.py", "--check-if-present"]))
    steps.append(("clean-source", ["git", "diff", "--exit-code"]))
    start = time.perf_counter()
    for label, command in steps:
        tick = time.perf_counter()
        p = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        combined = p.stdout+p.stderr
        print(f"\nWSP29_STEP {label}\n{combined}", flush=True)
        found = re.search(r"Ran (\d+) tests? in", combined)
        count = int(found.group(1)) if found else 0
        receipt["unique_tests"] += count
        receipt["steps"].append({"name": label, "seconds": round(time.perf_counter()-tick, 6), "exit_code": p.returncode, "tests": count,
                                 "output_sha256": hashlib.sha256(combined.encode()).hexdigest()})
        if p.returncode:
            receipt["status"] = "FAIL"
            print("WSP29_QUALIFICATION_RECEIPT "+json.dumps(receipt, sort_keys=True), flush=True)
            raise SystemExit(p.returncode)
        if label == "WSP29-DEV":
            receipt["scientific_dev"] = json.loads(p.stdout)
    receipt["total_seconds"] = round(time.perf_counter()-start, 6)
    receipt["status"] = "PASS"
    print("WSP29_QUALIFICATION_RECEIPT "+json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    run()

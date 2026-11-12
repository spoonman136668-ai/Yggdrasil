"""Complete inherited qualification, frozen predecessor, and WSP40 DEV."""
import os
import subprocess
import sys
import time
import json
import platform
import re


def main():
    steps = [
        ("full-WSP01-39", [sys.executable, "research/contrib/chatgpt/WSP-39/qualify.py"]),
        ("frozen-WSP39-PRIMARY", [sys.executable, "research/contrib/chatgpt/WSP-39/battery.py", "--cohort", "PRIMARY"]),
        ("WSP40-focused", [sys.executable, "-m", "unittest", "discover", "-s", "research/contrib/chatgpt/WSP-40", "-p", "test_*.py", "-v"]),
        ("WSP40-DEV", [sys.executable, "research/contrib/chatgpt/WSP-40/battery.py", "--cohort", "DEV"]),
        ("clean-source", ["git", "diff", "--exit-code"])]
    receipt = {"schema": "wsp40.qualification.v1", "sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
               "tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip(),
               "platform": platform.platform(), "python": sys.version, "steps": [], "unique_tests": 0}
    for name, cmd in steps:
        started = time.perf_counter()
        p = subprocess.run(cmd, text=True, capture_output=True, encoding="utf-8", errors="replace", env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        out = p.stdout + p.stderr
        tests = sum(map(int, re.findall(r"Ran (\d+) tests? in", out)))
        receipt["unique_tests"] += tests
        receipt["steps"].append({"name": name, "seconds": time.perf_counter()-started, "tests": tests, "exit": p.returncode})
        print("WSP40_STEP " + name + "\n" + out, flush=True)
        if p.returncode:
            print("WSP40_QUALIFICATION_RECEIPT " + json.dumps(receipt, sort_keys=True), flush=True)
            raise SystemExit(p.returncode)
    receipt["status"] = "PASS"
    print("WSP40_QUALIFICATION_RECEIPT " + json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__": main()

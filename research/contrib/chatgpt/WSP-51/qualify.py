"""Exact-source qualification: all inherited regressions plus WSP51."""
import json
import os
import platform
import re
import subprocess
import sys
import time


def main():
    commands = [
        ("full-WSP01-50", [sys.executable, "research/contrib/chatgpt/WSP-50/qualify.py"]),
        ("frozen-WSP50-PRIMARY", [sys.executable, "research/contrib/chatgpt/WSP-50/battery.py", "--cohort", "PRIMARY"]),
        ("WSP51-focused", [sys.executable, "-m", "unittest", "discover", "-s", "research/contrib/chatgpt/WSP-51", "-p", "test_*.py", "-v"]),
        ("WSP51-DEV", [sys.executable, "research/contrib/chatgpt/WSP-51/battery.py", "--cohort", "DEV"]),
        ("clean-source", ["git", "diff", "--exit-code"]),
    ]
    receipt = dict(schema="wsp51.qualification.v1",
                   sha=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                   tree=subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip(),
                   platform=platform.platform(), python=sys.version,
                   steps=[], unique_tests=0)
    for name, command in commands:
        t = time.perf_counter()
        p = subprocess.run(command, text=True, capture_output=True, encoding="utf-8",
                           errors="replace", env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        out = p.stdout + p.stderr
        tests = sum(map(int, re.findall(r"Ran (\d+) tests? in", out)))
        receipt["steps"].append(dict(name=name, seconds=time.perf_counter() - t,
                                     exit=p.returncode, tests=tests))
        receipt["unique_tests"] += tests
        print("WSP51_STEP " + name + "\n" + out, flush=True)
        if p.returncode:
            receipt["status"] = "FAIL"
            print("WSP51_QUALIFICATION_RECEIPT " + json.dumps(receipt, sort_keys=True), flush=True)
            raise SystemExit(p.returncode)
    receipt["status"] = "PASS"
    print("WSP51_QUALIFICATION_RECEIPT " + json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

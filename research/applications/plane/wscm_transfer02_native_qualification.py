#!/usr/bin/env python3
"""Run frozen WSCM-TRANSFER-02 fixture tests against exact repository native code."""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys
from pathlib import Path

EXPERIMENT = "WSCM-TRANSFER02-NATIVE-FUNCTIONAL-CONSENSUS-QUAL-01"
PINNED = {
    "yggdrasil/native_episode_experience.py": "5a77232cdd4a0fda314e47278c9ba0ed109cfd50",
    "yggdrasil/native_external_action_identity.py": "b31538c00cda5e7b526aa1178e883e86a26be0d4",
    "research/contrib/chatgpt/WSCM-TRANSFER-02/composition_wire_dev.py": "eb141d75b0af6af3b217dd68703222df451b61ed",
    "tests/test_wscm_transfer02_composition_wire_dev.py": "a25a13c2c004a9a9001a234fcc9bb1dce0e4ff68",
    "tests/test_wscm_transfer02_functional_consensus_dev.py": "e6a852f6d55bb0f5d09e00d7b06d0fc88ce0191d",
    "tests/test_wscm_transfer02_composition_native.py": "cf22ad059d02cd82ec7ceed7f13a47ed10fb53c5",
}
SUITES = ("test_wscm_transfer02_composition_wire_dev.py",
          "test_wscm_transfer02_functional_consensus_dev.py",
          "test_wscm_transfer02_composition_native.py")

def git(root, *args):
    p = subprocess.run(["git", *args], cwd=root, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError("GIT_FAILED " + p.stderr[-1000:])
    return p.stdout.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    env0 = dict(os.environ)
    env0["PYTHONDONTWRITEBYTECODE"] = "1"
    env0["PYTHONHASHSEED"] = "0"
    env0["PYTHONPATH"] = str(root) + os.pathsep + env0.get("PYTHONPATH", "")
    head = git(root, "rev-parse", "HEAD")
    pins = {}
    for path, expected in PINNED.items():
        actual = git(root, "rev-parse", "HEAD:" + path)
        pins[path] = {"expected": expected, "actual": actual, "match": actual == expected}
    pin_pass = all(v["match"] for v in pins.values())
    suites = []
    if pin_pass:
        for pattern in SUITES:
            # Embedded Windows Python can ignore PYTHONPATH. Supply the pinned root explicitly.
            launch = "import sys, runpy; sys.path.insert(0, sys.argv.pop(1)); runpy.run_module(\"unittest\", run_name=\"__main__\")"
            cmd = [sys.executable, "-B", "-c", launch, str(root), "discover",
                   "-s", str(root / "tests"), "-p", pattern, "-q"]
            p = subprocess.run(cmd, cwd=root, env=env0, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               check=False, timeout=600)
            output = p.stdout or ""
            m = re.search(r"Ran (\d+) tests? in ", output)
            sm = re.search(r"skipped=(\d+)", output)
            count = int(m.group(1)) if m else 0
            skipped = int(sm.group(1)) if sm else 0
            passed = p.returncode == 0 and count == dict(zip(SUITES, (12, 11, 16)))[pattern] and skipped == 0
            suites.append({"pattern": pattern, "tests": count, "skipped": skipped,
                           "exit_code": p.returncode, "pass": passed})
            print("=== " + pattern + " ===")
            print(output[-12000:])
    clean = git(root, "status", "--porcelain") == ""
    tests_pass = pin_pass and len(suites) == len(SUITES) and all(s["pass"] for s in suites)
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "status": "ORIGINAL_NATIVE_FIXTURE_PASS" if tests_pass and clean else
                  ("SOURCE_BLOB_PIN_MISMATCH" if not pin_pass else "ORIGINAL_NATIVE_FIXTURE_FAIL"),
        "source_sha": head,
        "metrics": {
            "python": sys.version.split()[0],
            "source_blob_pins": pins,
            "suite_results": suites,
            "test_count_total": sum(s["tests"] for s in suites),
            "skipped_total": sum(s["skipped"] for s in suites),
            "all_focused_tests_pass": tests_pass,
            "working_tree_clean": clean,
            "source_environment_constructed": False,
            "source_reset_calls": 0,
            "source_step_calls": 0,
            "source_interventions": 0,
            "source_actions": 0,
            "protected_source_first_use": False,
            "production_model_mutations": 0
        },
        "scientific_pass": False, "scientific_gain_verified": False,
        "source_first_use": False
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n",
                   encoding="utf-8")
    print("WSCM_NATIVE_FIXTURE_TEST_STATUS=" + result["status"])
    print("WSCM_NATIVE_FIXTURE_TESTS=" + str(result["metrics"]["test_count_total"]))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

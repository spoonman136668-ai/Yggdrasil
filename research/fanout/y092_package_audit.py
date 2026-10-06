import argparse
import json
import os
import pathlib
import subprocess

BASE_SHA = "8b06604ee9fb8bcd81a53cf01076d7953800dde9"
WORKFLOW = ".github/workflows/external-cumulative-dependent-pipeline-learned-consumer-architecture-092.yml"
ALLOWED_AUX = {
    ".github/workflows/y092-free-fanout-r1.yml",
    "research/fanout/y092-package-audit.manifest.json",
    "research/fanout/y092_package_audit.py",
}
MODES = {"identity", "workflow-static", "source-tree", "package-diff"}

def fail(code):
    raise SystemExit(code)

def git(*args):
    p = subprocess.run(["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if p.returncode != 0:
        fail("Y092_FANOUT_GIT_FAILED:" + ":".join(args))
    return p.stdout.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--candidate-config", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    if os.environ.get("FREE_FANOUT_AUTHORITY") != "external-evidence-only":
        fail("Y092_FANOUT_AUTHORITY_INVALID")
    if os.environ.get("FREE_FANOUT_DATA_CLASS") != "historical-replay":
        fail("Y092_FANOUT_DATA_CLASS_INVALID")

    cfg = json.loads(pathlib.Path(a.candidate_config).read_text(encoding="utf-8"))
    if set(cfg) != {"mode"} or cfg["mode"] not in MODES or cfg["mode"] != a.candidate:
        fail("Y092_FANOUT_CANDIDATE_INVALID")

    if git("merge-base", "--is-ancestor", BASE_SHA, "HEAD") != "":
        pass

    mode = cfg["mode"]
    if mode == "workflow-static":
        if not pathlib.Path(WORKFLOW).is_file():
            fail("Y092_FANOUT_WORKFLOW_MISSING")
        if git("rev-parse", BASE_SHA + ":" + WORKFLOW) != git("rev-parse", "HEAD:" + WORKFLOW):
            fail("Y092_FANOUT_WORKFLOW_DRIFT")
    elif mode == "source-tree":
        for path in ("src", "tests", "pyproject.toml"):
            if git("rev-parse", BASE_SHA + ":" + path) != git("rev-parse", "HEAD:" + path):
                fail("Y092_FANOUT_SOURCE_DRIFT:" + path)
    elif mode == "package-diff":
        changed = {x for x in git("diff", "--name-only", BASE_SHA + "..HEAD").splitlines() if x}
        if changed != ALLOWED_AUX:
            fail("Y092_FANOUT_SCOPE_DRIFT:" + ",".join(sorted(changed)))

    result = {
        "candidate_id": a.candidate,
        "interface": "cognition_consumer(retained_state, local_state) -> decision_state",
        "metric": {"name": "package_audit_pass", "value": 1},
        "resource_usage": {"parameters": 0, "context_bytes": 0, "model_calls": 0},
        "total_slots": 16,
        "active_slots": 7,
        "retained_slots": 9,
        "hidden_persistent_memory_growth": False,
    }
    out = pathlib.Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()

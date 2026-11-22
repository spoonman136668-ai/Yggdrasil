"""Commit matching Linux and Windows evidence and preserve the earlier state."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from independent_audit import stable

HERE = Path(__file__).resolve().parent


def read_artifact(variable):
    files = list(Path(os.environ[variable]).rglob("campaign-result.json"))
    if len(files) != 1:
        raise ValueError("Expected exactly one campaign result.")
    return json.loads(files[0].read_bytes())


def write_json(name, document):
    (HERE / name).write_bytes((json.dumps(document, indent=2, sort_keys=True) + "\n").encode())


linux = read_artifact("CKAD19_LINUX_DIRECTORY")
windows = read_artifact("CKAD19_WINDOWS_DIRECTORY")
source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip()
signature = hashlib.sha256(stable(linux)).hexdigest()
assert stable(linux) == stable(windows)
assert all(d["source_candidate_sha"] == source and d["stable_sha256"] == signature for d in (linux, windows))
write_json("result.json", linux)
write_json("replication-windows.json", windows)
write_json("provenance.json", {
    "schema": "yggdrasil.ckad19.provenance.v1",
    "source_sha": source,
    "source_tree": tree,
    "prereg_sha": os.environ["CKAD19_PREREG_SHA"],
    "run_id": int(os.environ["GITHUB_RUN_ID"]),
    "stable_sha256": signature,
    "original_source_actions": 0,
    "scientific_pass": False,
    "deployment": "NONE",
})
last = linux["stages"][-1]["bounds"]
total = last["two_stage"]["native_beta"]
terminal = last["logged_history_terminal"]
report = f"""# CKAD19 composed DTR decisions

The integrated learner combines its existing transition and terminal forecasts
to compare first actions. It selects a contingent second action for each
possible next state. Both decision stages use the original Beta estimates.

The standalone conventional dynamic program reconstructs all values and actions
from the identical witnessed prefix. The three full CKAD18 snapshots restore
the same plan with their complete learned bytes preserved.

On 192 already-consumed held episodes, {total['observed_matches']} entire
logged paths match the final policy. Only those paths reveal its actual reward.
Its finite-cohort return bounds have numerators {total['return_numerator']}
over 192. The paired full-policy gate is {linux['two_stage_empirical_gain']}.
The final terminal choice matches {terminal['observed_matches']} logged actions
at factual histories. The terminal-only paired gate is
{linux['logged_history_terminal_empirical_gain']}.

The bounds allow all binary outcomes compatible with the public log.
A terminal recommendation at a factual history cannot resolve the reward or
state that would follow a different first action. The source was already
consumed. Science remains unqualified and deployment status is NONE.

The campaign took {linux['whole_wall_seconds']:.3f} seconds on Linux and
{windows['whole_wall_seconds']:.3f} seconds on Windows, including three cold
restores per run and excluding CI setup and final qualification.

Reproduce with python -B research/contrib/chatgpt/CKAD-19/campaign.py
--output-directory /tmp/ckad19. Run independent_audit.py in the same directory
to verify the sealed evidence.
"""
(HERE / "SESSION_REPORT.md").write_text(report, encoding="utf-8")

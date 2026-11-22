"""Reuse independently checked Linux model states for portability comparison."""

import json
from pathlib import Path
import platform
import sys
from time import monotonic

from causal_templates_audit import replay as audit_templates
from checkpoint_replay_parity import SCHEMA, STUDIES, archive, parents, summary
from open_set_audit import audit as audit_open_set
from shadow_preflight import checked_bytes
from staged_retention_audit import check as audit_retention
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam

HERE = Path(__file__).resolve().parent
AUDITORS = (audit_retention, audit_templates, audit_open_set)


def verify(checkpoints, candidate):
    if platform.system() != "Linux":
        raise ValueError("The sealed scientific receipts were produced on Linux")
    start = monotonic()
    spec, material = parents(checkpoints)
    raw = checked_bytes(checkpoints / spec["joint_name"], spec["joint_sha256"])
    anchor = NativeCausalAmalgam.restore(raw, spec["joint_sha256"], **material)
    models = {"anchor": summary(anchor, raw, None)}
    manifest = {name: (trace_sha, expected_sha)
                for name, (trace_sha, expected_sha), _ in archive()}
    reports = {}
    for (study, protocol), audit in zip(STUDIES, AUDITORS, strict=True):
        def capture(seed, restored, trace_sha):
            key = f"{study}/{seed}"
            result = summary(restored, restored.checkpoint(), trace_sha)
            if (key in models or manifest.get(key) !=
                    (result["trace_sha256"], result["joint_sha256"])):
                raise ValueError(f"Unexpected or invalid verified model: {key}")
            models[key] = result
        reports[study] = audit(checkpoints, HERE / protocol, HERE / study, capture=capture)
    if set(models) - {"anchor"} != set(manifest):
        raise ValueError("Exact replay capture did not cover the sealed roster")
    return {"schema": SCHEMA, "candidate": candidate, "platform": "Linux",
            "models": models, "source_actions": 0, "wall_seconds": monotonic()-start}, reports


if __name__ == "__main__":
    directory, sha, output = sys.argv[1:]
    replay, reports = verify(Path(directory), sha)
    Path(output).write_text(json.dumps(replay, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(reports, indent=2, sort_keys=True))

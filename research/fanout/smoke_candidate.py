#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

TOTAL_SLOTS = 16
ACTIVE_SLOTS = 7
RETAINED_SLOTS = 9
INTERFACE = "cognition_consumer(retained_state, local_state) -> decision_state"

def cognition_consumer(retained_state, local_state, candidate_id):
    salt = int(hashlib.sha256(candidate_id.encode("utf-8")).hexdigest()[:8], 16)
    combined = [int(v) for v in retained_state] + [int(v) for v in local_state]
    if len(combined) != TOTAL_SLOTS:
        raise SystemExit("SMOKE_CONTRACT_SLOT_COUNT_MISMATCH")
    return [int((combined[(i + salt) % TOTAL_SLOTS] + combined[(i * 3 + 1) % TOTAL_SLOTS] + i) % 257) for i in range(ACTIVE_SLOTS)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    fixture = json.loads(Path(__file__).with_name("smoke_fixture.json").read_text(encoding="utf-8"))
    retained = fixture["retained_state"]
    local = fixture["local_state"]
    if len(retained) != RETAINED_SLOTS or len(local) != ACTIVE_SLOTS:
        raise SystemExit("SMOKE_CONTRACT_PARTITION_MISMATCH")
    decision = cognition_consumer(retained, local, a.candidate)
    result = {
        "candidate_id": a.candidate,
        "interface": INTERFACE,
        "total_slots": TOTAL_SLOTS,
        "active_slots": ACTIVE_SLOTS,
        "retained_slots": RETAINED_SLOTS,
        "hidden_persistent_memory_growth": False,
        "fixture_class": "synthetic-replay",
        "metric": {
            "name": "synthetic_decision_checksum",
            "value": round(sum(decision) / (ACTIVE_SLOTS * 256.0), 12),
        },
        "resource_usage": {
            "parameters": 0,
            "context_bytes": len(json.dumps(fixture, sort_keys=True).encode("utf-8")),
            "model_calls": 0,
        },
        "decision_sha256": hashlib.sha256(json.dumps(decision, separators=(",", ":")).encode("utf-8")).hexdigest(),
    }
    Path(a.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()

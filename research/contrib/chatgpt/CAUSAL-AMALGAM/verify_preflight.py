"""Compare platform replay receipts to the development preflight invariants."""
import json
from pathlib import Path
import sys


def semantic(path):
    data = json.loads(path.read_bytes())
    data.pop("wall_seconds", None)
    data.pop("child_cost", None)
    # Each platform verifies its own original bytes. Libm-trained weights can
    # differ within the independently checked numeric source tolerance.
    data.pop("joint_checkpoint_sha256", None)
    return data


for expected_name, replica in zip(("shadow-result.json", "growth-result.json", "joint-result.json"), sys.argv[1:], strict=True):
    expected = Path(__file__).with_name(expected_name)
    actual = Path(replica)
    if semantic(expected) != semantic(actual):
        raise RuntimeError(f"AMALGAM_PREFLIGHT_REPRODUCTION_MISMATCH: {expected_name}")
    print(actual.read_text(encoding="ascii"))
print("AMALGAM_PREFLIGHT_REPRODUCTION_PASS")

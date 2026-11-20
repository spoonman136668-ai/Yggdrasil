"""Bounded offline tampering tests for NCI-SOURCE-07 archival custody."""
import json
from pathlib import Path
import tempfile
from audit_archived_joint import run

HERE = Path(__file__).parent
MANIFEST = HERE / "manifest.json"

def must_fail(f, label):
    try:
        f()
    except ValueError:
        return
    raise AssertionError(label + " was not rejected")

def test(linux, windows):
    baseline = run(linux, windows, MANIFEST)
    assert baseline["verified_episodes"] == 1025
    assert baseline["sources"][0]["projection1_view_conflicts"] == 497
    assert baseline["sources"][1]["projection0_view_conflicts"] == 0
    assert baseline["sources"][0]["joint_sha256"] != baseline["sources"][1]["joint_sha256"]
    assert baseline["sources"][0]["native_sha256"] == baseline["sources"][1]["native_sha256"]
    with tempfile.TemporaryDirectory() as d:
        dest = Path(d)
        altered = dest / "tampered.zip"
        source = bytearray(linux.read_bytes())
        source[-64] ^= 1
        altered.write_bytes(source)
        must_fail(lambda:run(altered, windows, MANIFEST), "outer ZIP altered")
        wrong = dest / "bad_manifest.json"
        for field in ("one_original_public_packet_sha256", "native_sha256"):
            doc = json.loads(MANIFEST.read_text())
            doc[field] = "0" * 64
            wrong.write_text(json.dumps(doc))
            must_fail(lambda:run(linux, windows, wrong), "wrong " + field)
        doc = json.loads(MANIFEST.read_text())
        doc["episode_count"] += 1
        wrong.write_text(json.dumps(doc))
        must_fail(lambda:run(linux, windows, wrong), "changed count")
    print("NCI07_OFFLINE_NEGATIVE_CONTROLS_PASS")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--linux",type=Path,required=True)
    p.add_argument("--windows",type=Path,required=True)
    a = p.parse_args()
    test(a.linux,a.windows)

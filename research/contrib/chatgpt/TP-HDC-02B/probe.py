"""TP-HDC-02B frozen custody repair; disjoint source-free trial (DEV ONLY)."""
from __future__ import annotations
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path

PREREG_COMMIT = "1c5dc38f2ca7c7b6e9ccda2b6d08a63208691ae0"
ORIGINAL_SHA256 = "db5f66e633193ccb2a6a593347c57fa91bbbf43b307764230158975c2d93b082"
NEW_SEEDS = (515, 626, 737, 848)
SOURCE = Path(__file__).resolve().parent.parent / "TP-HDC-02" / "probe.py"


def corrected_hashed(tag: str, *parts: object) -> bytes:
    return hashlib.sha256((tag + "|" + "/".join(map(str, parts))).encode("ascii")).digest()


def main() -> None:
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("TPHDC02B_ORIGINAL_SOURCE_IDENTITY_MISMATCH")
    spec = importlib.util.spec_from_file_location("tp_hdc_02_frozen", SOURCE)
    if spec is None or spec.loader is None:
        raise ValueError("TPHDC02B_IMPORT_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.hashed = corrected_hashed
    module.SEEDS = NEW_SEEDS
    module.PREREG_COMMIT = PREREG_COMMIT
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        module.main()
    result = json.loads(output.getvalue())
    result.update({
        "schema": "yggdrasil.tp-hdc02b.sourcefree-result.v1",
        "experiment_id": "TP-HDC-02B",
        "original_source_sha256": ORIGINAL_SHA256,
        "hash_domain_repair": "tag + '|' + slash-joined decimal components",
        "prior_trial": "TP-HDC-02 INVALID; no reused seeds or scored outcomes",
        "independent_science_qualified": False,
    })
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

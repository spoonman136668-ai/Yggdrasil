"""WSP215 strict cross-OS verifier built on unchanged WSP214 source."""
import importlib.util
import json
from pathlib import Path
import sys
from experiment import _git_blob_sha, SCHEMA, PREREG, WORLDS

SRC = Path(__file__).resolve().parent.parent / "WSP-214" / "verify_parity.py"
EXPECTED_BLOB = "1137ef2704354e0eaf8db5c97a971f16fc927143"
if _git_blob_sha(SRC) != EXPECTED_BLOB:
    raise RuntimeError("source-exact verifier changed")
_spec=importlib.util.spec_from_file_location("wsp215_source_exact_parity",SRC)
if _spec is None or _spec.loader is None:
    raise RuntimeError("missing source-exact WSP215 cross-platform verifier")
_v=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v)
_v.SCHEMA=SCHEMA
_v.PREREG=PREREG
_v.WORLDS=WORLDS
metric=_v.metric


def compare_receipts(linux,windows):
    return _v.compare_receipts(linux,windows)


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: verify_parity.py linux.json windows.json")
    a=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    b=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    print("WSP215_CROSS_OS_PARITY=PASS CLASSIFICATION="+compare_receipts(a,b))

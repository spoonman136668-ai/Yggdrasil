#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2g_second_task_compositional_service_transfer_v1 as g

EXPECTED_BYTES=473730
EXPECTED_SHA256="cf33e4bbced5c02f577ed195acd8af4f197742897a1e2f9eab4b926aba2fa09f"

p1=Path(sys.argv[1]).read_bytes()
p2=Path(sys.argv[2]).read_bytes()
if p1!=p2:
    raise SystemExit("accepted LU2G duplicate artifact mismatch")
if len(p1)!=EXPECTED_BYTES:
    raise SystemExit(f"accepted sweep byte-count mismatch: {len(p1)}")
sha=hashlib.sha256(p1).hexdigest()
if sha!=EXPECTED_SHA256:
    raise SystemExit(f"accepted sweep SHA mismatch: {sha}")
sweep=json.loads(p1.decode("utf-8"))
out={
  "duplicate":{"byte_identical":True,"bytes":len(p1),"sha256":sha},
  "qualification":g.g.qualification(sweep)
}
Path(sys.argv[3]).write_bytes(json.dumps(out,sort_keys=True,separators=(",",":")).encode())

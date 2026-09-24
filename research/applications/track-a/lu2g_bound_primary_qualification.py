#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path

import lu2g_second_task_compositional_service_transfer_v1 as g

LU2GF1="e9a01aa97587fc97dde073cb2a6a35ad141006cd"
BOUND_BUNDLE_SHA256="1c711199238d3a223c75262ca490a1dfb4e4eab34cceb64992e8f378b4ecfe78"
BOUND_SWEEP_SHA256="cf33e4bbced5c02f577ed195acd8af4f197742897a1e2f9eab4b926aba2fa09f"
BOUND_SWEEP_BYTES=473730

manifests=g.g.primary_manifests(LU2GF1)
bundle=json.dumps(manifests,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(bundle).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("bound LU2G manifest bundle mismatch")

sweep=g.g.run_sweep(manifests)
raw=json.dumps(sweep,sort_keys=True,separators=(",",":")).encode()
if len(raw)!=BOUND_SWEEP_BYTES:
    raise SystemExit(f"bound sweep byte-count mismatch: {len(raw)}")
if hashlib.sha256(raw).hexdigest()!=BOUND_SWEEP_SHA256:
    raise SystemExit("bound sweep SHA mismatch")

out={
    "lu2gf1":LU2GF1,
    "bound_manifest_bundle_sha256":BOUND_BUNDLE_SHA256,
    "bound_sweep_bytes":len(raw),
    "bound_sweep_sha256":hashlib.sha256(raw).hexdigest(),
    "qualification":g.g.qualification(sweep),
}
Path(sys.argv[1]).write_bytes(json.dumps(out,sort_keys=True,separators=(",",":")).encode())

#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2i_task2_load_response_calibration_v1 as x

LU2IF1="326f89f940818a6abb0fcbc999595b844936dc53"
BOUND_SHA="3598c372a046530caaf8956b58e0b2654c212fed00149cf9f350d0035344995f"

manifests=x.calibration_manifests(LU2IF1)
raw=json.dumps(manifests,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_SHA:
    raise SystemExit("LU2I bound manifest bundle mismatch")
for m in manifests:
    x.validate_manifest(m)
result=x.run_calibration(manifests)
Path(sys.argv[1]).write_bytes(json.dumps(result,sort_keys=True,separators=(",",":")).encode())

#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2m_doubled_distributed_lesion_robustness_v1 as x

LU2MF1="e05168e6452f81cad45474ed0984fe4970762456"
BOUND_BUNDLE_SHA256="051828c43997c19863879990f9d56d5a7d81a65ec17949a07f50bd4dd4544fa0"
BOUND_MANIFEST_SHA256=[
  "dbe5806ba76559b088653394adf38ab87a3591695d6352aecbe7661741ef6c64",
  "76f3b6b992919f8c73f8722eecd8f70e6015badee095ccca7101abfcc14d6b8e",
  "606687546b448c6ea2fa36604910a79595e3da5b65484ac841d1e88c76253f4d",
  "1b00292241814090d38f607f0889cd7a6ea44bf97ece7e3d4b7abf5c094e515f",
  "417e7c45eb69d15388425adbd1c7db643796b017dbc05a92f9579c6a20537cbe",
  "d2cf856db9ad118bbfcbcd6676974f563ffa760e35b50366ceaaa8e400d82336",
  "47bb4c119c25306c1d3c1169cc7badaec9df086512fcbee9c02f952a739f60a5",
  "6ccd7f4130640bcbe9e5407fcd9cc1f7a4eebf6e14040aa82e1d70a6febc1d13",
  "e69b1a40596edf49b6bbfcf5b2a9cd978d36926b622bf236bf7c45d430ebc40e",
  "365955ba9cd309a4b12ebf4e8201da9d6d8377ee837113b7659457af59223898"
]

ms=x.primary_manifests(LU2MF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("LU2M bound manifest bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256:
    raise SystemExit("LU2M bound manifest identity mismatch")
for m in ms:
    x.validate_manifest(m)
sweep=x.run_sweep(ms)
Path(sys.argv[1]).write_bytes(json.dumps(sweep,sort_keys=True,separators=(",",":")).encode())

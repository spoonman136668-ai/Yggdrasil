#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2k_fresh_l1_exact_parent_validation_v1 as x

LU2KF1="441d90e9c39e0ed9444953937d90d585084b4c7b"
BOUND_BUNDLE_SHA256="01d4cf6349ea7fdcff2fb77f8d13a9f497b1d161b26a7d7f07ef8fa760360a33"
BOUND_MANIFEST_SHA256=[
"a678dde7080aec0a08631cfd01de9a9db6a4aac4381e18b4bac105f237b88344",
"0da02983cb2348028022e4cffabfd2199dd0e6b8168d05ec29179d40708019a1",
"66db1367335db6b2edd1b4ed0e21457365f02b46591cf2fe0e885bf94f5f718e",
"abf8c1e4b7d09b2d5c05e77f18ff08e48bc23809cc36e24f820c88a47d076ebc",
"abd917fb919e264c153596b281803fe33411cfcfb8ebc7963f572857461c9bfd",
"c3b6f2182c57e5f5727ea1586b8195a015928cceb5fc901f0513f9475a259de9",
"f05c64562ab0bbf668b8f2b283d173be037c7e3e03a9786f8d66fced0854de59",
"cdb78a6b08d3221cd8209f2ba9f52eec052f0b587be59fd9ee0fbd0f93115809",
"56d0e69c4d6145bdadacc8dd3d2ead668a4e0886cd9b84ed15c0592737a66bb6",
"6505be7f299d7979eb8dccb4c2a3558b187a4788909fe56e648bbc6bbf424b33",
]

ms=x.manifests(LU2KF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("LU2K bound manifest bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256:
    raise SystemExit("LU2K bound manifest identity mismatch")
for m in ms:
    x.validate_manifest(m)

result=x.run_validation(ms)
Path(sys.argv[1]).write_bytes(json.dumps(result,sort_keys=True,separators=(",",":")).encode())

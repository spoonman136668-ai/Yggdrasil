#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import lu2q_task3_exact_parent_feasibility_v1 as x

LU2QF1="c2907a97aeff03f6fb7bebacf448fc9027859e19"
BOUND_BUNDLE_SHA256="a7e202de864c885c5f50d0a5cff7f449040d0d0ffd7bc9a73c665f57d2cf917a"
BOUND_MANIFEST_SHA256=[
"82e65f1191039bac382e4a34a59fcad768eb6e47fddc4e5b51ceee70b44231db",
"1d23081b8b13696db9f0ecb4e73de5076a00ab44bd2c407640f6b76188305a59",
"71a77f1b31317179bace20644f3e37dde706591462609f4a275692029784f538",
"c9b9bef87ff47dd08c9f37503ee3cbb3c924d32e08cb52e61c0fa1e30868f5d3",
"1ed1d9fcdec21d64169861005a4b7f155e8780d79257f49a83ce7bd178e24846",
"732c7e40a47ee3d79f55e4eadd1d643ee4be59bf2a3f9a9005bbd8ba638f1f07",
"f5fe24dea01091326873d6750a21c03692068db746e8ba9740af2ad195f893d6",
"0134ac2543ea77a2216c2b4407daf70e6b46a0b0c90774fc67cafa3c9dcbf993",
"6fef6c4143825e7b5112d7e11ef75a29e2c05834f02de3baee6837cbdf6c126f",
"09afb14f8f542a05dfea602c0a13d4bef6b87ff5f972c8b4e0bc52ba593346ab"
]
ms=x.primary_manifests(LU2QF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256: raise SystemExit("LU2Q bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256: raise SystemExit("LU2Q manifest mismatch")
for m in ms: x.validate_manifest(m)
Path(sys.argv[1]).write_bytes(json.dumps(x.run_sweep(ms),sort_keys=True,separators=(",",":")).encode())

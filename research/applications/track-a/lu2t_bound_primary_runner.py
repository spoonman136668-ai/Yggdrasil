#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2t_task4_exact_parent_feasibility_v1 as x

LU2TF1="dcdac04ed1fed5ce1fdfc294f133125b6d26cb0e"
BOUND_BUNDLE_SHA256="94fd7a56abbe3ba0db3398733327f12c2b5677ca31df569f22dc2a8eb2304328"
BOUND_MANIFEST_SHA256=[
"39b577f48da1df298bc9ba34571971f29af7afdd403016f732f8ade87ade5f54",
"9920bcd0d9c1bd432a5191abb130791c8fe939ab61ecaf73388cc8fe1c80e58f",
"83321647abd5739d693f2540d62920e3d983de174f38ad945bf5494a24348d68",
"ba8a92230d804b55cd90d7015bd61099e7320cb829eaf033a82b3ac29a40aeab",
"ff0460d68d37f5d929c914eddb507a38d76f61bd84bda7701a71c498f9fce130",
"af45f46d9309bd8fe67de5b7402dc96e7074a1b57ef0b8a3160aa83c8ab92c28",
"adc30f2457b6c8ba81efbd44d20fe76cf06b821b5666451ef5d004e3c5896b4b",
"901f9a279414315702fa1e35822dec7992710c11e0442889b5d4b0303d11ebc0",
"8e0b23f477c0dfc31a0d44409a13e80adaf27338dc7b03be1d272820eaaf59b3",
"3a939f23ff3fea83433da1c72aaf9a767204c765bf5e9e5349cbecd9904e184c"
]

ms=x.primary_manifests(LU2TF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("LU2T bound manifest bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256:
    raise SystemExit("LU2T bound manifest identity mismatch")
for m in ms:
    x.validate_manifest(m)
sweep=x.run_sweep(ms)
Path(sys.argv[1]).write_bytes(json.dumps(sweep,sort_keys=True,separators=(",",":")).encode())

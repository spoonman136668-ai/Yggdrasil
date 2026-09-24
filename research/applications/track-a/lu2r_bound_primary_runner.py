#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2r_task3_learned_u_transfer_v1 as x

LU2RF1="1cfce19f866b6d33ccfb7b6bcd9ae8d10207f5d3"
BOUND_BUNDLE_SHA256="a571db4d3e1346b8d834e7d9e0ea14d5bec612d1fd97dc81536971975ef16ab8"
BOUND_MANIFEST_SHA256=[
"b79165db6b6857328f6f6ea1ef37e3edd39f5fa44877246f7a9d59da73e4f498",
"0878e91cb6a007424a4e9979676b0cf030f2869ea91d3525852e337401cb9ec2",
"205caaf3a544e869c05c6aa9abf420ebe316a8b97aaa784ad94f7eea24f7805e",
"200208f33de5a823bef120ac17064b687453de9e14eb86fae0ecef758f7b7e0d",
"79968e8115bf9afe79602dcfeed53a59ae69c8d92de242b097cbe4bd59515a0a",
"ce07092e36bf83787e3f3846df0ff03e8c361dcc6209147eb70f8968cc7ae2e4",
"eae3714725dd6946ecc40b11a462b645f4387252afe507483e99484bbdbdf35e",
"583816e2fc1c2fe4e04c0bc65414409b72e9e70c1d3ba330d5e1faba18eb81e4",
"6b051b82068c41c84219c2eab125156dc23a647b9f568f482d841786a4397437",
"6417794054ac2b2f4cd54c7d1261a3e617ef5e6da45c5f839519a96e53470bb9"
]

ms=x.primary_manifests(LU2RF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("LU2R bound manifest bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256:
    raise SystemExit("LU2R bound manifest identity mismatch")
for m in ms:
    x.validate_manifest(m)

sweep=x.run_sweep(ms)
Path(sys.argv[1]).write_bytes(json.dumps(sweep,sort_keys=True,separators=(",",":")).encode())

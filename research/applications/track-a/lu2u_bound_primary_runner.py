#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2u_task4_learned_u_transfer_v1 as x

LU2UF1="ad60a966768e15cb3b9f5eb56b889d52b40c21ae"
BOUND_BUNDLE_SHA256="c811e71941b22b92b1be600f48358d0200bd8307e0a58c96ae14609cdcf8bdd3"
BOUND_MANIFEST_SHA256=[
"074c2b5fd1eeae7ade9864c5359b5fb92db11740f4f2ac359da508ad2563c029",
"294e101c38eb82b6797b9d6b4f0a445c25238ea9a7969effe4e588bf8675f7bb",
"284dab22f1f253afcaeee06b35140628818d5590826859b4b829390fb0d0acf7",
"0a25e7532b44a2d1ddfd7ab1e99d4582964583e4d7d96c052882d4de4d4f88b1",
"533054c55d6eb9d6808ad9dc633665554deefcb1b9978cdc397e036903710aac",
"a70537b53d3e9ac051dbcd82f6c4049d8bb22cc467dd21f8f5b4b53a44324079",
"d2f5ab0012f2615c0f99b3fc92253e559f87b2a336ec7a413a7ee3c3776b3557",
"c727f4bb0037fd0f8a70ff26eabd9d1b8f6f17a9f082f090a0fa3b5eb067022f",
"f2e2cd9970f93d4201079a074bc836cdc3dd2f2ad3f523e11f70697562eac979",
"3c02fb1097196cb1f7f495e5382fa56f0c0265d22063ce289384d074fcb1c86b"
]

ms=x.primary_manifests(LU2UF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("LU2U bound manifest bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256:
    raise SystemExit("LU2U bound manifest identity mismatch")
for m in ms:
    x.validate_manifest(m)
sweep=x.run_sweep(ms)
Path(sys.argv[1]).write_bytes(json.dumps(sweep,sort_keys=True,separators=(",",":")).encode())

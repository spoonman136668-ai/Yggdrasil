#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2s_task3_independent_confirmation_v1 as x

LU2SF1="f2d08b96ac502a6e61013132b3d7a8b7ff241f2e"
BOUND_BUNDLE_SHA256="d1a07b887b3d4422045609647c67ffe0ae6d5aa49b9eba9ba0f1be575741ac58"
BOUND_MANIFEST_SHA256=[
"f669af144761f0cd044dcc6e2293467653e5fdaadca471109a159bf179b4f4c0",
"0091e198588d5bcb6a8e420069145ad0ba80a407a1b2f76d6b589dd8913ee41d",
"81d4e09faa36b303ef3bf5dbae1a99256a0c0c90551b75c04636a82eb40d10e5",
"fb0de2b98e3aa1d13dd88734d04dfa69cc094d2c85e154be61d550a9f086f72c",
"e3a2bf954fcf5d70fc36212a2762a24ae828cd34d2ffc6f4b714a6828ff9669e",
"b131cd00b38932d90a816ac9074ca4320dd1b5fac60dec39c4f5c81a35f6437f",
"3de962082d8e501d9e9868e3c1eaeff70069dce1286b7781156fc9b40ea05096",
"9907a124fa82dc308aead7abd53bbf59899f3aad24169f8f54fa838102e1ac21",
"7257e9a6b858cdb1088e6fc5153b8208c48665da28a42eb9085ffe9cd5b63a32",
"4832901c240d9aa946006ee3ae2c2c329b18f245576e17034ce28cc673080d48"
]

ms=x.primary_manifests(LU2SF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("LU2S bound manifest bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256:
    raise SystemExit("LU2S bound manifest identity mismatch")
for m in ms:
    x.validate_manifest(m)
sweep=x.run_sweep(ms)
Path(sys.argv[1]).write_bytes(json.dumps(sweep,sort_keys=True,separators=(",",":")).encode())

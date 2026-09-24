#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2v_task4_independent_confirmation_v1 as x

LU2VF1="e832853554e813db2e185d6b607543541f32d887"
BOUND_BUNDLE_SHA256="de68bd564a594c2f6d9f18b4355586ff2e9058c376ccd4a36760a56b0a54e10e"
BOUND_MANIFEST_SHA256=[
"86f2a963c87894ef8d676538d96ed497b79fabe1cc77e5ebe43edfd75f2bf876",
"b12e1cb54179dc0fb5d53d0bc3da0c768f4d726ab3bc727fa14ae2834fbaaa23",
"bf246bfee67651f9f47fa7fc9696e10eb959036635c2923f06ac154ca83493ce",
"4ec87c1ad2398de8692c3a94c08812d8639d410998d1db76e2d156cf4c9e3447",
"39f20b5b6c7c69e74feec181add54e1f85d279093e304522a24b61cfcec9b1f1",
"7991bfa97e2d8170389e19d55f6f9a56e97f88d22138ba538ef6b731fda00a16",
"6aff4c772d04046303df55f2d04f1232a58ce95bc5fc8b5d48c6c2a289939504",
"5934abd39719bf17c8b23b0803fbed1052d6f7ed0fa03b6df6c4e236ddc3ee9b",
"c1e9a84ae5a4417e7ab98dfe4daee95b7c80dd1ce6c19910d4886148ed2258f1",
"6638430b87ecf2aa0277102a166e7ce93d1894f22251e79a7b20de8612156f4b"
]

ms=x.primary_manifests(LU2VF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("LU2V bound manifest bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256:
    raise SystemExit("LU2V bound manifest identity mismatch")
for m in ms:
    x.validate_manifest(m)
sweep=x.run_sweep(ms)
Path(sys.argv[1]).write_bytes(json.dumps(sweep,sort_keys=True,separators=(",",":")).encode())

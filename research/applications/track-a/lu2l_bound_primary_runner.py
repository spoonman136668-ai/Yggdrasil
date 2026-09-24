#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2l_l1_learned_u_transfer_v1 as x

LU2LF1="799058733a864c1d8437569cf4e8cdc6502fa6c3"
BOUND_BUNDLE_SHA256="22828e7d2c31ce0bda49f19a748132a088196a3746a7e7d99e35f488ff446a11"
BOUND_MANIFEST_SHA256=[
"38a2152b6c09cc2f3863777be2c69acfa33e6b180a1696f3075d6910f980fae7",
"9cb12e5f4ac5ee0db471546ada16760c2c7cf25980cb11d743cdcac90aa9f57b",
"03f2d328af9cebfed67048ce26a0063ea16dc197d6e72f83ec0b45db0141db24",
"27b018797eb1ff0f7c6755285e640d74d158e39b3a3322bfcff079627c9ae9a9",
"adbbaf365e6bcf1d848811568d3c6b187a91c05a74f4e2eb43084fb4b0953c42",
"a09eddb17680a5ee25c923f86a59a4ba0f327ceb547d7671c511158fde49effd",
"8e23199f618629b81e984d40d49db689cd7b10aa26fe567a206d6bd044767d97",
"88f2d199c581e84badb1fd2f952ac4b599d6575c8aec6c6d3b7b13d2f0af7a7c",
"272374f0d245bc3c0937e5b5382d7ae265ce3174b844062e482ceb76023801e9",
"004ae05e9af99715d7005dc0039caa0b22ea5f8ae39bf1e195142b9339e1f8ad",
]

ms=x.primary_manifests(LU2LF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("LU2L bound manifest bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256:
    raise SystemExit("LU2L bound manifest identity mismatch")
for m in ms:
    x.validate_manifest(m)

sweep=x.run_sweep(ms)
Path(sys.argv[1]).write_bytes(json.dumps(sweep,sort_keys=True,separators=(",",":")).encode())

#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import lu2p_contiguous_lesion_mature_repair_v1 as x

LU2PF1="6cf5ac96c4357fa3d065f2076ee64fe401e542e9"
BOUND_BUNDLE_SHA256="1f1fa0f77cb18a499eb037030075502f112af639021826d590fe040dba6b97d5"
BOUND_MANIFEST_SHA256=[
"56ce1567aee8b0fb9fad7200e9b14dbc3ec7554dc615aa4e4ce390ad2e355dcf",
"a2ca65ce8a4778fd0bf0032e458a0e1a4d07283344c5d29ff139c88bc40ca2c3",
"9d48e1b36c355093190a4a331ea10bf5f1bc5cec9a11477e7ea3a10502523044",
"4201619ec5e83ec9eea0753f3cc08a3885c8883d68c675ad8b8d9c7f82fcf5f0",
"3fbaecabf12200b24ec9c15537374b76bcb463dcb4068a88baa01635f60c41d6",
"819891c386c415e445b7f5abceafa20b0e245bfa99b969ef43e1b024c179087c",
"e53d464af33e89a7fa4b30e1fbe0744ab2ec380f12cdbd2e7730e075b49901b1",
"5dfd284a94b77fad4a2612aa8dfbbfcad0f59d4170bc41c7957292e4e9c28c53",
"cccb3019d6b37738fe9ae5ab081e493bc95e0381c5377c7707f9ccdcafe4cab3",
"d21456fb26de2ba9388a559b1f46614e9b1efc29c61072c486527f4e4ef4cd19"
]
ms=x.primary_manifests(LU2PF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256: raise SystemExit("LU2P bound bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256: raise SystemExit("LU2P manifest identity mismatch")
for m in ms: x.validate_manifest(m)
sweep=x.run_sweep(ms)
Path(sys.argv[1]).write_bytes(json.dumps(sweep,sort_keys=True,separators=(",",":")).encode())

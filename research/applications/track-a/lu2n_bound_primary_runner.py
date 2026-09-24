#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import lu2n_contiguous_16cell_lesion_robustness_v1 as x

LU2NF1="a4657c94a654d2b4f83b6af0c7844b65e6999593"
BOUND_BUNDLE_SHA256="a14a1f4dad871d196628f7e62218aad115ada1eb8e9fc98bfb8ca28081809f24"
BOUND_MANIFEST_SHA256=[
"f6ba25119e06212c096f8d2bcd8ba9a9bb50d3d31d9d5431fe95e38837b7632e",
"4ef388baed20466e8d87ba1941cd67524e3bf40b2169b6cf7177711d9f8930bc",
"e771f5c7b0406645246aa7a23b05cdb6e9fbcc149b3cfcf1c5553eddce13b6b6",
"8b5b737385df199055cd5ff9ebd13a8df4472917451c03915114f0cd9ac1ef06",
"4643c3371201a38f096566c2d4cee3a4aa3736c384ab4708a57cc6b4ede36cf5",
"a906e490770542fe36c1d77ff7a91aa62509252c3ba9f13087d44fc7888bec8e",
"547d666074df254bf567eedb27dab65967c6f689ee2354946cfd484c070151b1",
"1f540211c6ab447deb40e7233291743ecfcc6e5b94d6eee5de149f7e0a050a97",
"18a418649e8d040a2d737122cdf50355287d5aee399800c4d6fccb6cc1196fba",
"ced52c52d1268bc15a29dd05713cb90fb4a39d527f6c22fd852f7f4349da43e1"
]

ms=x.primary_manifests(LU2NF1)
raw=json.dumps(ms,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(raw).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("LU2N bound manifest bundle mismatch")
if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256:
    raise SystemExit("LU2N bound manifest identity mismatch")
for m in ms:
    x.validate_manifest(m)
sweep=x.run_sweep(ms)
Path(sys.argv[1]).write_bytes(json.dumps(sweep,sort_keys=True,separators=(",",":")).encode())

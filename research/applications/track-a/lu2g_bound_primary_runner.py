#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path

import lu2g_second_task_compositional_service_transfer_v1 as g

LU2GF1="e9a01aa97587fc97dde073cb2a6a35ad141006cd"
BOUND_BUNDLE_SHA256="1c711199238d3a223c75262ca490a1dfb4e4eab34cceb64992e8f378b4ecfe78"
BOUND_MANIFEST_SHA256=[
"0978a2c3d93b929ff9f28a8b766db299356a06aaa5030794990d621a0aaef173",
"b315103925063b00e0c9210889d9019b1fe9dcd6282d4af4ea207fb7d662e41b",
"1c264068629d12b6b9f412200c9e742ac09fcf41f0751d145064f2dddc771e02",
"dba433d10626dd728baadd56c4f7a8bdeee1cc163920913f64573e0368573e61",
"492d049f1026dcd9b380c47f17b8e9c745dad419e4806c8fb798db90f146ed4d",
"61199e877a3a7f20c2fac42d30dfe02ed1b92e905c5d18dd9d8086d4976682ae",
"ef3b3234c13a0363802677920c2e7ba0b50aaf100bec0b9986fc8212ff5623d5",
"ba5e85d178a596db63d545e9f2ee36c51a0bae298e7ab069357cfa8f109d6ac4",
"c06fd3d6b3a0432cf9ce13d0ecdfcf69a960123c8ee7f31404fc95c09d606e0b",
"1ff0dcc478356148e898ee8d51a5e4628b5d5e154d5748ba91dbf13051ec872b",
]

manifests=g.g.primary_manifests(LU2GF1)
bundle=json.dumps(manifests,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(bundle).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("bound LU2G manifest bundle mismatch")
if [m["manifest_sha256"] for m in manifests]!=BOUND_MANIFEST_SHA256:
    raise SystemExit("bound LU2G manifest identity mismatch")
for m in manifests:
    g.g.validate_manifest(m)

sweep=g.g.run_sweep(manifests)
Path(sys.argv[1]).write_bytes(json.dumps(sweep,sort_keys=True,separators=(",",":")).encode())

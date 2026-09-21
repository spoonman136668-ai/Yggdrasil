#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz')
EXPECTED_SOURCE_SHA256='a1ef99dc5948328d5b8a85d87b7e62a718b4238474322c16aeec6a730244d5c5'
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f'A17 harness source hash mismatch: {actual}')
exec(compile(source,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

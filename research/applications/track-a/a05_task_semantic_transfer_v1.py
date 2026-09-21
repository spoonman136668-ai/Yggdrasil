#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path

PAYLOAD=Path(__file__).with_suffix(".py.gz")
EXPECTED_SOURCE_SHA256="9efc8e31c08b60b6decff06c7ffc5b5a1ad10df7bb4440d4b2ab4d1fb5876fce"
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f"A05 harness source hash mismatch: {actual}")
exec(compile(source,str(PAYLOAD.with_suffix("")),"exec"),globals(),globals())

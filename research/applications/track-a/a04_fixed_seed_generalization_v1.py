#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path

PAYLOAD=Path(__file__).with_suffix(".py.gz")
EXPECTED_SOURCE_SHA256="d40fd3ac9b9b792df62e5e40b1b83627a24eac3ee906d8a1519ae74c8cf07122"
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f"A04 harness source hash mismatch: {actual}")
exec(compile(source,str(PAYLOAD.with_suffix("")),"exec"),globals(),globals())

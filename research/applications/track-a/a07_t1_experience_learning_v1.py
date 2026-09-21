#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path

PAYLOAD=Path(__file__).with_suffix(".py.gz")
EXPECTED_SOURCE_SHA256="de26ba2c1530f9086a878521f4705896c8f2ad332179ceec0fde9d5f6d71d0ad"
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f"A07 harness source hash mismatch: {actual}")
exec(compile(source,str(PAYLOAD.with_suffix("")),"exec"),globals(),globals())

#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path

PAYLOAD=Path(__file__).with_suffix(".py.gz")
EXPECTED_SOURCE_SHA256="0dc330887718767812b2143877b751dc1ad580e0cefe834afac88486ad5707e0"
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f"A08 harness source hash mismatch: {actual}")
exec(compile(source,str(PAYLOAD.with_suffix("")),"exec"),globals(),globals())

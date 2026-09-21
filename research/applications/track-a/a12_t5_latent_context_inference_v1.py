#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix(".py.gz")
EXPECTED_SOURCE_SHA256="628c23f8319aa0e429a5c0e4dd8b0007e1346a799428c1678d33189dda10bdfd"
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f"A12 harness source hash mismatch: {actual}")
exec(compile(source,str(PAYLOAD.with_suffix("")),"exec"),globals(),globals())

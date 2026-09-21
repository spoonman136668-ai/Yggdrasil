#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix(".py.gz")
EXPECTED_SOURCE_SHA256="299df0843e90524d3ace88373925f35c8d1418d52086a5d042321a20e69106ca"
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f"A14 harness source hash mismatch: {actual}")
exec(compile(source,str(PAYLOAD.with_suffix("")),"exec"),globals(),globals())

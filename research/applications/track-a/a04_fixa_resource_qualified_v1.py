#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path

PAYLOAD=Path(__file__).with_suffix(".py.gz")
EXPECTED_SOURCE_SHA256="0b0f1a47e109ee8f218c664c568dd981c97bfb382c54ec30d035e6c8cf4e4f1a"
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f"A04 FIXA harness source hash mismatch: {actual}")
exec(compile(source,str(PAYLOAD.with_suffix("")),"exec"),globals(),globals())

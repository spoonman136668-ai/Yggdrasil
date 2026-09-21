#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path

PAYLOAD = Path(__file__).with_suffix(".py.gz")
EXPECTED_SOURCE_SHA256 = "b2eeb1e589a029f16b0437ce1f3dd05826b81a91ab6c6d91ce25bb28b96db60b"

source = gzip.decompress(PAYLOAD.read_bytes())
actual = hashlib.sha256(source).hexdigest()
if actual != EXPECTED_SOURCE_SHA256:
    raise SystemExit(f"A02 harness source hash mismatch: {actual}")
exec(compile(source, str(PAYLOAD.with_suffix("")), "exec"), globals(), globals())

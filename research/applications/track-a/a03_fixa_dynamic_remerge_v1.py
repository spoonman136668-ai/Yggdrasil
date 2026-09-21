#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path

PAYLOAD = Path(__file__).with_suffix(".py.gz")
EXPECTED_SOURCE_SHA256 = "f38fbe4823c6f8e3093a45b701cc39054c3bc814a67a97053d180bacb5087234"

source = gzip.decompress(PAYLOAD.read_bytes())
actual = hashlib.sha256(source).hexdigest()
if actual != EXPECTED_SOURCE_SHA256:
    raise SystemExit(f"A03 FIXA harness source hash mismatch: {actual}")
exec(compile(source, str(PAYLOAD.with_suffix("")), "exec"), globals(), globals())

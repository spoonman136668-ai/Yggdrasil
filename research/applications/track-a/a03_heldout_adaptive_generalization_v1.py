#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path

PAYLOAD = Path(__file__).with_suffix(".py.gz")
EXPECTED_SOURCE_SHA256 = "7f7cd60ababa073cc7a3c541033c6aee7ca5c9c77a76e8cec5a17ee00ed984c1"

source = gzip.decompress(PAYLOAD.read_bytes())
actual = hashlib.sha256(source).hexdigest()
if actual != EXPECTED_SOURCE_SHA256:
    raise SystemExit(f"A03 harness source hash mismatch: {actual}")
exec(compile(source, str(PAYLOAD.with_suffix("")), "exec"), globals(), globals())

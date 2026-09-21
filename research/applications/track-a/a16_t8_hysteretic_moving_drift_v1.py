#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz')
EXPECTED_SOURCE_SHA256='cd89dbc46174c97e0bea0bc0a1db4b65eea9b5732521ca30f00ed30f06b792fa'
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f'A16 harness source hash mismatch: {actual}')
exec(compile(source,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz')
EXPECTED_SOURCE_SHA256='066e66e36e601effa777052e54f7470d96ddee21d5b1153e767b0ebe6aa43c9f'
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f'A17 FIXA source hash mismatch: {actual}')
exec(compile(source,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

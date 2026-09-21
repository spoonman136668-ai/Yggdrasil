#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz')
EXPECTED_SOURCE_SHA256='a3760a2857c06dd12e3bbaf293c600147b98c45384bde24e69b3edaddf4476f3'
source=gzip.decompress(PAYLOAD.read_bytes())
actual=hashlib.sha256(source).hexdigest()
if actual!=EXPECTED_SOURCE_SHA256:
    raise SystemExit(f'A16 FIXA source hash mismatch: {actual}')
exec(compile(source,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

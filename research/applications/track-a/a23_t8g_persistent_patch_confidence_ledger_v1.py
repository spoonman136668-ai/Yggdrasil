#!/usr/bin/env python3
import gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz')
EXPECTED='05a9c9bf631282189160ebf7c2ad088b6212318440b561d7a4f613a2714763e0'
src=gzip.decompress(PAYLOAD.read_bytes())
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A23 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

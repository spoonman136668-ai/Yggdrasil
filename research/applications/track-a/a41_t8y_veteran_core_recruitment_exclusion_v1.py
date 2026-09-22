#!/usr/bin/env python3
import base64,gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz.b64')
EXPECTED='e3efb1b3fb7377e5975e88ac045d23dfb1e5592ba903e967cf09d2665567ad1b'
src=gzip.decompress(base64.b64decode(PAYLOAD.read_text().strip()))
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A41 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

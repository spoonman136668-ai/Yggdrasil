#!/usr/bin/env python3
import base64,gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz.b64')
EXPECTED='b4c778977af69ba40b9c9a3d6264aa6a93a9c7d6d52c16b45bdf41efae36b409'
raw=base64.b64decode(PAYLOAD.read_text().strip())
src=gzip.decompress(raw)
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A38 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('').with_suffix('')),'exec'),globals(),globals())

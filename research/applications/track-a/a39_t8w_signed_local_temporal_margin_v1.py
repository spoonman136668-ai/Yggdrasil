#!/usr/bin/env python3
import base64,gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz.b64')
EXPECTED='5b3cf9f9817410f76b607602e9149ed0e9b9f15b63f835db0fa09720683f2a87'
src=gzip.decompress(base64.b64decode(PAYLOAD.read_text().strip()))
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A39 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

#!/usr/bin/env python3
import base64,gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz.b64')
EXPECTED='97b837b5d65b73508fca8aff732391bbbce85a5be9624fab2aa4deb6150de5c2'
src=gzip.decompress(base64.b64decode(PAYLOAD.read_text().strip()))
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A43 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

#!/usr/bin/env python3
import base64,gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz.b64')
EXPECTED='10202cd1f770651d9dbf958c7433ac55c1d377612e6c6e7b9f226944b3a51cf7'
src=gzip.decompress(base64.b64decode(PAYLOAD.read_text().strip()))
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A40 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

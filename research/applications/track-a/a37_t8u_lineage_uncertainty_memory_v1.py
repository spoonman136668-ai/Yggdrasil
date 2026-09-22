#!/usr/bin/env python3
import base64,gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz.b64')
EXPECTED='3e69f508489181c989c79d1d7c72f83a751fe457e726c520785b126e0a095de6'
raw=base64.b64decode(PAYLOAD.read_text().strip())
src=gzip.decompress(raw)
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A37 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('').with_suffix('')),'exec'),globals(),globals())

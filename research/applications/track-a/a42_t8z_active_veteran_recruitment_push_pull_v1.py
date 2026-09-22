#!/usr/bin/env python3
import base64,gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz.b64')
EXPECTED='583203d2162ac7b27da6ea81f161496bee9d5c1e2aa0a657d687ae2b7a9c8c1b'
src=gzip.decompress(base64.b64decode(PAYLOAD.read_text().strip()))
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A42 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

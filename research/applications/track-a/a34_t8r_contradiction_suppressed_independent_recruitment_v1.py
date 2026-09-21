#!/usr/bin/env python3
import gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz')
EXPECTED='b8095a5839b5bef2567e28fe6c8d2d9aeaf85b697d46f9bf2507078088c53d88'
src=gzip.decompress(PAYLOAD.read_bytes())
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A34 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

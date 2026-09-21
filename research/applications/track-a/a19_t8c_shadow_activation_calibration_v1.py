#!/usr/bin/env python3
import gzip, hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz')
EXPECTED='d9637729a6b53526efd4a3fb7f90f37efea6185ab5f0f863419a63cff8ad649f'
src=gzip.decompress(PAYLOAD.read_bytes())
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A19 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

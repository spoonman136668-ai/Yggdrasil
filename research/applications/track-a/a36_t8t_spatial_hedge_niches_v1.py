#!/usr/bin/env python3
import gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz')
EXPECTED='5ff16100fc817a650a74e74d574ee9361de824418c38323c03192493359cd1d3'
src=gzip.decompress(PAYLOAD.read_bytes())
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A36 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix("")),'exec'),globals(),globals())

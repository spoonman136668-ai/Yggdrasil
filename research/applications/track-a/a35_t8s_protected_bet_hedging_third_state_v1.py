#!/usr/bin/env python3
import gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz')
EXPECTED='073f60c43f16b80e47e359998e8477a2ddf112d5567790ec7729bbc9b39ec030'
src=gzip.decompress(PAYLOAD.read_bytes())
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A35 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

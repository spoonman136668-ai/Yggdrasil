#!/usr/bin/env python3
import gzip,hashlib
from pathlib import Path
PAYLOAD=Path(__file__).with_suffix('.py.gz')
EXPECTED='67522a26a83b457014453634db2deef3ffb539fea4fe78d2ca165883f19372c4'
src=gzip.decompress(PAYLOAD.read_bytes())
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A26 source hash mismatch: {got}')
exec(compile(src,str(PAYLOAD.with_suffix('')),'exec'),globals(),globals())

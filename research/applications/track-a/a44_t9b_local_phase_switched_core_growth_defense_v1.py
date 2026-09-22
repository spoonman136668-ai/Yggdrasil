#!/usr/bin/env python3
import base64,gzip,hashlib
from pathlib import Path
HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM+'.payload.part*.b64'))
if len(PARTS)!=6:
    raise SystemExit(f'A44 payload part count mismatch: {len(PARTS)}')
EXPECTED='39b4080d6fc44b2229d7f6e61c042101741d02892777d3b824eb336d211e1039'
encoded=''.join(''.join(p.read_text().split()) for p in PARTS)
src=gzip.decompress(base64.b64decode(encoded,validate=True))
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED: raise SystemExit(f'A44 source hash mismatch: {got}')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

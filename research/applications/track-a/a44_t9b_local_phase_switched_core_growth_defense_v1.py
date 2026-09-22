#!/usr/bin/env python3
import base64,gzip,hashlib
from pathlib import Path
HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM+'.payload.part*.b64'))
if len(PARTS)!=6:
    raise SystemExit(f'A44 payload part count mismatch: {len(PARTS)}')
EXPECTED_B64='d7cf3ab1fdcbf2e835e6a284be6be3ea64ba5dcc129520039021cede1dabe681'
EXPECTED_GZIP='ca134a87e8b66ed9ee55d5fa1b701c2c0c1c6906e740ea10a0157af1e07a949b'
EXPECTED_UNPATCHED='39b4080d6fc44b2229d7f6e61c042101741d02892777d3b824eb336d211e1039'
EXPECTED_PATCHED='83ea9d5adc4f3fccb8147f646035a7c98caa8a2887bfb17bc21af691ca6caa0b'
OLD=b"    arm_base=h64('YGG-A44-ARM-SEED',seed,ctx,rep,arm)\n"
NEW=(b"    if kind in ('BASE','MARGIN_REINFORCE'):\n"
     b"        arm_base=h64('YGG-A43-ARM-SEED',seed,ctx,rep,arm)\n"
     b"    elif kind=='ACTIVE_MARGIN_RECRUIT':\n"
     b"        arm_base=h64('YGG-A42-ARM-SEED',seed,ctx,rep,arm)\n"
     b"    else:\n"
     b"        arm_base=h64('YGG-A44-ARM-SEED',seed,ctx,rep,arm)\n")
encoded=''.join(''.join(p.read_text().split()) for p in PARTS)
if hashlib.sha256(encoded.encode()).hexdigest()!=EXPECTED_B64:
    raise SystemExit('A44 encoded payload hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP:
    raise SystemExit('A44 gzip payload hash mismatch')
src=gzip.decompress(gz)
if hashlib.sha256(src).hexdigest()!=EXPECTED_UNPATCHED:
    raise SystemExit('A44 unpatched source hash mismatch')
if src.count(OLD)!=1:
    raise SystemExit(f'A44 RNG patch target count mismatch: {src.count(OLD)}')
src=src.replace(OLD,NEW)
got=hashlib.sha256(src).hexdigest()
if got!=EXPECTED_PATCHED:
    raise SystemExit(f'A44 patched source hash mismatch: {got}')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

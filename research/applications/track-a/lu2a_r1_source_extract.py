#!/usr/bin/env python3
import base64, gzip, hashlib, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
parts=sorted(HERE.glob("lu2a_partial_learned_hu_closed_loop_v1.source.chunk*.b64"))
if len(parts)!=5:
    raise SystemExit(f"part-count mismatch: {len(parts)}")
encoded="".join(p.read_text(encoding="ascii").strip() for p in parts)
if len(encoded)!=9760:
    raise SystemExit(f"base64 char-count mismatch: {len(encoded)}")
gz=base64.b64decode(encoded + ("="*((4-len(encoded)%4)%4)), validate=True)
if len(gz)!=7320:
    raise SystemExit(f"gzip byte-count mismatch: {len(gz)}")
src=gzip.decompress(gz)
if len(src)!=23066:
    raise SystemExit(f"source byte-count mismatch: {len(src)}")
sha=hashlib.sha256(src).hexdigest()
if sha!="251fcb655a04b109dc9716a021acef9f956333ca265685246f41868923627f35":
    raise SystemExit(f"source hash mismatch: {sha}")
Path(sys.argv[1]).write_bytes(src)

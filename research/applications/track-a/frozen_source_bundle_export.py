#!/usr/bin/env python3
import base64, gzip, hashlib, json, re, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]).parent/"frozen-source-bundle"
OUT.mkdir(parents=True,exist_ok=True)

def grab_int(txt,name):
    m=re.search(rf"^{name}\s*=\s*(\d+)\s*$",txt,re.M)
    return int(m.group(1)) if m else None

def grab_str(txt,name):
    m=re.search(rf"^{name}\s*=\s*['\"]([^'\"]+)['\"]\s*$",txt,re.M)
    return m.group(1) if m else None

manifest={}
for loader in sorted(HERE.glob("*.py")):
    txt=loader.read_text(encoding="utf-8",errors="strict")
    src_bytes=grab_int(txt,"EXPECTED_SOURCE_BYTES")
    src_sha=grab_str(txt,"EXPECTED_SOURCE_SHA256")
    if src_bytes is None or src_sha is None or "gzip.decompress" not in txt:
        continue
    stem=loader.stem
    # Generic loader convention.
    parts=sorted(HERE.glob(stem+".source.chunk*.b64"))
    # LU2A-R1 intentionally points at non-R1 chunk stem.
    if not parts and stem=="lu2a_partial_learned_hu_closed_loop_v1_r1":
        parts=sorted(HERE.glob("lu2a_partial_learned_hu_closed_loop_v1.source.chunk*.b64"))
    if not parts:
        continue
    enc="".join(p.read_text(encoding="ascii").strip() for p in parts)
    try:
        raw=base64.b64decode(enc + ("="*((4-len(enc)%4)%4)),validate=True)
        src=gzip.decompress(raw)
    except Exception:
        continue
    if len(src)!=src_bytes or hashlib.sha256(src).hexdigest()!=src_sha:
        # Some current chunk families serve a different historical loader; do not export mismatches.
        continue
    dst=OUT/loader.name
    dst.write_bytes(src)
    manifest[loader.name]={
        "bytes":len(src),
        "sha256":hashlib.sha256(src).hexdigest(),
        "parts":[p.name for p in parts],
    }

(OUT/"manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
Path(sys.argv[1]).write_text(json.dumps({"exported":len(manifest),"manifest":manifest},sort_keys=True,separators=(",",":")),encoding="utf-8")

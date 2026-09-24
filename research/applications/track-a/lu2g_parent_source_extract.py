#!/usr/bin/env python3
import base64, gzip, hashlib, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPECS={
  "task1_emergent_functional_organization_v1": (8,14676,11007,37394,"567c37e3e2171bc3cfc15b996c447e87b7ac5cdafb7bc299ba104284ae826e12"),
  "task1b_commitment_neutral_ingress_sensing_v1": (3,4868,3650,12748,"e8d409c5eb8e750123aae4979fd1091611a915c22f7cf977e420345186aef6b9"),
  "task1e_request_bound_anchor_handoff_v1": (3,5904,4427,15476,"c1578a0d21d1125a26d81664adc0c3a78a3a23e9a4a2a4865d526e41af7d2207"),
  "task1f_local_hedge_ambiguity_r1_v1": (4,7504,5626,18265,"a3122a9f4f6da6c138cc12944528f5e2e3ef608e904067ef30da7feab7d640f4"),
}
out={}
for stem,(parts_n,b64_n,gz_n,src_n,sha_expected) in SPECS.items():
    parts=sorted(HERE.glob(stem+".source.chunk*.b64"))
    if len(parts)!=parts_n:
        raise SystemExit(f"{stem} part-count mismatch {len(parts)}")
    enc="".join(p.read_text(encoding="ascii").strip() for p in parts)
    if len(enc)!=b64_n:
        raise SystemExit(f"{stem} b64 mismatch {len(enc)}")
    gz=base64.b64decode(enc,validate=True)
    if len(gz)!=gz_n:
        raise SystemExit(f"{stem} gzip mismatch {len(gz)}")
    src=gzip.decompress(gz)
    if len(src)!=src_n:
        raise SystemExit(f"{stem} source bytes mismatch {len(src)}")
    sha=hashlib.sha256(src).hexdigest()
    if sha!=sha_expected:
        raise SystemExit(f"{stem} source hash mismatch {sha}")
    out[stem]={"sha256":sha,"bytes":len(src),"source":src.decode("utf-8")}
Path(sys.argv[1]).write_text(json.dumps(out,sort_keys=True,separators=(",",":")),encoding="utf-8")

#!/usr/bin/env python3
import ast, base64, gzip, hashlib, json, re, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
LOADERS=[
    "task1_emergent_functional_organization_v1.py",
    "task1b_commitment_neutral_ingress_sensing_v1.py",
    "task1e_request_bound_anchor_handoff_v1.py",
    "task1f_local_hedge_ambiguity_r1_v1.py",
    "lu0c_density_preserving_local_pool_v1.py",
    "lu0d_no_pool_confirmation_v1.py",
    "lu0e_v02_staged_local_identifiability_v1.py",
    "lu1a_first_learned_staged_cell_v1.py",
    "lu1b_focal_side_canonical_stay_v1.py",
    "lu1e_state_conditioned_equivariant_relational_updater_v1.py",
]

def constants(text):
    tree=ast.parse(text)
    out={}
    for node in tree.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            k=node.targets[0].id
            try: out[k]=ast.literal_eval(node.value)
            except Exception: pass
    return out

bundle={}
for name in LOADERS:
    p=HERE/name
    text=p.read_text(encoding="utf-8")
    c=constants(text)
    stem=p.stem
    parts=sorted(HERE.glob(stem+".source.chunk*.b64"))
    exp_parts=int(c["EXPECTED_PARTS"])
    if len(parts)!=exp_parts: raise SystemExit(f"{name}: part-count {len(parts)} != {exp_parts}")
    encoded="".join(x.read_text(encoding="ascii").strip() for x in parts)
    if len(encoded)!=int(c["EXPECTED_B64_CHARS"]): raise SystemExit(f"{name}: b64 length")
    if "EXPECTED_B64_SHA256" in c and hashlib.sha256(encoded.encode("ascii")).hexdigest()!=c["EXPECTED_B64_SHA256"]:
        raise SystemExit(f"{name}: b64 hash")
    padded=encoded+("="*((4-len(encoded)%4)%4))
    gz=base64.b64decode(padded,validate=True)
    if len(gz)!=int(c["EXPECTED_GZIP_BYTES"]): raise SystemExit(f"{name}: gz length")
    if "EXPECTED_GZIP_SHA256" in c and hashlib.sha256(gz).hexdigest()!=c["EXPECTED_GZIP_SHA256"]:
        raise SystemExit(f"{name}: gz hash")
    src=gzip.decompress(gz)
    sha=hashlib.sha256(src).hexdigest()
    if len(src)!=int(c["EXPECTED_SOURCE_BYTES"]): raise SystemExit(f"{name}: source length")
    if sha!=c["EXPECTED_SOURCE_SHA256"]: raise SystemExit(f"{name}: source hash")
    bundle[name]={"bytes":len(src),"sha256":sha,"source":src.decode("utf-8")}

Path(sys.argv[1]).write_text(json.dumps(bundle,sort_keys=True)+"\n",encoding="utf-8")

#!/usr/bin/env python3
import ast, base64, gzip, hashlib, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
p=HERE/"lu2g_second_task_compositional_service_transfer_v1.candidate.py"
text=p.read_text(encoding="utf-8")
tree=ast.parse(text)
vals={}
for node in tree.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
        try: vals[node.targets[0].id]=ast.literal_eval(node.value)
        except Exception: pass
enc=vals["ENCODED"]
gz=base64.b64decode(enc,validate=True)
assert len(gz)==vals["EXPECTED_GZIP_BYTES"]
assert hashlib.sha256(gz).hexdigest()==vals["EXPECTED_GZIP_SHA256"]
src=gzip.decompress(gz)
assert len(src)==vals["EXPECTED_SOURCE_BYTES"]
assert hashlib.sha256(src).hexdigest()==vals["EXPECTED_SOURCE_SHA256"]
Path(sys.argv[1]).write_bytes(src)

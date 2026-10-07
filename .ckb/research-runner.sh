#!/usr/bin/env bash
set -euo pipefail
export E="$RUNNER_TEMP/ckb-research-evidence"; rm -rf "$E"; mkdir -p "$E"
test "$(git rev-parse HEAD)" = "$PACKAGE_SHA"
git merge-base --is-ancestor '3bd913bd4057f3780367e3687e1fa83adfc9f46a' HEAD
git merge-base --is-ancestor '' HEAD
python - <<'PY'
import base64,hashlib,json,os,pathlib
raw=base64.b64decode("eyJhdXRob3JpdHlfd29ya2Zsb3dfcmVmIjoibWFpbiIsImF1dGhvcml0eV93b3JrZmxvd19yZWZfc2hhIjoiYWFkZWE3NjVmZmU5ODk4NmMxNTgwZWFhZDU4NDM2MjYwZDJhMmNhZCIsImNrYl9wbGFuZV9tYWluX3NoYSI6ImU1MzI0MDU5MmViMjA5MWIwYjhmMDQ1ZDc1OGMzNDE3NzQ4NDYzZTIiLCJleHBlcmltZW50IjoiRVhQLURHUi1FWFRFUk5BTC1DVU1VTEFUSVZFLURFUEVOREVOVC1QSVBFTElORS1DT05TT0xJREFUSU9OLUNPTlNVTUVSLUNPVVBMSU5HLURJQUdOT1NJUy0wOTQiLCJmZXRjaF9kZWNpc2lvbiI6eyJzY2hlbWEiOiJja2ItcGxhbmUuZXh0ZXJuYWwtZXhwb3N1cmUtZmV0Y2gudjEiLCJkaXNwb3NpdGlvbiI6IlJFQURZX0ZFVENIIiwic2NvcGUiOiJmZXRjaC12ZXJpZnktb25seSIsInJlYXNvbnMiOm51bGx9LCJtYW5pZmVzdF9zaGEyNTYiOiJjMmE4ZmE0ZTU1MjkwZGM4ZjM4NmI1MTY4ZTE3MWIwOWE4ZGI5YmRhODlhNzQ4Y2ZhNjUzMmVlODZmYjM4NDIxIiwicGxhbl9kZWNpc2lvbiI6eyJzY2hlbWEiOiJja2ItcGxhbmUuZXh0ZXJuYWwtZXhwb3N1cmUudjEiLCJkaXNwb3NpdGlvbiI6IlJFQURZX1BMQU4iLCJzY29wZSI6InBsYW4tb25seSIsInJlYXNvbnMiOm51bGx9LCJwcmVyZWdpc3RyYXRpb25fc2hhIjoiMjJiOGMwY2RmZTc4MzNhZjJmODE4ZWJjYzZiNzU2YWQ3YWU2YjU1ZSIsInByb2plY3QiOiJZZ2dkcmFzaWwiLCJyZXF1ZXN0X2lkIjoiYTZkMGQyNWU2OTdhNTVkZmNiMjc1ZDI2MjcyNmUyMmEiLCJyZXNlYXJjaF9kZWNpc2lvbiI6eyJzY2hlbWEiOiJja2ItcGxhbmUuZXh0ZXJuYWwtZXhwb3N1cmUtcmVzZWFyY2gudjEiLCJkaXNwb3NpdGlvbiI6IlJFQURZX1JFU0VBUkNIIiwic2NvcGUiOiJyZXNlYXJjaC1jb25zdW1lLW9uY2UiLCJyZWFzb25zIjpudWxsfSwicmVzZWFyY2hfaG9zdCI6IkNLQi1QTEFORS1SRU1PVEUiLCJydW5uZXJfaWQiOiJDS0ItUExBTkUtUkVNT1RFIiwic2NoZW1hIjoiY2tiLXBsYW5lLmV4dGVybmFsLWV4cG9zdXJlLXJlYWR5LXJlc2VhcmNoLXJlY2VpcHQudjEifQ==",validate=True)
assert hashlib.sha256(raw).hexdigest()=="3de1c384deb9c93ec6afd344204f1bf2c34fd56f9f434b321670b9d94a745a90"
r=json.loads(raw)
assert r["schema"]=="ckb-plane.external-exposure-ready-research-receipt.v1"
assert r["project"]=="Yggdrasil"
assert r["experiment"]=="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-CONSUMER-COUPLING-DIAGNOSIS-094"
assert r["preregistration_sha"]==""
assert r["manifest_sha256"]=="c2a8fa4e55290dc8f386b5168e171b09a8db9bda89a748cfa6532ee86fb38421"
assert r["ckb_plane_main_sha"]=="e53240592eb2091b0b8f045d758c3417748463e2"
assert r["research_decision"]["disposition"]=="READY_RESEARCH"
(pathlib.Path(os.environ["E"])/"authority.json").write_bytes(raw)
PY
python - <<'PY'
import hashlib,json,os,pathlib,urllib.parse,urllib.request
root=pathlib.Path(os.environ["RUNNER_TEMP"]); names=("transfer","third","fourth","fifteenth","sixteenth"); dirs={n:root/("y094-"+n) for n in names}
for p in dirs.values():p.mkdir(parents=True,exist_ok=True)
hist={
"transfer":[("code","https://raw.githubusercontent.com/python/cpython/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/Lib/statistics.py",61896,"3023ec949802c2e880a000775bfd1a6b70c21b5423881118141e3ec69d8e3336",41453,"66bb25b24a0316b4965c64798494de93a1d7332672b15b5f430ab6a2fb4b9d45"),("structured","https://raw.githubusercontent.com/json-schema-org/JSON-Schema-Test-Suite/5b0ee1613e45fcc2bddac00e07c19cd49b00d8a8/tests/draft2020-12/uniqueItems.json",14490,"ed84ef6ddc827659e257ba64cbe9679f06932b6320bea5c07622bf3d2cc4daa5",14365,"95ddbd0eaef29aad5ecfc74f9da21b795481f58b2c59380324a445fcd4d08932"),("technical_prose","https://raw.githubusercontent.com/golang/go/6f5c275ebdc454197fff5f1496521c8f81e20eef/doc/README.md",3124,"c1bf000e7a873b3afed329c5b9f9c07f7692b1d7fb2bfca2d7600cec8b1d1407",1454,"48c3d95b8b03864a4af41d892710675956cde85afd0d5d6c331594de9f17881b")],
"third":[("code","https://raw.githubusercontent.com/torvalds/linux/a74306e2e676f9775457366fc047a660fbf02f26/kernel/sched/core.c",303863,"9297982652b9810b3508993c06d3c6e097ebca5cbe1ef3a6246bccfa0c1128b1",41453,"50744a9e70d67d62c97f3f434f4f05788b6b8514c6bce46cf7dafbaf49e2abff"),("structured","https://raw.githubusercontent.com/SchemaStore/schemastore/de76181a2ab215431d3e9314bc14f83cc3b01ad2/src/schemas/json/github-workflow.json",118601,"d10c9f4656e1bd5bc6727e9b35080e017dc167154726fca93da33c7a6bd1c4f3",14365,"2a97ba02bc5e479b1738f6f0c3e09318bb5a255350c84de014ddbcebea46af56"),("technical_prose","https://raw.githubusercontent.com/rust-lang/book/1500248d8f230566e4ec9f27fcbb8fe9e2898ab1/src/ch01-03-hello-cargo.md",11025,"61369f359b84b646fc3773eb569a26bc18ba6edb4cf2be06a84472c7054c0e39",1454,"23c002a1984ed065abfdbafa82100ed54d6bf6276a947676e710a30c75d96017")],
"fourth":[("code","https://raw.githubusercontent.com/kubernetes/kubernetes/e7967bb9b76d43a6388abb7a4e90d2f899ef97ff/pkg/kubelet/kubelet.go",156626,"e0f247ef45cb281166b58ba1a013dc6925023388193bd74c1f126c695b770d34",41453,"283073d9f6c0dd868c39a913364bce6744ff1e29c038f6920197c0d33e0c2ac1"),("structured","https://raw.githubusercontent.com/microsoft/TypeScript/50d70a3f5f453a79a4323b263165da51f656a4e3/package-lock.json",143844,"52b6c9bd0a26ef1b0fc27dfbfaa00df6a047cdddd587d07c4f6c1c3345faf5cf",14365,"a46fcfb7d862b03b750b61a5f667d4ac25a064df9ccb746e395db7e864068933"),("technical_prose","https://raw.githubusercontent.com/django/django/a461af8ce48762d7ec602260aaff81014ddccbcb/docs/intro/tutorial01.txt",10844,"1cf1817e6211b7c0fa9e8044ee808fde1e8f16ca5f9d5ab5358510a5c9591b96",1454,"5d0c2efd139bd6094098bc893ed746020f03e0860a25f278348f43f47c236222")]}
for group,sources in hist.items():
  for domain,url,full_n,full_h,prefix_n,prefix_h in sources:
    data=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"yggdrasil-y094"}),timeout=90).read(full_n+1)
    assert len(data)==full_n and hashlib.sha256(data).hexdigest()==full_h
    p=data[:prefix_n];assert hashlib.sha256(p).hexdigest()==prefix_h
    (dirs[group]/{"code":"code.bin","structured":"structured.bin","technical_prose":"technical-prose.bin"}[domain]).write_bytes(p)
m=json.load(open("research/experiments/exp-dgr-external-cumulative-dependent-pipeline-consolidation-consumer-coupling-diagnosis-094-manifest.json"))
assert m["manifest_sha256"]=="c2a8fa4e55290dc8f386b5168e171b09a8db9bda89a748cfa6532ee86fb38421"
for group in m["unseen"]:
  for src in group["sources"]:
    url=f"https://raw.githubusercontent.com/{src['repo']}/{src['commit']}/{urllib.parse.quote(src['path'])}"
    data=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"yggdrasil-y094"}),timeout=90).read()
    assert hashlib.sha1((f"blob {len(data)}\0").encode()+data).hexdigest()==src["git_blob"]
    p=data[:src["prefix_bytes"]];assert hashlib.sha256(p).hexdigest()==src["prefix_sha256"]
    (dirs[group["name"]]/{"code":"code.bin","structured":"structured.bin","technical_prose":"technical-prose.bin"}[src["domain"]]).write_bytes(p)
PY
python -m py_compile research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-consumer-coupling-diagnosis-094.py
python -m pip install --disable-pip-version-check -e '.[test]'
python -m pytest -q
script='research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-consumer-coupling-diagnosis-094.py'
python "$script" --transfer-root "$RUNNER_TEMP/y094-transfer" --third-root "$RUNNER_TEMP/y094-third" --fourth-root "$RUNNER_TEMP/y094-fourth" --fifteenth-root "$RUNNER_TEMP/y094-fifteenth" --sixteenth-root "$RUNNER_TEMP/y094-sixteenth" --out "$E/result1.json" --resource-out "$E/resource.json"
python "$script" --transfer-root "$RUNNER_TEMP/y094-transfer" --third-root "$RUNNER_TEMP/y094-third" --fourth-root "$RUNNER_TEMP/y094-fourth" --fifteenth-root "$RUNNER_TEMP/y094-fifteenth" --sixteenth-root "$RUNNER_TEMP/y094-sixteenth" --out "$E/result2.json"
cmp "$E/result1.json" "$E/result2.json"
python - <<'PY'
import json,math,os,pathlib
E=pathlib.Path(os.environ["E"]);r=json.loads((E/"result1.json").read_text());m=r["metrics"];arms={a["id"]:a for a in r["arms"]};non=[arms[k] for k in ("target-continuous_target-discrete","target-continuous_retained-discrete","retained-continuous_retained-discrete")]
valid=(m["invalid_evaluation_rows"]==0 and m["capacity_total"]==16 and m["capacity_active"]==7 and m["capacity_retained"]==9 and m["coupling_arm_count"]==4 and m["addressing_change_count"]==0 and m["capacity_growth_event_count"]==0 and m["source_identity_mismatch_count"]==0 and m["transport_identity_mismatch_count"]==0 and all(math.isfinite(float(v)) for v in m.values()))
strong=[a for a in non if a["improved_context_count"]==2 and a["lost_y091_clean_rescue_count"]==0 and a["partner_collateral_failure_count"]==0]
support=valid and len(strong)==1
mixed=valid and not support and (any(a["improved_context_count"]==1 and a["lost_y091_clean_rescue_count"]==0 and a["partner_collateral_failure_count"]==0 for a in non) or len(strong)>=2)
cls="invalid" if not valid else "supported" if support else "mixed" if mixed else "negative"
out={"schema":"yggdrasil.research-classification.v1","experiment":"EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-CONSUMER-COUPLING-DIAGNOSIS-094","classification":cls,"validity_pass":valid,"diagnostic_only":True,"rsi_success":False,"next_successor":None,"package_sha":os.environ["PACKAGE_SHA"],"metrics":m,"arms":r["arms"]}
(E/"classification.json").write_text(json.dumps(out,separators=(",",":")),encoding="utf-8");print(json.dumps(out,separators=(",",":")))
PY
rm -rf "$RUNNER_TEMP"/y094-*

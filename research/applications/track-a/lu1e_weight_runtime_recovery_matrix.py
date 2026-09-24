#!/usr/bin/env python3
import base64, hashlib, json, os, platform, sys
from pathlib import Path
import numpy as np
import torch
import lu1e_state_conditioned_equivariant_relational_updater_v1 as e

LU1EF1="f459273c897a7bd889b6de2ec2d9720374215327"
EXPECTED_RAW_BYTES=55917
EXPECTED_RAW_SHA="b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023"
EXPECTED_B64_CHARS=74556
EXPECTED_B64_SHA="b9803bdfdd8dfc69c4a1f9d205f0f92083dc1c29ee0c08b98d15a3c45edb95d3"
EXPECTED_METRICS_SHA="e5a54d75e37b475653a3bb3384fa27c791f928c0d50953a105a80144dd3d0c8e"

outdir=Path(sys.argv[1])
outdir.mkdir(parents=True,exist_ok=True)
wp=outdir/"weights.bin"
mp=outdir/"metrics.json"
e.train_once(LU1EF1,wp,mp)
raw=wp.read_bytes()
metrics=mp.read_bytes()
enc=base64.b64encode(raw).decode("ascii")
mj=json.loads(metrics)

raw_sha=hashlib.sha256(raw).hexdigest()
b64_sha=hashlib.sha256(enc.encode("ascii")).hexdigest()
metrics_sha=hashlib.sha256(metrics).hexdigest()
canonical=(
    len(raw)==EXPECTED_RAW_BYTES and raw_sha==EXPECTED_RAW_SHA and
    len(enc)==EXPECTED_B64_CHARS and b64_sha==EXPECTED_B64_SHA and
    metrics_sha==EXPECTED_METRICS_SHA
)
result={
    "schema":"yggdrasil.lu1e-weight-runtime-recovery.v1",
    "lu1ef1":LU1EF1,
    "requested_cpu_capability":os.environ.get("ATEN_CPU_CAPABILITY"),
    "reported_cpu_capability":getattr(torch.backends.cpu,"get_cpu_capability",lambda:None)(),
    "python":sys.version,
    "platform":platform.platform(),
    "numpy":np.__version__,
    "torch":torch.__version__,
    "weight_bytes":len(raw),
    "weight_sha256":raw_sha,
    "base64_chars":len(enc),
    "base64_sha256":b64_sha,
    "metrics_bytes":len(metrics),
    "metrics_sha256":metrics_sha,
    "final_train_mean_batch_equal_head_loss":mj["final_train_mean_batch_equal_head_loss"],
    "validation_total_equal_head_loss":mj["validation"]["total_equal_head_loss"],
    "canonical_exact_match":canonical,
}
(outdir/"result.json").write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
if canonical:
    (outdir/"canonical_weights.b64").write_text(enc,encoding="ascii")
else:
    wp.unlink()
    mp.unlink()
print(json.dumps(result,sort_keys=True))

#!/usr/bin/env python3
import base64, hashlib, json, sys, tempfile
from pathlib import Path
import lu1e_state_conditioned_equivariant_relational_updater_v1 as e

HERE=Path(__file__).resolve().parent
LU1EF1="f459273c897a7bd889b6de2ec2d9720374215327"
EXPECTED_RAW_BYTES=55917
EXPECTED_RAW_SHA="b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023"
EXPECTED_B64_CHARS=74556
EXPECTED_B64_SHA="b9803bdfdd8dfc69c4a1f9d205f0f92083dc1c29ee0c08b98d15a3c45edb95d3"
EXPECTED_METRICS_SHA="e5a54d75e37b475653a3bb3384fa27c791f928c0d50953a105a80144dd3d0c8e"

with tempfile.TemporaryDirectory(prefix="lu1e-rebuild-") as td:
    wp=Path(td)/"weights.bin"
    mp=Path(td)/"metrics.json"
    e.train_once(LU1EF1,wp,mp)
    raw=wp.read_bytes()
    metrics=mp.read_bytes()

enc=base64.b64encode(raw).decode("ascii")
parts=sorted(HERE.glob("lu2a_lu1e_canonical_weights.chunk*.b64"))
surviving="".join(p.read_text(encoding="ascii").strip() for p in parts)
tail=enc[len(surviving):] if enc.startswith(surviving) else ""

out={
  "lu1ef1":LU1EF1,
  "source_sha256":"38c3d42786426d4ace4a779b69d49509d65a7eb31f9bfa3c4209e603879d0b2a",
  "raw_bytes":len(raw),
  "raw_sha256":hashlib.sha256(raw).hexdigest(),
  "metrics_bytes":len(metrics),
  "metrics_sha256":hashlib.sha256(metrics).hexdigest(),
  "base64_chars":len(enc),
  "base64_sha256":hashlib.sha256(enc.encode("ascii")).hexdigest(),
  "surviving_regular_parts":len(parts),
  "surviving_prefix_chars":len(surviving),
  "surviving_prefix_exact":enc.startswith(surviving),
  "recovered_tail_chars":len(tail),
  "recovered_tail_sha256":hashlib.sha256(tail.encode("ascii")).hexdigest() if tail else None,
  "all_frozen_identities_match":(
      len(raw)==EXPECTED_RAW_BYTES and
      hashlib.sha256(raw).hexdigest()==EXPECTED_RAW_SHA and
      len(enc)==EXPECTED_B64_CHARS and
      hashlib.sha256(enc.encode("ascii")).hexdigest()==EXPECTED_B64_SHA and
      hashlib.sha256(metrics).hexdigest()==EXPECTED_METRICS_SHA and
      enc.startswith(surviving)
  ),
  "recovered_tail":tail,
}
Path(sys.argv[1]).write_text(json.dumps(out,sort_keys=True,separators=(",",":")),encoding="utf-8")
if not out["all_frozen_identities_match"]:
    raise SystemExit("frozen LU-1E reproduction identity mismatch")

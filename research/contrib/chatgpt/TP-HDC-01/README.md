# TP-HDC-01 — fixed-byte task-keyed superposition (source-free DEV)

**Status:** first frozen synthetic primary run completed, exact-source replay matched; **no native Yggdrasil science qualification**. Independent implementation, Windows, full candidate regression, and protected original-world first use remain **UNVERIFIED**.

## Source and custody

- Accepted `main` at preflight: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Cumulative Amalgam ancestor: `86264b41a08d49f558418c0fba367f3a2636befa`, PR #1278.
- Frozen preregistration **before any score**: `13852c61883a76b08396add9e58b87a7c9bbd368` (`prereg.json`).
- Exact executed source: `d1114fedb5988a174a00f1e080cba5f552a0ef37`, `probe.py` blob `fc293f4aa3fb7bdc80dd7e433e809ddbca271a06`, SHA-256 `a5fe0fa221585ac594e6ca03563a2c2b7bbcbe5f43cda137c66d26e73cae556d`.
- Original complete first-result JSON SHA-256 `2835204c3474816d7a7f1999400a6f6b59307d00ba4a79962f76744513d76244`. Preserved losslessly in `result.json.gz.base64`: decode Base64 then gzip. Archive gzip SHA-256 `87fbada4f5931cc3b7658c2ff27bbfc5204123dc47b16361a78f7939e91aa275`; Git blob `c923d4cad741f4e5b86206de29fc0ee76ce1d8d8`.
- Full machine-readable provenance: `provenance.json`. Four fixed seeds: 101, 202, 303, 404. Four stages A → B → A → C, 2,048 synthetic public observations across seeds, **no CausalGym or protected first-use**.
- No runner, deployment, promotion, merge, accepted-ref mutation, or paid API.

## Results (mean observed prequential Brier; lower is better)

| Arm | A | B | A-return | C | Retention drift after B |
| --- | ---: | ---: | ---: | ---: | --- |
| Exact task-tagged 8-bit counters | 0.187758 | **0.194270** | **0.167245** | 0.265220 | 0 on all four seeds |
| TP-HDC (4096 signed int8 dimensions) | 0.192639 | 0.200578 | 0.168319 | 0.270488 | -0.001768 to +0.002903 |
| Task-blind pooled counters | **0.187758** | 0.329773 | 0.223546 | 0.255214 | +0.040035 to +0.087318 |
| Sham all-task-same-key | 0.192639 | 0.322462 | 0.221577 | 0.256091 | +0.044582 to +0.092430 |
| No-update | 0.250000 | 0.250000 | 0.250000 | 0.250000 | 0 |

All **3/3 prespecified synthetic numerical conditions** were true. That only establishes that task-keyed HDC beat the pooled interference control in this very narrow labelled-task exercise, and came close to exact. **The exact task-tagged counter beats TP-HDC on all four stage scores** and has only **24 actually used count bytes** instead of the **4096-byte HDC channel**. The exact counter was padded to 4096 bytes for matched allocation; padding is not learned information. This invokes the preregistered exact-control dominance negative clause, even though the simpler numeric rules were satisfied. **Conservative classification: MIXED / negative for memory efficiency; SCIENTIFIC_PASS = FALSE**. Do not revise thresholds after the result.

**Saturation warning:** HDC clips **442,817** coordinate updates across the four seeds (sham **920,576**). It is a fixed-byte storage mechanism with significant finite-capacity stress; no infinite noninterference or unlimited memory claim is justified. Deterministic projection key cache is regenerated and not persisted in the channel, but transient runtime memory and projection computation are not free. Task IDs were provided externally; task discovery and unfamiliar causal transfer were not tested.

## Replay

From this directory, on Python 3.13.5 with only the standard library:

```bash
python probe.py > replay-result.json
python - <<'PY'
import base64, gzip, hashlib, json
from pathlib import Path
original = gzip.decompress(base64.b64decode(Path("result.json.gz.base64").read_text()))
assert hashlib.sha256(original).hexdigest() == "2835204c3474816d7a7f1999400a6f6b59307d00ba4a79962f76744513d76244"
old = json.loads(original)
new = json.loads(Path("replay-result.json").read_text())
for key in ("seeds", "aggregate", "frozen_rules", "outcome", "source_identity_sha256"):
    assert old[key] == new[key], key
print("TP_HDC01_EXACT_SOURCE_REPLAY_PASS")
PY
```

An exact-source local replay produced identical scientific fields and checkpoint digests. Initial **CPU 11.73 s**, replay **11.51 s**; reported tracemalloc peak **579,582 bytes** on a Linux 6.18 x86_64 container with Python 3.13.5. These CPU/RSS numbers are not native Yggdrasil runtime measurements.

## Interpretation and follow-on

TP-HDC demonstrates a bounded **task-keyed storage isolation** mechanism relative to a deliberately weak shared-memory control. It **does not beat an equally informed exact task-tagged count control**, does not prove action-consequence abstraction, and does not establish that a single channel outperforms specialized exact memories under useful density. Do **not** integrate into native cells based on this synthetic experiment.

A meaningful next experiment would first enforce an information-density frontier where exact task-tagged memory must operate under the same *actual* 4096-byte state with nontrivial task count and cold-restart keys, and include a strong compressed exact/hashed baseline, rather than merely padding a tiny exact count table. Freeze a separate protocol and obtain source-owner authority before any protected original-world run.

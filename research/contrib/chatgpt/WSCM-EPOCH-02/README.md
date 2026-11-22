# WSCM-EPOCH-02 — Sealed fresh-seed causal epoch trial (incomplete)

**Disposition: INVALID_INCOMPLETE_EXTERNAL_TIMEOUT. No verified scientific gain.** Source-free research contributor to [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), in existing draft [WSCM PR #1364](https://github.com/spoonman136668-ai/Yggdrasil/pull/1364).

## Frozen provenance
The new, disjoint 4-seed development protocol was committed **before execution** at `95c7d309ba6a4fdb2e9aa2da585d607d426fac13` (prereg Git blob `6001dd5377e61d948d28aae8eb9e691fdfe47073`). The independently tested, sealed one-shot runner and ten negative/source-custody unit tests were committed **before scoring** at `f14daabd1a48dc4ac88c46091157da20da1f0ccc`, blobs `33926ca8331277466fa8dae0ea55a511a3aa800c` and `0149c152af1530afcbc5ecbe71bf44ce734ddaf2`. Parent Amalgam stays `86264b41a08d49f558418c0fba367f3a2636befa`. Original WSCM-EPOCH-01 algorithm and all seven previously frozen readouts are unchanged; only the **source-free generator seed allowlist** changed.

The original **1,025-witness engineering checkpoint** `amalgam-joint-state.json` SHA256 `576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8` was restored, using pinned native episode source Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e` with the previously documented **minimal source-equivalent dependency shims**. The original full dependency tree has not been qualified.

## Scored development evidence (lower transition Brier is better)

| New scenario/seed | Candidate, changed stage | Strongest same-information control | Candidate minus control | Familiar return Brier drift vs frozen | Return <= +0.01 |
|---|---:|---:|---:|---:|---|
| B-94011 | 0.290251 | 0.205912 (continuing native) | +0.084339 | +0.014557 | **FAIL** |
| B-94023 | 0.275918 | 0.246379 (continuing native) | +0.029539 | +0.025083 | **FAIL** |
| C-95011 | 0.289945 | 0.216641 (trailing-32 Beta) | +0.073305 | +0.000000 | PASS |
| C-95023 | **UNVERIFIED** | **UNVERIFIED** | — | — | **INCOMPLETE** |

All three **completed** seeds failed the new-law improvement gate; both completed B seeds exceeded the +0.01 old-law retention drift bound. Each completed seed had 112 source-free paired public outcomes and three cold checkpoint receipts; **336 completed observations** total. No warmup false activations among completed seeds. These are observed **development negatives**, not a complete four-seed scientific classification.

The fourth seed **C-95023 was marked STARTED** and has **no completed receipt**. The outer execution command timed out at **180 seconds**, despite the child timeout being configured at 35 seconds; no terminal timeout receipt was written. The number of outcomes consumed by this child is **UNKNOWN**, and the timeout root cause remains **UNVERIFIED**. No process was found remaining after the outer timeout. **Do not rerun any started seed** or silently reclassify the incomplete cohort.

## Exact evidence

- `partial-result.json`: authored summary; all three positive loss deltas, two old-task regressions, SHA/source pins, missing-fourth-state and failure classification.
- `partial-sealed-receipts.tar.gz` (SHA256 `c8e8d0091530cc7e0bbaf4141f959058d6e8e62e6d5fd5184ce2c1b948931d09`, Git blob `80a85bb6a5c72f3cebafc306bd359b5bef0aa432`): seven exact write-once source records — three complete receipt JSONs, their three prior STARTED markers, and the fourth seed's STARTED marker. Use `tar -xzf partial-sealed-receipts.tar.gz -C /tmp/wscm-receipts` after creating the destination to examine original per-arm losses, fixture SHA256, checkpoint digest, RSS and elapsed CPU/wall measurements. No protected source or secrets are included.
- Source-free focused tests **10/10 local PASS** (Linux CPython 3.13.5) before first scoring. Exact repository-source parity verified immediately before scoring. No PR CI/workflow result was claimed. Complete final cross-platform regression **UNVERIFIED**.

**ENGINEERING:** local negative contract/source pins PASS; cohort completeness FAIL/INVALID from missing terminal receipt and external timeout; full final regression UNVERIFIED. **SCIENTIFIC:** three negative paired development outcomes, incomplete cohort; actual native cumulative retention/transfer gain UNVERIFIED. **DEPLOYMENT:** UNVERIFIED; research-only draft/unmerged, no native code or owner controller changes.

**Decision:** Stop this W16 historical-loss routing/epoch-selector approach. Do not fine-tune the prior 216 consumed witnesses or these newly consumed seeds. Any further experiment must be a materially different native memory mechanism, independently preregistered with legitimate protected-source custody/authority, fully trained matched controls, cold retention and unfamiliar transfer. This failure is not a claim that native memory is impossible.

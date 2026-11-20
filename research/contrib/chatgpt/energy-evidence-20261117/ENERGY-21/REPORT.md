# ENERGY-21 — Authentic native CKAD21 result reaggregation (no energy intervention)

**Date:** 2026-11-18. **Classification:** retrospective read-only diagnostic of the existing **fully trained and persisted** Yggdrasil CKAD21 native learner; original experimental source/held outcomes unchanged. **NOT a new trained-energy comparison**, new Yggdrasil checkpoint run, new science trial or promoted gain.

## Main result

The earlier ENERGY-20 energy-sidecar synthetic proxy was not an actual Yggdrasil checkpoint comparison. Here the input is the original pinned native CKAD21 scored result and **three original checkpoint binary blobs** linked byte-for-byte from native CKAD21's source commit in the **same Git repository**. The isolated GitHub archive's `audit.py` verifies checkpoint SHA-256, Git blob IDs, complete 18-session reward aggregation, frozen metrics, and source-result identity on a checkout.

| Existing CKAD21 held cohort (3 seeds) | Native context-active reward | Pooled native control reward | Native minus pooled |
|---|---:|---:|---:|
| Session 0, first familiar state | 251/288 | 231/288 | +20/288 (+6.94 pp) |
| Session 3, later return to familiar state | 246/288 | 246/288 | 0/288 (0 pp) |
| Frozen returning aggregate, sessions 0 + 3 | 497/576 (86.28%) | 477/576 (82.81%) | +20/576 (+3.47 pp) |
| Shifted context sessions 1 + 4 | 485/576 (84.20%) | 397/576 (68.92%) | +88/576 (+15.28 pp) |
| Unfamiliar terminal-switch, session 5 | 162/288 (56.25%) | 77/288 (26.74%) | +85/288 (+29.51 pp) |

**Frozen CKAD21 threshold:** Returning advantage must be >=5 percentage points over the pooled native control. The measured 3.47 pp **FAILS**. The session-3 advantage itself is zero. This identifies the **returning-context retention/adaptation gap**, not a planning formula defect.

The new terminal-switch group is **descriptive only**, not a preregistered general-transfer pass: per-seed active/pooled are **42/3**, **35/38**, **85/36** out of 96 respectively, demonstrating substantial heterogeneity, including one negative seed. Raw individual paired returns and uncertainty intervals were not present in the aggregated result; significance and independent transfer cannot be established from reward sums alone.

The CKAD21 source records **14,688 native versus exact-mixture forecast comparisons** and **12,240 decision comparisons**, with **0 recorded mismatches**. The audit validates these reported counters and per-session summary, but does not independently execute the original checkpoint's Python inference code here. Its exact expected-reward policy was already correct in the ENERGY-19 sense.

## Provenance

- Yggdrasil source: draft [PR #1207](https://github.com/spoonman136668-ai/Yggdrasil/pull/1207), pinned native commit `392f6c5d66adfff3b79d6a6a2910b6557dfccbdc`.
- Original result Git blob: `39c9cdeca8a302c2650ec58d80165ec3ee99ec84`; original file `research/contrib/chatgpt/CKAD-21/result.json`.
- Three original native checkpoint SHA-256 and same-repo Git blob IDs: see `source_pins.json`.
- Exact byte-identical source files are linked by existing Git blob IDs into this isolated archive; no re-training, no rematerialization from a text summary.
- ENERGY-20: independent synthetic proxy reported no advantage for its separate energy-factor learner over the strongest conventional control. Nothing here overturns that result.

## Qualifications and next falsifiable work

**ENGINEERING:** Source readback, immutable Git tree pointers, deterministic integer-reward reaggregation PASS at preparation. `audit.py` is provided for cross-platform full source-byte/checkpoint verification. Original native dual-platform CKAD21 qualification is referenced but not rerun here. G29 atlas CI remains a distinct engineering gate; do not classify stale atlas failures as scientific learning failures.

**SCIENCE:** **NO-GO**, consistent with CKAD21's frozen development failure. Do **not** retrofit energy constraints based on these already-consumed held outcomes. Future energy learning tests must prospectively freeze new heldout regimes, calibrate paired accuracy, preserve action consequence and prior retention, and exceed both pooled native and fully fitted conventional controls while keeping the native expected-reward decision rule unchanged. No hidden first-use or original-source actor use.

**DEPLOYMENT:** NONE. No merge, promotion, controller, scheduler, runner or active research loop mutation.

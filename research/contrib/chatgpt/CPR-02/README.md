# CPR-02 — Independent-probe confirmation of conformal alarms (research only)

**Decision: NO SCIENTIFIC ADVANTAGE SHOWN on source-free fixtures. Do not
promote, spawn specialists, or replace Yggdrasil's native memory.**

## Custody and freeze

- Accepted `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- CPR-01 immutable parent: `3ae43b4d79a411bd9f3a1bbca8300af7586ea435`.
- CPR-02 preregistration was committed FIRST at
  `707714324a4818f9c3013f2c16f7a89602f3fc63`.
- Implemented only `monitor.py`, source-free tests and comparison controls.
- Probe SHA and monotonic sequence do **not** certify independence. True
  independence needs separately qualified source-owner evidence.
- No G41 33-expert artifact, real expert, FIT/CAL/HELD cohort, original-world
  action, live learner, protected first-use, dispatcher, or runner was used.

## Source-free results (not accepted science)

Local Linux x86_64 Python 3.13.5 stdlib: 10/10 unit tests passed using
a **local CPR-01 behavioral stand-in**, not byte-exact CPR-01 source.
The committed CPR-02 module and tests matched the local Git blob hashes:
`dc9291064d22d5cba40ee7dde28643604247db9d` (module),
`0412a55aa7aaf355c2f4dc18f2fc8e092eab2d7c` (7 base tests), and
`5ddfd88f45364a482fd276d68d6cd93f092aabf7` (3 matched controls).
GitHub CI and full exact-SHA Linux/Windows regression were not run.

| Synthetic case | CPR-01 raw alarm | CPR-02 confirmed | Same-probe two-streak control |
| --- | --- | --- | --- |
| 64 good + 8 corrupted primary + 8 good, independent probe clean | step 75 | none | none |
| 16 A then 32 genuinely changed, probe changed too | step 27 | step 29 | **step 18** |
| 64 good + 16 jointly contaminated + 8 good | step 75 | false at step 77 | false at step 66 |

All indices are one-based within the whole scenario. For the sustained
shift, CPR-02 confirms on shift-relative step 13, while the matched-info
probe-only comparator confirms on shift-relative step 2: **11-step gap**.
Neither detector is robust to fully correlated probe corruption.

A green test intentionally verifies the correlated-noise counterexample;
it is not a safety or scientific PASS. The matched-information comparator
uses the **same probe labels** and an equivalent two-mismatch threshold.
This screen does not establish equal end-to-end compute or trained control
strength. No old-task Brier, unfamiliar transfer, cold learner retention,
costed action, reproduction or native behavioral gain was measured.

## Disposition

**Engineering:** Source-free monitor and test blobs committed; 10/10 local
simulation with CPR-01 stand-in PASS. Integration against the exact CPR-01
Git blob, interface/negative controls on native Yggdrasil, and mandatory
final dual-platform regression remain UNVERIFIED.

**Science:** CPR-02 shows no incremental utility over a simpler,
matched-information two-probe detector in these frozen synthetic cases.
No retention or generalization gain. Treat this as an exploratory
**negative screen** and discontinue CPR-02 architecture expansion unless
a separately preregistered realistic independent-probe source and stronger
matched controls justify it.

**Deployment:** NONE; no acceptance, merge, promotion or original-world
first-use authority.

For follow-up, prioritize a mechanism that directly improves cumulative
memory/readout retention under equal-information, fully trained
comparators, rather than adding another alarm-confirmation layer.

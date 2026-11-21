# SRL01 — post-result source-free resource qualification (NOT a second science trial)

This is a **post-hoc engineering CPU microprofile**, not a new primary science result, not an approved native experiment, not a pre-registered performance superiority result and not a native end-to-end CPU qualification. Its only inputs are the already consumed, deterministic 72 cohorts' six-public-witness histories (48 stationary +24 no-stable-role); it never observes or reveals new target truths or dispatches model actions. Candidate/trial frozen source commit `7b513cc388406bdd7ba47234ca90a887dc7c6648` and first primary result are not changed.

**Python 3.13.5/Linux x86_64, sequential single-process `time.process_time`, 3 warm-up fits per history, 80 measured repeats ×72 histories=5,760 fits/arm, identical public inputs and caller-side sampling.**

| Resource metric | Current independent per-address empirical Beta | Source-fitted shared 16-state exact-Fraction posterior |
|---|---:|---:|
| Measured 5,760 fit CPU, run A | 0.021785 sec | 2.913352 sec |
| Measured 5,760 fit CPU, run B | 0.023386 sec | 3.004570 sec |
| Per-fit CPU, run B | 0.00406 ms | 0.52163 ms |
| Fit-only ratio | reference | **128.48×** run B (**133.73×** run A) |

This microprofile is useful critical-path evidence, **not proof of the same ratio inside the real native evaluator**: it excludes parent native source-relation queries, provenance checks, action selection, cold restore, end-to-end environment stepping, original training and CPU/platform effects. The exact native <=2× gate remains **UNVERIFIED**. Nonetheless, the large resource delta shows this exact-Fraction DEV prototype is **not ready for promotion**; an optimized integer/fixedpoint/cached implementation would itself require a new frozen capacity/precision equivalence gate and a mandatory full exact-final Windows/Linux regression on the candidate SHA. No post-result parameter tuning of the consumed 72 cohorts is permitted.

**Source:** [`profile_source_free.py`](profile_source_free.py), Git blob `7990604bb16b3b76df241646351a157e7be03824`; [source-free timing receipt](resource-profile.json), Git blob `f9c32f4df2ab3cd141d647109bbb0526e78294c9`. Original frozen positive **+45 synthetic detections over independent Beta at the same two-action evaluation budget**, with independently trained exact Bayes **perfect parity**, is preserved unchanged in [`result-summary.json`](result-summary.json); no scientific advantage over strong controls exists. No original raw stdout was sealed to GitHub; only deterministic code, original SHA and summary are in the repo.

**Classification:** Engineering source-only focused 8/8 tests PASS; six preset **predictive** DEV criteria PASS; performance microprofile **resource concern/NO PROMOTION**; authentic native integration and <=2× resource acceptance **UNVERIFIED**; scientifically qualified new learning **NO**; deployment **NONE**. Preserve the negative no-mapping Brier regression +0.005293 as a separate bounded negative. Continue only under central Amalgam authority and existing issue #426 first-use restrictions.

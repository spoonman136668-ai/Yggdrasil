# FCR03 — retrospective diagnostic-action identifiability correction (read-only)

**Status:** SOURCE-FREE ANALYTIC CORRECTION / ENGINEERING 17/17 focused local PASS / no scientific gain / no deployment. This is not a new candidate, trial, threshold change, source actor or independent learner.

## Pinned original evidence

- Existing FCR03 `DEV_NO_GO` at [`e9ba639b038b4f18f2ada68b8b5576687ae0740c`](https://github.com/spoonman136668-ai/Yggdrasil/commit/e9ba639b038b4f18f2ada68b8b5576687ae0740c), tree `a71c6fbcb9e460c21c1bda977a076062b2cca301`. Frozen code commit before outcome `3bfa0cd51e02c16bc8124cd9d0b2f220377b245a`; parent coordinator PR #1278 still `86264b41a08d49f558418c0fba367f3a2636befa`.
- Original XZ result Git blob `f9ca478fe6ff6d3fd7b694d70ec279c22bebfe34`, exact decompressed JSON SHA256 `a81297f6a0f0bf7c982f7c8656af85be92c432e321b5e49dfbea9b5beee92cee`. This read-only audit independently verifies those source blobs and result before examining existing seed identities; it does **not** rerun `dev_trial.py`.
- Runnable audit `audit_identifiability.py`, negative tests `test_identifiability_audit.py`, source-derived receipt `identifiability-audit.json`. Reproduction on exact branch: `cd research/contrib/chatgpt/CAUSAL-AMALGAM/FCR03 && PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_mechanism_recall.py test_dev_trial.py test_identifiability_audit.py && PYTHONDONTWRITEBYTECODE=1 python audit_identifiability.py`.
- Local sandbox Python 3.13.5 17/17 focused tests PASS (existing FCR03 13 + new 4). Full Linux/Windows regression and authentic owner checkpoint **NOT RUN**.

## Exact analytic argument — FCR03 A/B mechanism only

The frozen laws in `dev_trial.py` are:
```
Transition A: s2 = x1 XOR c
Transition B: s2 = x1
Reward A:     y  = s2 XOR x2
Reward B:     y  = s2 XOR x2 XOR c
```
Here `c` is **public but exogenous**: neither intervention `x1` nor `x2` changes `c`. Enumerating *every allowed binary action and observed s2* proves:

| Context | Transition A and B differing? | Reward A and B differing, given public s2? | Can x1/x2 action choice increase separation? |
|---|---|---|---|
| c=0 | NO (all actions) | NO (all actions) | NO |
| c=1 | YES (all actions) | YES (all actions) | NO |

Under equal prior A/B and deterministic observations, **one** witnessed transition or reward outcome at c=1 reveals **1 bit** about the respective mechanism, regardless of action; at c=0 it gives **0 bits**, regardless of action. Once that mechanism is identified with a c=1 witness, further same-law actions have **zero incremental identification value**. This is a statement about these particular two hypotheses and publicly conditioned stages, **not** about arbitrary hidden confounders, novelty, state-changing interventions or full Yggdrasil.

## Retrospective evidence coverage, no new trial

Existing source-free eight-seed (317101–317108) fixture had c=1 observations:
- Familiar A: **324/640** total, ≥33 in each seed.
- Changed B: **312/640** total, ≥36 in each seed.
- Returning A: **338/640** total, ≥36 in each seed.
- Recombined C: **310/640** total, ≥30 in each seed.
- Nonlinear D: **183/384** total, ≥17 in each seed; its reward rule is **outside this A/B proof**.

All c=1 observation counts are derived from exact SHA256 fixture inputs and source code and do not consume new evaluation seeds or model updates. Original C reward Brier **0.077734375** vs strongest matched hazard-Bayes **0.0309703378**, delta **+0.046764037175**; returning A transition Brier **0.0572265625** vs best **0.0223950315**, delta **+0.034831530953**, above the +0.020 guard.

## Corrected diagnosis and impact

**Correct earlier speculative claim** that FCR03 failed because the policy lacked distinguishing diagnostic interventions. On this frozen A/B family, *all* admissible actions at c=1 are equally identifying and none at c=0 are identifying. There was plenty of informative context in every phase. Changing x1/x2 intervention selection, while holding the observed context and budget equal, cannot fix the failure of FCR03's existing alarm/recall heuristic. The archived reward recall count 2/8 and returning-transition drift remain negatives; the most direct supported investigation is **mechanism-change recognition and staged retention selection**, compared with fully trained conventional fixed-share Bayes/changepoint controls, not a rerun of the same action policy.

Prior [CKAD36 PR #1253](https://github.com/spoonman136668-ai/Yggdrasil/pull/1253) already tested active versus fixed matched-action intervention choice, where fixed tied in-family and the development decision was NO-GO. Do not spend source or CPU on that duplicate. A new intervention experiment would require **a different structurally identified problem** where actions have provably different information or long-horizon consequences, a separate preregistration, disjoint inputs, matched actions/cost/compute, strongest controls, owner source permission, and mandatory exact-head regression. No FCR04 branch or new protected trial was created here.

**ENGINEERING**: local audited evidence and 17/17 tests PASS; source-blob equality PASS; Windows/Linux full final UNVERIFIED. **SCIENTIFIC**: no new scientific evidence, original FCR03 DEV_NO_GO remains. **DEPLOYMENT**: none; accepted main, coordinator PR #1278, retention #1329, checkpoint custody #1322 unchanged.

# P0 Quine — complete old-prefix single-witness retention guard

**Status:** isolated additive engineering repair; no new source, trained checkpoint, protected seed, controller, scheduler, acceptance or deployment. Based on previously source-qualified P0 Quine candidate `d0f1b0a382f16ee119c464a434f79f18e2603cc9` with original frozen Amalgam transfer study untouched.

## Reproduced decision defect

The original Quine veto correctly checked 5–10 selected witnesses individually and every mastered-regime / entire old-prefix **mean** Brier. However, an unselected old example could undergo severe forgetting while a long regime's mean remained below the fixed +0.02 gate.

The new source-free test constructs 96 already-witnessed synthetic rows with two 48-row mastered windows. One unselected row's transition prediction changes from `0.25` to `0.90` for true class `0`, worsening Brier from `0.0625` to `0.81` (individual drift `+0.7475`). Yet its 48-row regime mean only worsens by `+0.0155729` and the 96-row old-prefix mean by `+0.0077865`; all selected Quines are unchanged. **The original code would admit this destructive update.** This is a constructed engineering counterexample, not evidence from reserved scientific cohorts.

## Narrow implementation

The existing full old-prefix evaluation was already computing anchor and proposed prediction losses for every witnessed original record. Reuse those same predictions to track the greatest per-witness per-stage increase and fail the shared overwrite if it exceeds the **same frozen +0.02 threshold**. Keep the original Quine tests, all regime-mean and complete-prefix-mean checks, exact one-witness append and checkpoint/prefix tamper checks. No extra forward passes are required beyond the preexisting full-prefix evaluation. Record only worst old index/stage and numerical drift in the diagnostic result. On veto preserve the **currently admitted** state; never revert to original anchor or spawn a rival specialist. Previously admitted beneficial updates remain cumulative.

The new rule is intentionally conservative: a single noisy old example can veto useful adaptation. A scientific decision requires preregistered retention/novel-transfer trade-offs, matched strong controls, provenance-certified mastered regimes and fresh authorized sources. This branch does not run those trials, mutate the accepted native model, or claim scientific PASS.

**Qualification:** focused negative + original Quine tests, full original-source dual-OS regression, and G29 atlas reanchor required on exact candidate SHA. Existing historical tests and original 1,025/1,145 witness work are reused, not re-scored as fresh science.
